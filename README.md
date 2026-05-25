# Spaghetti Library

19 sourced patterns for AI-assisted code generation. Each one is a failure mode agents introduce reliably, the fix with a verifiable source, and a trigger condition specific enough to stop generation before the damage lands.

## Why it exists

Vibe coding removed the access moat. It did not change what a shipped product needs to survive production, and it did not change the fact that AI agents fail in predictable ways. Every team re-researches the same failure modes, re-learns the same patterns, and cleans up the same classes of generated code, and none of it gets written down somewhere others can use it.

This is that place.

The patterns here are sourced from PEPs, official language documentation, named practitioner texts, and peer-reviewed research, because an agent that reads a sourced entry before generating is less likely to re-introduce the failure than one reading a rule someone made up. Every entry stands alone. Read it, apply it, move on.

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
│       ├── 16-cross-cognitive-chunking.md
│       ├── 17-python-composition-root-creds.md
│       ├── 18-python-boundary-permission-gate.md
│       └── 19-python-refresh-and-reauthorize.md
└── skills/
    └── dev/
        └── SKILL.md            The /dev routing skill
```

## How to use it

Load `skills/dev/SKILL.md` at the start of a code-writing task. The skill checks the trigger table before generation and halts when a condition fires. If you prefer to drive it yourself, the same trigger table lives in `library/dev/README.md`: when you're about to write something that matches a trigger, read the entry before writing.

To add an entry: when a rework event reveals a repeatable pattern, create a numbered file in `library/dev/` using the 6-field format, add a row to both trigger tables, and cite the source. PEP number, official docs page, named book with author and section. A pattern earns a slot after it prevented rework, not before.

## Entry format

Every entry carries six fields:

1. **Pattern name:** 3-5 words
2. **Language(s)**
3. **Rework-prevention rationale:** one sentence naming the AI generation failure mode this prevents
4. **Canonical source:** author, title, section. Verifiable.
5. **Before/after code:** 4-8 lines per side showing the failure and the fix
6. **Trigger condition:** one prose sentence: what an agent should recognize as "halt, read this entry"

## Research basis

Entries 01-16 came from a three-pass thread: Gemini breadth pass, ChatGPT adversarial audit, ChatGPT third-pass. The auth and permissions entries (17-19) came from a separate ChatGPT-only three-pass thread; Pass 2 caught a P0 in entry 18 before it landed, and Pass 3 resolved two undefined class names in entry 19. Both corrections were folded before the entries were written.

## What this is not

- A security hardening checklist
- A linting ruleset (these patterns explain the why, not just the what)
- A complete catalog (it grows from resolved rework events)
- Vendor-specific (patterns transfer across platforms)

## License

MIT. Use it, fork it, extend it. If you add entries that survive production, share them back.
