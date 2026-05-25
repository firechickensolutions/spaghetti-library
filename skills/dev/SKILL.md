# Dev Skill

## Diagnostic

AI agents generate code that passes syntax checks but introduces rework: premature abstraction, defensive accumulation, untestable coupling, and patterns that look correct in isolation but break under the system's constraints. This skill routes agents to sourced patterns at the moment of generation — before the failure mode lands.

## When to load

Load at the start of any code-writing task. Check the trigger table before writing code, not after.

## Workflow

1. Before writing code, scan the trigger table for conditions that match the current task.
2. When a trigger fires, halt. Read the corresponding library entry in full.
3. Apply the sourced pattern. Resume generation.
4. At session close, read the full section for every language touched and flag deviations.

## Trigger table

| Trigger condition | Library entry |
|---|---|
| About to write a SQLite `CREATE TABLE` for data with historical, audit, correction, or effective-date semantics | `library/dev/01-sql-bitemporal-strict.md` |
| About to seed lookup rows, migration data, or default records using `INSERT OR REPLACE`, `INSERT OR IGNORE`, or `ON CONFLICT` | `library/dev/02-sql-idempotent-migrations.md` |
| About to write `from abc import ABC`, `@abstractmethod`, or an interface/base class with only one known implementation | `library/dev/03-python-structural-protocols.md` |
| Writing a boolean type predicate over a closed union where both the `if` and `else` branches need narrowing | `library/dev/04-python-typeis-narrowing.md` |
| About to acquire a file, lock, transaction, temp directory, environment mutation, or external resource that must be released | `library/dev/05-python-resource-boundaries.md` |
| About to build and return a list from a loop over a file, API stream, database cursor, log, or large iterable | `library/dev/06-python-lazy-generators.md` |
| Receiving a plain `dict` with fixed keys between functions, or converting structured data into a class without checking boundary vs domain | `library/dev/07-python-typeddict-dataclass.md` |
| Defining or modifying a function with four or more positional parameters | `library/dev/08-python-signature-relief.md` |
| Writing a script that can be rerun and mutates files, APIs, databases, queues, seed data, or external state | `library/dev/09-python-idempotency-guards.md` |
| Defining TypeScript state, action, API, or task objects using a string `status` field plus optional payload fields | `library/dev/10-ts-exhaustive-unions.md` |
| Defining React component state with optional `loading`, `data`, `error`, `empty`, or `status` fields that can form impossible combinations | `library/dev/11-ts-react-union-state.md` |
| About to call a React hook inside a condition, loop, nested function, event handler, `try`/`catch`/`finally`, after an early return, or with an incomplete dependency array | `library/dev/12-react-hook-ordering.md` |
| Lifting React state to a parent, context, store, or global module before confirming two or more independent consumers need it | `library/dev/13-react-state-colocation.md` |
| Writing a PowerShell hook that changes `$ErrorActionPreference`, changes directories, calls native executables, or checks command success with `$?` | `library/dev/14-powershell-scoped-hooks.md` |
| Adding `None`, key-existence, `isinstance`, schema, or transport-shape checks inside business logic that already receives a parsed domain object | `library/dev/15-cross-parse-boundary.md` |
| Writing a function with many live booleans, nested branches, mutable side effects, optional values, or intermediate variables that cannot be named as a small coherent set | `library/dev/16-cross-cognitive-chunking.md` |

## Library growth

When a rework event reveals a repeatable pattern:

1. Create a new numbered entry in `library/dev/` using the 6-field format
2. Add a row to the trigger table above and to `library/dev/README.md`
3. Cite the source — PEP, official docs, named practitioner text with author and section

Entries earn a slot by preventing rework, not by anticipation.

## Verification

- Trigger fires on specific syntactic or semantic signals, not vague categories
- Every entry has a canonical source with author and section
- Before/after code demonstrates the failure and the fix without additional context
- A reviewer can read one entry and apply the pattern without reading the others
