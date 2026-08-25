# RDS — Best Practices

## What an endpoint actually is

An RDS endpoint is one database server, the managed equivalent of installing PostgreSQL or MySQL on a box you own. Databases live *inside* it, and one server holds many — the same `CREATE DATABASE` you'd run on a self-managed host.

That equivalence is what tempts teams into the mistake below: since one host can hold `app_prod` and `app_staging` side by side, it looks like environment isolation comes free. It does not. On a self-managed box, isolation was yours to configure. On RDS, the instance is the unit AWS operates on — the unit it patches, reboots, snapshots, restores, and upgrades — so the isolation boundary is the instance, not the database inside it.

---

## Rule 1: One DB instance (or Aurora cluster) per environment

Production gets a host to itself. No other environment shares it.

**Why it bites you:**

| Coupling | What goes wrong |
|---|---|
| **Noisy neighbour** | vCPU, RAM, IOPS, and connection slots are instance-wide. A staging load test, a runaway seed script, or a migration that takes an `ACCESS EXCLUSIVE` lock starves production. Connection exhaustion is the usual first casualty — the limit is per instance, and staging can consume all of it. |
| **Maintenance window** | Patching, reboots, failover, and major-version upgrades act on the instance. Every database on it goes down together, so staging's maintenance schedule becomes production's downtime. |
| **Restore granularity** | Snapshots and point-in-time restore produce a **new instance**, never a single database. Recovering staging clones production's data with it; recovering production means restoring the whole instance and then dumping one database out of it, under incident pressure. |
| **Instance-wide config** | Parameter groups, installed extensions, engine version, and storage settings apply to every database on the host. Testing a parameter change in staging means changing it in production. |
| **Blast radius** | The low-trust environment sits on the same host, same security group, and same network path as production. One over-granted role, one leaked master credential, one `\c app_prod` — and the separation you assumed was never there. |

Separate hosts remove all five couplings at once. Nothing at the database or role level substitutes for that, because the failures above are properties of the instance.

---

## Rule 2: Staging matches production's engine and version, not its size

Staging exists to make production's failures happen somewhere cheap first. That only holds while the engine underneath behaves the same way — call it **fidelity**, and spend on it selectively:

| Must match | May differ |
|---|---|
| Engine **flavour** (Aurora PostgreSQL is not RDS for PostgreSQL) | Instance class / ACU range |
| Engine **major version** | Multi-AZ vs single-AZ |
| Parameter group settings that change semantics (`timezone`, collation, isolation level, `search_path`) | Backup retention |
| Installed extensions | Storage size and type |
| Schema, migration history, and role model | Data volume (use a scrubbed subset) |

Aurora and the community engine are the trap worth naming: same SQL dialect, different storage layer, different failover semantics, different extension availability, and different planner behaviour under load. A query plan validated on Aurora tells you little about RDS for PostgreSQL, and vice versa. Treat a flavour mismatch between staging and production as no staging at all.

---

## Rule 3: Non-production environments may share a host

The rule is about production, not about spending. Dev, preview branches, CI, and ephemeral test environments can share one small instance — give each its own database and its own role, and let them contend.

They qualify because they are mutually low-trust and individually disposable: a noisy neighbour costs a rerun, and a bad restore costs nothing. Staging is the judgement call. Share it with dev when it is a scratch environment; keep it alone when it is a release gate that must stay stable and mirror production.

---

## Rule 4: Answer the cost objection with a smaller host, not a shared one

"Another instance doubles the bill" assumes the second instance is sized like the first. Size staging for correctness, not for load:

- Smallest workable instance class (Graviton `t4g` burstable classes are the usual floor).
- Single-AZ. Failover behaviour is a production concern.
- Minimum backup retention, or none where the data is reproducible from a seed script.
- `gp3` storage at the smallest allocation the schema needs.
- **Stop the instance when idle.** RDS supports stopping an instance or Aurora cluster for a bounded window before it auto-starts; a scheduled stop overnight and at weekends removes most of the compute charge. Check the current maximum stop duration in the RDS docs before relying on it.
- For Aurora, Serverless v2 with a low minimum capacity floor lets an idle staging cluster cost close to nothing between test runs.

A staging host built this way is a rounding error next to production, and it buys back every coupling in Rule 1.

---

## Decision tree

```
Is this production?
├── Yes → its own instance / cluster. Nothing else on it.
└── No → Is it a release gate that must mirror production?
          ├── Yes (staging) → its own instance, matching engine flavour + major
          │                   version, sized down and stopped when idle
          └── No (dev, preview, CI) → share one small instance;
                                      one database + one role per environment
```
