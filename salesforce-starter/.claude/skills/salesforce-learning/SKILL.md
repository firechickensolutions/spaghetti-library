---
name: salesforce-learning
description: Guide Salesforce LWC development from first tool setup and a learning-org deployment through least-privilege testing and production-release readiness. Use for Salesforce component builds, permissions, deployment planning, and the Winter '27 API 68.0 baseline.
---

# Salesforce learning project

- Start with the learner’s OS and available practice org. Offer Developer Edition if they need an org. Use synthetic data in a confirmed learning org. Guide browser sign-in without asking for passwords, MFA codes, access tokens, or authentication URLs.
- Teach the route from Setup to source files. Objects and fields describe the work, Lightning App Builder places and configures a component, and permissions and sharing determine what it can display. Ask which parts Salesforce configuration already solves.
- Use [setup](references/setup.md) for tools, an explicit learning-org alias, and a new local Salesforce DX project. Verify the installed `sf` commands and API 68.0 support before deployment.
- Use the [Related Activity Board walkthrough](references/first-lwc.md) and its [packaged LWC](assets/relatedActivityBoard/) for the first deployment. Explain Task status, the Related To relationship, and the board’s allowlisted Case fields. The exercise adds a read-only app page alongside standard views. Use `dev-baseline` before changing code.
- Preview and validate only the supplied bundle. Confirm the target and change with the learner before applying metadata, page activation, or permission edits. Follow pending jobs by ID. Verify the page as allowed and restricted users. Save local test outcomes and any pending org checks.
- For an exercise involving Apex, custom data access, or permission metadata, read [permissions, Apex, and tests](references/permissions-and-apex.md).
- For a proposed release beyond the learning org, read [production readiness](references/production-readiness.md) before planning validation, rollout, and recovery.
