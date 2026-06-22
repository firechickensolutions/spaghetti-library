# Council Skill

A compact council pattern for asking several independent model or agent roles to pressure-test a decision, then having a final judge reconcile the result.

The inspiration is OpenRouter's easy model-comparison experience: ask multiple capable models, compare their reads, then synthesize the strongest answer. This skill is intentionally not tied to OpenRouter. For day-to-day use, the final judge should run on the assistant or model surface where you already have a trusted subscription, account, and data boundary.

Use it for architectural calls, high-stakes recommendations, adversarial reviews, product framing, and research synthesis. Do not use it as ceremony for simple questions.

## What you get

This folder contains:

- `SKILL.md` - the actual agent skill. This is what a code agent reads.
- `README.md` - this human setup guide.

There are no packages to install and no API keys required. The skill is a reusable thinking workflow.

## Download it

Download or clone the Spaghetti Library repo:

```bash
git clone https://github.com/firechickensolutions/spaghetti-library.git
```

Or open the folder directly on GitHub:

```text
https://github.com/firechickensolutions/spaghetti-library/tree/master/skills/council
```

Then copy this folder:

```text
spaghetti-library/skills/council
```

into the place your agent reads skills from.

Common destinations:

```text
~/.codex/skills/council
```

or, for a project-local copy:

```text
your-project/skills/council
```

If your tool has its own "custom skills", "project instructions", or "knowledge" area, upload or paste `SKILL.md` there.

## Use it in a code agent

After the folder is in your skills directory, start a new agent session and ask for the council by name:

```text
Use the council skill to pressure-test this architecture decision.
Decision: Should we adopt <option A> or <option B>?
Sources: Read docs/adr.md and src/core/.
I want Builder, Skeptic, Operator, and Judge roles.
```

For code agents that support subagents, the council works best when each role is run independently and the judge sees their outputs afterward. If your agent does not support subagents, it can still run the roles sequentially in one conversation.

## Use it in Claude Chat, ChatGPT, or CoWork-style tools

Chat-only tools may not automatically load a skill folder. Use the skill manually:

1. Open `SKILL.md`.
2. Paste it into the chat, or attach it if your tool supports file attachments.
3. Add your decision and sources.
4. Ask the assistant to run the council roles and then judge them.

Starter prompt:

```text
Use the attached Council Skill.

Decision: <the decision you need help with>
Context: <paste the relevant facts, docs, links, or code excerpts>

Run these roles independently:
- Builder
- Skeptic
- Operator
- Domain reader

Then act as Judge. Do not count votes. Identify the strongest objection, reconcile disagreements, and give me a final recommendation with the next action.
```

For stronger independence, run the roles in separate chats or different subscribed model surfaces, then paste their answers into your preferred subscription-backed model and ask it to judge.

## What "subscription-backed judge" means

The council pattern was inspired by OpenRouter's model-comparison flow, but the judge does not need to run through OpenRouter. If you already pay for Claude, ChatGPT, Codex, CoWork, or another trusted model surface, use that as the judge.

The important idea is:

```text
many independent reads -> one trusted judge -> one decision
```

Do not send private work, customer data, source code, or confidential documents to an external router or model unless you are comfortable with that data boundary.

## When to use it

Good fits:

- choosing between architectures
- reviewing a risky implementation plan
- pressure-testing a product direction
- deciding whether evidence is strong enough
- reconciling contradictory model answers
- writing an ADR or final recommendation

Bad fits:

- simple factual questions
- tiny code edits
- formatting or copy changes
- anything where a direct answer is clearly enough

## Can it be used outside code agents?

Yes, with limits. In Claude Chat, ChatGPT, or CoWork-style tools, the skill can be used as a prompt/process pattern: paste or reference the `SKILL.md`, ask for named council roles, then ask one model to judge the outputs. It is strongest in code-agent environments because subagents, file reads, and source-grounded review can be isolated and repeated. In chat-only surfaces, it still works, but the independence is weaker unless you manually run separate conversations or models.
