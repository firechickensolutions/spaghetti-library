---
name: dev-baseline
description: Use before designing, generating, or editing code and tests. Reuse the existing owner or platform feature, verify version-sensitive APIs, and prove the changed behavior and relevant failure cases.
---

# Development baseline

1. **Describe what the user will observe.** Identify one success case and the failures that matter. Decide how to observe each through the normal entry point. A user story with two checks is enough for a small change.
2. **Read before editing.** Find the behavior’s current owner, existing configuration, source, tests, and local changes. Preserve working behavior and others’ edits. Fix the current owner when it can meet the requirement. In Salesforce, consider a record page, Dynamic Forms, permission sets, a validation rule, or Flow before custom code. Then prefer existing code, standard libraries, and installed dependencies before adding new ones.
3. **Ground version-sensitive work.** Read the project’s manifest or lockfile and the installed tool’s version. Check official docs or source for the exact target release and installed tool’s syntax. Report gaps where the version or behavior is unclear. Keep credentials, real customer data, and secret-bearing logs out of lookups.
4. **Write the smallest clear change.** Prefer direct code for one consumer. Name meaningful steps and keep related state together. Parse raw inputs at the trust boundary. Add a guard where a real failure can occur, and make the failure observable and recoverable.
5. **Prove what changed.** For a UI, open the real page as the intended user and exercise it. For a safety check, use a known-denied case and assert the denial through the same application path. For a retryable write, establish what happened before retrying, use a transaction or idempotency key where appropriate, and verify the resulting state.

Use [engineering checks](references/engineering-checks.md) when a change handles access, data boundaries, or mutations, or when generated code is growing harder to explain.
