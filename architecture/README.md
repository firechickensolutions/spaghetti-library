# Architecture Overview

## The problem this solves

AI-assisted code generation fails in predictable ways. The failures are not random; they cluster around six failure modes:

1. **Premature abstraction:** the agent creates hierarchies and interfaces before a second use case exists
2. **Defensive accumulation:** nested error handling, redundant null checks, validation repeated at every layer
3. **Interface with one implementation:** abstract base classes with a single concrete class beneath them
4. **Complexity underestimation:** the agent solves the stated requirement but misses the system constraint (idempotency, resource lifetime, token expiry)
5. **Untestable coupling:** global state, hardcoded paths, and side effects embedded in domain logic
6. **Imaginary extensibility:** plugin systems and config hierarchies for integrations that do not exist

The library addresses these at generation time, not at review time.

## System shape

```
┌─────────────────────────────────────────────────────┐
│  Skill layer                                         │
│  skills/dev/SKILL.md                                 │
│  Loads at session start. Checks trigger table.       │
│  Routes agent to the relevant library entry.         │
└──────────────────────┬──────────────────────────────┘
                       │ trigger fires → halt and read
┌──────────────────────▼──────────────────────────────┐
│  Library layer                                       │
│  library/dev/  (one file per pattern)                │
│  Self-contained entries. Read one, apply one.        │
│  Grows from resolved rework events.                  │
└─────────────────────────────────────────────────────┘
```

## How the skill works

The `/dev` skill sits at the generation layer. At the start of any code-writing task:

1. The agent scans the trigger table for conditions that match the current task
2. When a trigger fires (e.g., "about to write `from abc import ABC`"), the agent halts
3. The agent reads the corresponding library entry in full
4. The agent applies the sourced pattern and resumes

At session close, a reviewer pass reads the full section for every language touched and flags any entry whose pattern was deviated from.

## Trigger design

Triggers are agent-recognizable syntactic or semantic signals, not vague categories. Examples:

| Too vague (don't do this) | Specific (correct) |
|---|---|
| "Writing Python" | "About to write `from abc import ABC` or `@abstractmethod`" |
| "Database work" | "About to write a SQLite `CREATE TABLE` for data with historical or audit semantics" |
| "React component" | "Defining React state with optional `loading`, `data`, `error` fields that can combine impossibly" |

The trigger fires before the code is written. A trigger that fires at review time is a warning, not a prevention.

## Library growth protocol

Entries earn a slot by preventing rework, not by anticipation. The process:

1. A rework event occurs: generated code had to be rewritten
2. The fix reveals a repeatable pattern with a verifiable source
3. A new entry is created: 6 fields, sourced, before/after code, trigger condition
4. A row is added to the trigger table in `library/dev/README.md` and `skills/dev/SKILL.md`

Three questions gate a new entry:
- Does it have a verifiable source (PEP, official docs, named practitioner text)?
- Does the trigger condition fire on a specific, recognizable agent behavior?
- Does the before/after demonstrate the failure mode and the fix without additional context?

## What the library does not replace

- **Linting and static analysis:** enforce formatting, catch syntax errors, flag obvious bugs. The library explains why, linters enforce what.
- **Code review:** the library prevents a class of errors; human reviewers catch the rest.
- **Testing:** patterns make code testable; tests verify it works.
- **Architecture decisions:** the library covers code-generation patterns, not system design choices.

## Current coverage

16 entries across five domains. Auth and permissions in progress (3 entries).

| Domain | Entries | Key failure modes covered |
|---|---|---|
| SQL / SQLite | 2 | Complexity underestimation, data-corruption drift |
| Python | 7 | Interface-with-one-implementation, defensive accumulation, untestable coupling |
| TypeScript / React | 4 | Defensive accumulation, premature abstraction, hook-order drift |
| PowerShell | 1 | Untestable coupling |
| Cross-language | 2 | Defensive accumulation, complexity underestimation |
| Auth (in progress) | 3 | Credential scope leak, permission gate misplacement, token lifecycle blindness |
