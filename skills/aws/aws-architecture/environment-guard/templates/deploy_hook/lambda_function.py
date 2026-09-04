"""CloudFormation hook that reports when a deploy moves a service between environments.

The runtime guard watches the running code and catches a wrong target the moment a
record is written to it. It cannot see a flip that ships to a function which then sits
idle, because there is nothing to count. This runs on the deploy instead, before
anything is provisioned, and needs no traffic at all.

It is a nudge, not a gate. Registered with FailureMode WARN, a finding is reported and
the deploy continues regardless.

The thing this must never become is a monitor whose breakage looks like its silence —
the very failure it exists to catch. So every problem it can detect in itself is
reported as a finding rather than swallowed: a publish that fails, a template it
cannot read, an event it cannot parse, and a pattern that has stopped matching
anything at all. Under WARN none of that can block a deploy; it only makes the
breakage visible in the stack events, where somebody is already looking.
"""

import difflib
import json
import logging
import os
import re
import urllib.request
from typing import Any

import boto3
from botocore.config import Config

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# Botocore defaults to a 60-second connect and read timeout with four attempts, which
# on a slow call would blow the whole invocation budget and get the function killed
# mid-publish. CloudFormation then retries the hook, and the retry is what sends a
# duplicate notification. Keep the client's worst case well inside the budget.
sns_client = boto3.client(
    "sns",
    config=Config(connect_timeout=3, read_timeout=5, retries={"max_attempts": 2}),
)

# Read at import so a missing variable fails the invocation loudly. An init failure
# counts as a Lambda error, so the function's error alarm reports it — which is not
# true of an exception caught inside the handler.
ALERT_TOPIC_ARN = os.environ["ALERT_TOPIC_ARN"]

# Both halves of the pair, wherever they appear. TARGET_ENV is what the function runs
# with; ExpectedTarget is what its guard alarm watches for. A safe deliberate flip
# moves them together, and this reports that too — one nudge per cutover is the point,
# so somebody confirms the commit was reviewed.
#
# Matched by text rather than by parsing, because the payload can arrive as YAML or as
# JSON and the value can be inline or inside a Fn::ToJsonString map. Both spellings are
# covered: `TARGET_ENV: staging` and `"TARGET_ENV": "staging"`.
#
# It will also match those words inside a comment or a description that happens to put
# a colon before the value. That costs a spurious nudge, never a missed one, and a
# false nudge is the cheap direction to err in.
TARGET_PATTERN = re.compile(
    r'"?(TARGET_ENV|ExpectedTarget)"?\s*:\s*"?(staging|production)\b'
)

# CloudFormation truncates a hook message at 4096 characters.
MAX_HOOK_MESSAGE = 4000


def targets(template: str) -> list[str]:
    """Every environment-target assignment in a template, in the order it appears.

    Document order is kept on purpose. Comparing sorted values, or counts of them,
    would hide the case this exists to catch: two functions swapping environments in
    one deploy leaves the totals identical, so a count-based check stays silent while
    both are now writing to the wrong place.

    The cost is that genuinely reordering the template — moving a resource block
    without changing any value — reads as a change and sends one nudge. That is the
    cheap direction to err: a spurious nudge asks somebody to glance at a commit that
    did move things around, where the alternative is missing a real swap entirely.
    """
    return [f"{key}={value}" for key, value in TARGET_PATTERN.findall(template)]


def describe_change(*, previous: list[str], proposed: list[str]) -> str | None:
    """Summarise how two sequences of environment targets differ.

    Returns:
        One line per assignment that moved, or None when nothing moved.
    """
    if previous == proposed:
        return None

    if len(previous) == len(proposed):
        # Same number of assignments, so position still identifies each one and a
        # pairwise walk names every value that moved — including both halves of a swap.
        return "\n".join(
            f"#{position}  {before} -> {after}"
            for position, (before, after) in enumerate(zip(previous, proposed), start=1)
            if before != after
        )

    # A guarded resource was added or removed, so positions no longer line up. Fall
    # back to a diff, which resyncs around the insertion instead of reporting every
    # entry after it as changed.
    return "\n".join(
        difflib.unified_diff(
            previous, proposed, fromfile="deployed", tofile="proposed", lineterm="", n=0
        )
    )


