# Dev Library -- Routing Index

Agent-consumable pattern corpus. Each entry is self-contained: read one entry, apply the pattern, resume. The `/dev` skill at `skills/dev/SKILL.md` carries the full trigger routing protocol.

## Trigger table

| Trigger condition | Entry |
|---|---|
| About to write a SQLite `CREATE TABLE` for data with historical, audit, correction, or effective-date semantics | [01-sql-bitemporal-strict.md](01-sql-bitemporal-strict.md) |
| About to seed lookup rows, migration data, or default records using `INSERT OR REPLACE`, `INSERT OR IGNORE`, or `ON CONFLICT` | [02-sql-idempotent-migrations.md](02-sql-idempotent-migrations.md) |
| About to write `from abc import ABC`, `@abstractmethod`, or an interface/base class with only one known implementation | [03-python-structural-protocols.md](03-python-structural-protocols.md) |
| Writing a boolean type predicate over a closed union where both the `if` and `else` branches need narrowing | [04-python-typeis-narrowing.md](04-python-typeis-narrowing.md) |
| About to acquire a file, lock, transaction, temp directory, environment mutation, or external resource that must be released | [05-python-resource-boundaries.md](05-python-resource-boundaries.md) |
| About to build and return a list from a loop over a file, API stream, database cursor, log, or large iterable | [06-python-lazy-generators.md](06-python-lazy-generators.md) |
| Receiving a plain `dict` with fixed keys between functions, or converting structured data into a class without checking boundary vs domain | [07-python-typeddict-dataclass.md](07-python-typeddict-dataclass.md) |
| Defining or modifying a function with four or more positional parameters | [08-python-signature-relief.md](08-python-signature-relief.md) |
| Writing a script that can be rerun and mutates files, APIs, databases, queues, seed data, or external state | [09-python-idempotency-guards.md](09-python-idempotency-guards.md) |
| Defining TypeScript state, action, API, or task objects using a string `status` field plus optional payload fields | [10-ts-exhaustive-unions.md](10-ts-exhaustive-unions.md) |
| Defining React component state with optional `loading`, `data`, `error`, `empty`, or `status` fields that can form impossible combinations | [11-ts-react-union-state.md](11-ts-react-union-state.md) |
| About to call a React hook inside a condition, loop, nested function, event handler, `try`/`catch`/`finally`, after an early return, or with an incomplete dependency array | [12-react-hook-ordering.md](12-react-hook-ordering.md) |
| Lifting React state to a parent, context, store, or global module before confirming two or more independent consumers need it | [13-react-state-colocation.md](13-react-state-colocation.md) |
| Writing a PowerShell hook that changes `$ErrorActionPreference`, changes directories, calls native executables, or checks command success with `$?` | [14-powershell-scoped-hooks.md](14-powershell-scoped-hooks.md) |
| Adding `None`, key-existence, `isinstance`, schema, or transport-shape checks inside business logic that already receives a parsed domain object | [15-cross-parse-boundary.md](15-cross-parse-boundary.md) |
| Writing a function with many live booleans, nested branches, mutable side effects, optional values, or intermediate variables that cannot be named as a small coherent set | [16-cross-cognitive-chunking.md](16-cross-cognitive-chunking.md) |

## Entry format

Every entry carries six fields: pattern name, language(s), rework-prevention rationale (one sentence, names the AI failure mode), canonical source (author + title + section), before/after code, trigger condition.

## Growth protocol

New entries are added when a resolved rework event reveals a repeatable pattern. Add a numbered file, add a row here and in `skills/dev/SKILL.md`. A pattern earns an entry after it prevented rework, not before.

## Research basis

Entries 01-16 come from a three-pass research thread: Gemini breadth pass, ChatGPT adversarial audit, ChatGPT third-pass. Auth and Permissions entries (17-19) pending a separate ChatGPT-only three-pass thread.
