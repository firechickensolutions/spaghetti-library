# Spaghetti Library

19 sourced patterns for AI-assisted code generation, plus reusable agent skills. Each pattern is a failure mode agents introduce reliably, the fix with a verifiable source, and a trigger condition specific enough to stop generation before the damage lands.

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
│       ├── README.md           Trigger routing table for /dev
│       └── 01-19-*.md          Sourced code-generation patterns
└── skills/
    ├── README.md               Index of installable skills
    ├── dev/
    │   └── SKILL.md            Routes code-writing tasks to library/dev entries
    └── council/
        ├── SKILL.md            Multi-role council + subscription-backed judge workflow
        └── README.md           Human setup and usage guide
```

## How to use it

Clone the repo:

```bash
git clone https://github.com/firechickensolutions/spaghetti-library.git
```

### Use the /dev pattern library

If you're using a CLAUDE.md-aware agent (Claude Code or any tool that loads `CLAUDE.md`), the `/dev` trigger table fires automatically: the skill is invoked before generation starts, not after. The `CLAUDE.md` in this repo wires it.

If you're driving it manually, load `skills/dev/SKILL.md` at the start of a code-writing task, or read the trigger table in `library/dev/README.md` directly: when you're about to write something that matches a trigger, read the entry before writing.

To add an entry: when a rework event reveals a repeatable pattern, create a numbered file in `library/dev/` using the 6-field format, add a row to both trigger tables, and cite the source. PEP number, official docs page, named book with author and section. A pattern earns a slot after it prevented rework, not before.

### Use an installable skill

Each folder under `skills/` is a standalone skill. Browse the skill index at `skills/README.md`, copy the folder you want into your agent's skill directory, or paste its `SKILL.md` into tools that support custom instructions.

Common Codex-style install path:

```text
~/.codex/skills/<skill-name>
```

For example, copy `skills/council/` to `~/.codex/skills/council/`, then start a new session and ask:

```text
Use the council skill to pressure-test this decision.
```

See each skill's README for user-facing setup notes.

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
