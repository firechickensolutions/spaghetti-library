# Spaghetti Library

A sourced pattern library for AI-assisted code generation. Each entry is a failure mode AI agents introduce, the sourced fix, and the specific trigger condition that tells an agent to halt and read before continuing.

This is not a style guide. It is a corpus built to reduce rework. Code that comes out less wrong on the first pass.

## Why this exists

Vibe coding removed the access moat. It did not change what a shipped product needs to survive production. Every team using AI-assisted generation is re-researching the same patterns, re-learning the same failure modes, and cleaning up the same classes of generated code. This library is the shared ground.

The patterns here are sourced from PEPs, official language documentation, named practitioner texts, and peer-reviewed research. Every entry stands alone. Read it, apply it, move on.

## System Scaffold

```
spaghetti-library/
├── README.md
├── architecture/
│   └── README.md               System architecture, failure modes, growth protocol
├── library/
│   └── dev/
│       ├── README.md           Trigger routing table
│       ├── 01-sql-bitemporal-strict.md
│       ├── 02-sql-idempotent-migrations.md
│       ├── 03-python-structural-protocols.md
│       ├── 04-python-typeis-narrowing.md
│       ├── 05-python-resource-boundaries.md
│       ├── 06-python-lazy-generators.md
│       ├── 07-python-typeddict-dataclass.md
│       ├── 08-python-signature-relief.md
│       ├── 09-python-idempotency-guards.md
│       ├── 10-ts-exhaustive-unions.md
│       ├── 11-ts-react-union-state.md
│       ├── 12-react-hook-ordering.md
│       ├── 13-react-state-colocation.md
│       ├── 14-powershell-scoped-hooks.md
│       ├── 15-cross-parse-boundary.md
│       └── 16-cross-cognitive-chunking.md
└── skills/
    └── dev/
        └── SKILL.md            The /dev routing skill
```

## How to use it

### As a human developer

Read the trigger table in `library/dev/README.md`. When you're about to write something that matches a trigger condition, read the entry before writing.

### As an AI agent

Load `skills/dev/SKILL.md` at the start of any code-writing task. Check the trigger table. When a trigger fires, halt, read the entry, apply the pattern, resume.

### Extending it

When you resolve a rework event and the fix reveals a repeatable pattern:
1. Create a new numbered entry in `library/dev/` using the 6-field format
2. Add a row to the trigger table in `library/dev/README.md` and `skills/dev/SKILL.md`
3. Cite the source: PEP number, official docs page, named book with author and section

A pattern earns an entry after it prevented rework, not before.

## Entry format

Every entry carries six fields:

1. **Pattern name:** 3-5 words
2. **Language(s)**
3. **Rework-prevention rationale:** one sentence naming the AI generation failure mode this prevents
4. **Canonical source:** author, title, section. Verifiable.
5. **Before/after code:** 4-8 lines per side showing the failure and the fix
6. **Trigger condition:** one prose sentence: what an agent should recognize as "halt, read this entry"

## Research basis

The 16 entries in this library come from a three-pass research thread:
- Pass 1: Gemini Deep Research (breadth across Python, TypeScript, PowerShell, SQL)
- Pass 2: ChatGPT adversarial audit (sourcing verification, technical accuracy, coverage gaps)
- Pass 3: ChatGPT third-pass (corrections to the audit, missing patterns, sound examples)

Three auth and permissions entries (17-19) landed from a separate ChatGPT-only three-pass thread.

## What this is not

- A security hardening checklist
- A linting ruleset (these patterns explain the why, not just the what)
- A complete catalog (it grows from resolved rework events)
- Vendor-specific (patterns transfer across platforms)

## License

MIT. Use it, fork it, extend it. If you add entries that survive production, share them back.