def _fetch_payload(url: str) -> dict[str, str]:
    """Download the stack payload CloudFormation staged in S3.

    Stack-target hooks receive a presigned URL rather than the templates inline,
    because a template can exceed what a Lambda invocation may carry. Presigned means
    the URL carries its own authorisation, so this needs no s3:GetObject permission.
    """
    # S310 guards against user-supplied URLs. This one comes from CloudFormation in the
    # invocation request, not from anything a caller controls.
    with urllib.request.urlopen(url, timeout=10) as response:  # noqa: S310
        return json.loads(response.read())


def _proceed(token: str, message: str) -> dict[str, Any]:
    """Report nothing. Used only when the hook genuinely has nothing to say."""
    return {
        "hookStatus": "SUCCESS",
        "message": message[:MAX_HOOK_MESSAGE],
        "clientRequestToken": token,
    }


def _warn(token: str, message: str) -> dict[str, Any]:
    """Report a finding. Under FailureMode WARN the deploy still proceeds."""
    return {
        "hookStatus": "FAILED",
        "errorCode": "NonCompliant",
        "message": message[:MAX_HOOK_MESSAGE],
        "clientRequestToken": token,
    }


def lambda_handler(event: dict[str, Any], context: Any) -> dict[str, Any]:
    """Compare the deployed and proposed templates and report a target change."""
    token = ""
    try:
        # The docs' schema block and its own worked example disagree on the casing of
        # this field. Accept either rather than return an empty required field.
        token = event.get("clientRequestToken") or event.get("clientRequesttoken") or ""

        invocation_point = event.get("actionInvocationPoint", "")
        if invocation_point != "UPDATE_PRE_PROVISION":
            # A create has nothing to compare against, and a delete carries no template
            # at all. Only an update can move a function between environments.
            return _proceed(token, f"Nothing to compare on {invocation_point}.")

        # CloudFormation retries a hook up to three times. The publish below may
        # already have succeeded before the response was lost, so only ever notify on
        # the first attempt; a retry still reports the finding to the stack events.
        attempt = event.get("requestContext", {}).get("invocation", 1)

        payload_url = event.get("requestData", {}).get("payload")
        if not payload_url:
            return _warn(token, "Hook received no template payload; nothing checked.")

        payload = _fetch_payload(payload_url)
        previous = targets(payload.get("previousTemplate", ""))
        proposed = targets(payload.get("template", ""))

        if not previous and not proposed:
            # Neither template mentions a target. Either the pattern no longer matches
            # how the values are written, or they moved behind a !Ref. Both mean this
            # hook is blind, and blind must never look like all-clear.
            return _warn(
                token,
                "Target pattern matched nothing in either template. The hook is blind "
                "— check TARGET_PATTERN against the template.",
            )

        change = describe_change(previous=previous, proposed=proposed)
        if change is None:
            return _proceed(token, "Environment targets unchanged.")

        logger.info("Target change detected on attempt %s: %s", attempt, change)
        if attempt == 1:
            sns_client.publish(
                TopicArn=ALERT_TOPIC_ARN,
                Subject="Environment target changed by a deploy",
                Message=(
                    "A deploy is changing which environment a function talks to.\n\n"
                    f"{change}\n\n"
                    f"Stack: {event.get('stackId', 'unknown')}\n\n"
                    "If this was deliberate, nothing to do — the guard alarm for the "
                    "function you moved may also fire once during the cutover and "
                    "clear itself. If nobody intended it, revert the commit and "
                    "redeploy: this hook only warns, so the deploy it is reporting has "
                    "already gone ahead."
                ),
            )
        return _warn(token, f"Environment target changed:\n{change}")

    except Exception:
        # Never block a deploy. But never go quiet either: a swallowed exception
        # records no Lambda error, so the function's error alarm would not fire and the
        # failure would reach nobody. Reporting it as a finding puts it in the stack
        # events instead, which is the only channel left.
        logger.exception("Environment target hook failed")
        return _warn(token, "Environment target hook failed internally — check logs.")
