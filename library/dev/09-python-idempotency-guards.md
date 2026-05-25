# Automation Idempotency Guards

**Language(s):** Python / SQL

**Rework-prevention rationale:** Prevents complexity underestimation by making reruns safe instead of letting the agent generate append-only scripts, duplicate API creates, repeated seed inserts, or retry-corrupting mutations.

**Canonical source:** Gregor Hohpe and Bobby Woolf, *Enterprise Integration Patterns*, "Idempotent Receiver" (enterpriseintegrationpatterns.com); Jeff Geerling, *Ansible for DevOps*, sections on idempotent task design and changed-state convergence.

## Trigger condition

Halt and read this entry when writing any script that can be rerun and mutates files, APIs, databases, queues, seed data, or external state.

## The failure mode

An AI agent generates append-only writes and unconditional API creates. On first run: correct. On any retry or re-run: duplicate records, doubled entries, or corrupted state. The agent does not recognize "this script will be run again" as a constraint.

## Before

```python
def provision(path: Path, payload: str) -> None:
    with path.open("a") as f:           # appends on every run
        f.write(payload + "\n")
    api.create_runner(payload)          # creates a duplicate runner on retry
```

## After: compare-before-write (filesystem / API)

```python
def provision(path: Path, payload: str) -> None:
    if path.exists() and path.read_text(encoding="utf-8").strip() == payload.strip():
        return                          # desired state already present, no-op
    path.write_text(payload, encoding="utf-8")
    api.create_or_update_runner(payload)   # API must support upsert semantics
```

## After: uniqueness guard (database)

```python
def seed_runner(db: sqlite3.Connection, run_id: str, name: str) -> None:
    db.execute(
        "INSERT INTO runners (id, name) VALUES (?, ?) ON CONFLICT(id) DO NOTHING",
        (run_id, name),
    )
```

**Two canonical patterns:**

1. **Compare-before-write / desired-state check:** read existing state, write only if the desired state differs. Works for files, config, and APIs with GET+PUT semantics.
2. **Uniqueness guard:** database `ON CONFLICT DO NOTHING` or `ON CONFLICT DO UPDATE ... WHERE IS DISTINCT FROM` for seed and migration data. See entry `02-sql-idempotent-migrations.md` for SQL-specific detail.

**Sentinel files** (marker files that record "this stage completed") are a third pattern for multi-stage scripts where the stage has no queryable state: write a `.done` file at the end, check for it at the start.
