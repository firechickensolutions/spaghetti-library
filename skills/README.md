# Skills

Installable agent skills live here. A skill is a folder with a `SKILL.md` file that an AI coding agent or chat assistant can load as reusable instructions.

## Available skills

| Skill | Use it for |
|---|---|
| `dev` | Route code-writing tasks to the sourced pattern entries in `library/dev/` before generating code. |
| `council` | Run a multi-role council review and a subscription-backed judge for hard decisions, architecture calls, reviews, and research synthesis. |

## Install a skill

Copy the whole skill folder into your agent's skills directory.

Common Codex-style path:

```text
~/.codex/skills/<skill-name>
```

Example:

```text
~/.codex/skills/council
```

If your tool does not support skill folders, open the skill's `SKILL.md` and paste it into the tool's custom instructions, project knowledge, or chat context.
