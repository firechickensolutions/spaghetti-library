# Bi-temporal STRICT Schema

**Language(s):** SQL / SQLite

**Rework-prevention rationale:** Prevents complexity underestimation and defensive accumulation by pushing historical state, type enforcement, timestamp format, and temporal ordering into the database boundary instead of scattering those checks across application code.

**Canonical source:** SQLite Consortium, *SQLite Documentation*, "STRICT Tables" (sqlite.org/stricttables.html); Richard T. Snodgrass, *Developing Time-Oriented Database Applications in SQL*, chapters on valid time and transaction time.

## Trigger condition

Halt and read this entry when about to write a SQLite `CREATE TABLE` or migration for data that has historical, audit, correction, or effective-date semantics.

## Before

```sql
CREATE TABLE runner_config (
  config_id INTEGER,
  runner_name TEXT,
  concurrency_limit INTEGER,
  updated_at TEXT
);
```

## After

```sql
CREATE TABLE runner_config (
  config_id     INTEGER NOT NULL,
  runner_name   TEXT    NOT NULL,
  concurrency_limit INTEGER NOT NULL,
  valid_from    TEXT    NOT NULL
    CHECK (
      valid_from GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
      AND date(valid_from) IS NOT NULL
      AND date(valid_from) = valid_from
    ),
  valid_to      TEXT    NOT NULL
    CHECK (
      valid_to = '9999-12-31'
      OR (
        valid_to GLOB '[0-9][0-9][0-9][0-9]-[0-9][0-9]-[0-9][0-9]'
        AND date(valid_to) IS NOT NULL
        AND date(valid_to) = valid_to
      )
    ),
  tx_start      TEXT    NOT NULL DEFAULT CURRENT_TIMESTAMP,
  tx_end        TEXT    NOT NULL DEFAULT '9999-12-31 23:59:59',
  PRIMARY KEY (config_id, valid_from, tx_start),
  CHECK (valid_from <= valid_to),
  CHECK (tx_start <= tx_end)
) STRICT;

PRAGMA journal_mode = WAL;
PRAGMA foreign_keys = ON;
```

**Note on CHECK + NULL:** SQLite CHECK constraints pass when the expression evaluates to NULL (three-valued logic). The `date(x) IS NOT NULL` guard forces invalid date strings to fail rather than silently pass. Do not rely on short-circuit evaluation alone.

**Updating a record:** close the current row's `tx_end`, insert a new row with the corrected `valid_from`/`valid_to` and a fresh `tx_start`. Never UPDATE a bi-temporal row in place.
