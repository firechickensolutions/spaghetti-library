# Make the board your own

You now have a working Salesforce component, a place to experiment, and a repeatable way to build with AI. Your admin knowledge helps you choose the records, understand relationships, decide who should see a field, and recognize when configuration already meets the need. Claude can help turn those decisions into files, explain the changes, and run the checks with you.

Start after the [board walkthrough](.claude/skills/salesforce-learning/references/first-lwc.md) has reached its saved baseline. You do not need to understand every line of code before trying one small change. Use your confirmed learning org and fictional records. Keep Claude Code open in the **starter** folder; make code changes in the **lab's copied component**, leaving the supplied example available for comparison. Paste the prompts below into Claude, not a command terminal.

If you have no learning org yet, you can read the files and make the local change in exercise 3 after local setup and checks pass. Save deployment and browser checks as pending in the lab's existing README.

## 1. Follow a Task through the board

**Try:** Open the practice board and find the two fictional Tasks from the walkthrough. Open the Case-related Task, change its Status to another available value on the standard record page, return to the board, and select **Refresh**. Open its parent Case from the card. Compare it with the Task whose Related To field is blank.

```text
Use the salesforce-learning skill. Help me follow one of my fictional Tasks
through the board. Confirm my learning org and the practice records first.
Guide one action at a time, and explain how Task Status and Related To
control what I see. Let me make the status change on the standard record
page, then help me check Refresh and both record links.
```

**You should see:** The changed Task moves to its new status column, and the column counts update. Its Case link opens the expected record. The unrelated Task still appears and has no parent link. The board itself is read-only; status changes happen on standard Salesforce pages.

**What transfers:** You can describe an expected result and verify it through the same screens a colleague would use. To reset this exercise, restore only that fictional Task's original Status and refresh.

## 2. Choose the context on each card

**Try:** In **Setup → Lightning App Builder**, edit the practice App Page and select the Related Activity Board. Note the current values of **Show case number**, **Show case status**, and **Show case priority**. Toggle one setting at a time, save, return to the board, and reload it. Keep the existing page activation and audience.

```text
Help me try the three Case field controls already supplied in App Builder.
Explain which setting changes which row before I change it. Keep the page's
current audience. Compare each saved result with my prediction, then help me
restore my original settings. If a field is missing, check both the setting
and my actual field access before proposing a permission change.
```

**You should see:** A permitted Case row appears or disappears with its checkbox. **Case priority** is separate from the Task's own **Priority** row. Turning off Case priority does not hide Task Priority. The controls do not add arbitrary fields or grant access.

**What transfers:** You can offer useful configuration choices while respecting data permissions. For actual access proof, follow [Check access with a second user](.claude/skills/salesforce-learning/references/first-lwc.md#check-access-with-a-second-user). A display checkbox alone is not a permission test.

## 3. Make your first code change

**Try:** Change the board heading from **Related Activity Board** to **Practice Follow-up Board**. Ask Claude to show you the `title` on `lightning-card` in the lab's `force-app/main/default/lwc/relatedActivityBoard/relatedActivityBoard.html`. This is the title inside the component; the Salesforce navigation tab and App Builder component label have separate names.

Before editing, save a known-working checkpoint. If the lab already uses Git, have Claude inspect its changes and help save only your intended work. Otherwise, keep a copy of this one HTML file outside `force-app`, where deployment will not include it. Git is optional for this exercise.

```text
Use dev-baseline and salesforce-learning. In my lab's copied component,
change only the lightning-card title to Practice Follow-up Board. Show me
the original line and the proposed change, and help me save a checkpoint
first. Explain the file in terms I know from Lightning App Builder.
Run the existing local checks from the walkthrough and show their results.
After I confirm the learning org and change, follow the bundle preview,
validation and deployment steps. Help me check the actual page and explain
how to restore just this edit without discarding any other work.
```

**You should see:** The existing audit, component tests, toolchain checks, and lint pass. After a successful deployment and page reload, the new title appears; cards, record links, Case settings, and Refresh still work. Use the walkthrough's [deployment steps](.claude/skills/salesforce-learning/references/first-lwc.md#preview-validate-and-deploy-the-bundle) and [cache troubleshooting](.claude/skills/salesforce-learning/references/first-lwc.md#if-the-board-does-not-look-right) if the old title remains.

**What transfers:** You can ask for a bounded change, inspect the difference, and verify both the change and the behavior you wanted to preserve. To undo it, restore only that title edit in the lab, repeat the checks, and redeploy the bundle after confirming the target. Restoring a local file alone does not change the deployed page.

## 4. Turn one of your own needs into a small next feature

**Try:** Choose a visibility problem you understand, such as showing one extra permitted Case field or adding context from a custom Project parent. Describe the person using the screen, the decision they need to make, and one value that would help. Use fictional examples and approved schema details. This exercise produces a small plan; the extension is not already included in the pack.

```text
Help me scope one small Salesforce improvement using dev-baseline and
salesforce-learning. Ask me who needs the view, which records belong there,
and what they need to see. First check whether a standard view, report,
dashboard, or configuration meets the need. If code is useful, inspect the
actual object and relationship API names and the intended user's access.
Propose one small change, with an allowed case, a denied or missing-data
case, and a way to undo it. Keep implementation in my learning org as a
separate next step for me to choose.
```

**You should have:** A short request in the lab's README describing the audience, record scope, fields, expected result, permission checks, and recovery step. Claude should identify unanswered questions before writing against a guessed schema.

**What transfers:** Your understanding of the business process becomes the specification for the next change. The supplied board reads up to 50 visible Tasks and adds Case details. Project fields, a team filter, paging, a Lead board, or an Opportunity board each need their own implementation and checks. Agree on the record scope before treating any extension as a complete workload view.

## Bring the useful parts into your own work

The reusable habit is: describe the result, inspect what already exists, make one small change, run the relevant checks, and verify it as the intended user. Keep the outcome and any unfinished checks in your project's existing README so a later session can pick up accurately.

| Take with you | How it helps |
|---|---|
| `salesforce-learning` skill, references, and example assets | Tool setup, Salesforce-specific checks, the record-reading example, deployment, and release guidance |
| `dev-baseline` skill and its references | Clear requirements, small changes, reuse, testing, and recovery |
| The lab's source and tests | A working example you can inspect and adapt to another confirmed learning project |
| The permission and troubleshooting lessons | Separate checks for page access, fields, objects, sharing, and page-layout assignments |

For your next experiment, you can keep using this starter window and lab. To use the skills in an existing project, have Claude compare its current instructions first, then copy the complete `salesforce-learning` and `dev-baseline` folders into that project's `.claude/skills` without overwriting existing skills. Keep their reference and asset subfolders together. Review their starter-specific paths and setup directions for the new project, preserve the existing `CLAUDE.md`, and confirm Claude can read the skills and all needed references. [Claude Code project skills](https://code.claude.com/docs/en/skills)

The bundled dependency files are a tested starting point for a fresh lab. Have Claude compare them with an existing project's tooling instead of replacing its manifest or lockfile. Keep real records and credentials out of shared examples. Before any release beyond a learning org, use the [production-readiness guide](.claude/skills/salesforce-learning/references/production-readiness.md) and your team's review process; the pack's rehearsal does not prove a new feature in a different org.
