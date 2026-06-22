---
name: council
description: Run a multi-model or multi-agent council review before making a high-stakes recommendation, architectural decision, code-review verdict, product framing call, or research synthesis. Use when the user asks for a council, panel, judge, debate, adversarial pass, independent reviewers, model comparison, or when a decision would benefit from separated proposals and a subscription-backed final judge rather than one agent collapsing the answer too early.
---

# Council

Use a council when one answer is likely to be overconfident, under-explored, or shaped by a single model's habits. The council pattern separates candidate generation from judgment: several independent voices produce bounded opinions, then a judge reconciles them into a recommendation.

## Core rule

OpenRouter is a normal way to run the panel models in an automated council and requires the operator's `OPENROUTER_API_KEY`. The judge should run where the operator already has an active subscription or trusted account when possible. Do not route the final judge through OpenRouter just because the panel used it.

## Workflow

1. State the decision under review in one sentence.
2. Split the council into roles with distinct jobs, not personalities.
3. Give each role the same source material and the same output budget.
4. Keep role outputs independent until after they are written.
5. Ask the judge to reconcile disagreements, identify false consensus, and name what evidence would change the recommendation.
6. Return the final answer with:
   - verdict
   - strongest supporting argument
   - strongest objection
   - decision risks
   - next action

## Suggested roles

Use only the roles that fit the task.

| Role | Use for |
|---|---|
| Builder | Feasibility, implementation path, hidden complexity |
| Skeptic | Failure modes, missing proof, overclaim detection |
| Operator | User workflow, cognitive load, real-world usefulness |
| Domain reader | Source-grounded facts, terminology, constraints |
| Security/privacy | Data boundary, custody, misuse, compliance risk |
| Judge | Final synthesis and recommendation |

## Good council prompts

Ask roles for short, comparable outputs:

```text
Decision: <one sentence>
Sources: <files, links, or summarized evidence>
Role: <role>
Return:
- recommendation
- top 3 reasons
- top 3 risks
- one falsifier
```

Then judge:

```text
You are the judge. Reconcile the council outputs.
Do not average them. Identify which objections are load-bearing.
Return a final recommendation, the reason, the biggest residual risk, and the next action.
```

## Guardrails

- Do not count votes. A single correct objection can outweigh four agreeing answers.
- Do not let a role invent sources. Source-grounded roles must cite the evidence they used.
- Do not use council theater for simple work. If the task is obvious, answer directly.
- Do not send private or customer data to OpenRouter or any external model/router unless the user has approved that boundary.
- Do not ask the user to paste API keys into chat. Use the agent's environment or secret manager.
- Keep the final recommendation decisive. The council exists to improve judgment, not to produce a mushy compromise.

## Code-agent usage

In a code environment, emulate the council with isolated subagents or separate reasoning passes when tool support exists. If no subagent/tool support exists, run the roles sequentially in the current context but keep their notes separated before judging.

When editing code, the council does not replace tests, browser proof, or source reads. It is a thinking structure before action or review.
