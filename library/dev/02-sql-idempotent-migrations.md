# Idempotent SQLite Migrations

**Language(s):** SQL / SQLite

**Rework-prevention rationale:** Prevents complexity underestimation and data-corruption drift by stopping the agent from using destructive `INSERT OR REPLACE` semantics where a safe idempotent insert or explicit update is required.

**Canonical source:** SQLite Consortium, *SQLite Documentation*, "The ON CONFLICT Clause" (sqlite.org/lang_conflict.html); SQLite Consortium, *SQLite Documentation*, "Foreign Key Support" (sqlite.org/foreignkeys.html).

## Trigger condition

Halt and read this entry when about to seed lookup rows, rerunnable migration data, or default records using `INSERT OR REPLACE`, `INSERT OR IGNORE`, or `ON CONFLICT`.

## Before

```sql
-- REPLACE silently deletes the existing row first, triggering ON DELETE CASCADE
-- on any child tables: data loss on rerun
INSERT OR REPLACE INTO status_lookup (code, label)
VALUES ('READY', 'Ready');
```

## After

```sql
-- DO NOTHING skips the insert without touching the existing row or its children
INSERT INTO status_lookup (code, label)
VALUES ('READY', 'Ready')
ON CONFLICT(code) DO NOTHING;

-- When an update IS intended, use DO UPDATE with a guard so unchanged rows are not touched
INSERT INTO status_lookup (code, label)
VALUES ('READY', 'Ready for dispatch')
ON CONFLICT(code) DO UPDATE
  SET label = excluded.label
  WHERE status_lookup.label IS DISTINCT FROM excluded.label;
```

**INSERT OR REPLACE vs INSERT OR IGNORE vs ON CONFLICT:**
- `INSERT OR REPLACE` = delete conflicting row + insert new one. Triggers FK cascades. Almost never correct for seed data.
- `INSERT OR IGNORE` = skip on conflict. Equivalent to `ON CONFLICT DO NOTHING` but less explicit.
- `ON CONFLICT DO NOTHING` = preferred: intent is visible, no cascades.
- `ON CONFLICT DO UPDATE` = UPSERT. Use when you want to converge to a new value without losing the row.

**Migration versioning:** `CREATE TABLE IF NOT EXISTS` covers first-install tables. For schema evolution across deploys, maintain a `PRAGMA user_version` increment or a migration version table. SQLite does not support `ALTER TABLE ADD COLUMN IF NOT EXISTS`.
