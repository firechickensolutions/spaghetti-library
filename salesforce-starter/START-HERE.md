# Your first Salesforce component with Claude Code

**For certified Salesforce admins who are new to coding.** You already know how objects, fields, permissions, and business processes fit together. That knowledge tells you what to build, when Salesforce configuration already solves it, and what to check as the people who will use it. The new part is keeping a small change in files, deploying it, and proving it works.

You’ll set up VS Code and Salesforce CLI, create a fresh Salesforce DX project, and deploy a **Related Activity Board** in a learning org on **Winter ’27 / API 68.0**. It’s a separate, read-only Lightning Web Component (LWC) modeled on Kanban. Task cards group by status and show related record links and selected Case fields when Salesforce allows them. You choose which Case fields to show in Lightning App Builder. Use a personal Developer Edition org, a suitable Trailhead Playground, or an approved development sandbox with synthetic data. [Salesforce Winter ’27 developer guide](https://developer.salesforce.com/blogs/2026/10/developers-guide-to-the-winter-27-release)

## Start here on a new computer

Follow [First-time setup](FIRST-TIME-SETUP.md) first. It covers the download, VS Code, Claude Code installation and account access, and how to open the right folder. You do not need Git or a GitHub account for this download.

**Already have the tools?** Open the extracted `salesforce-starter` folder in VS Code. Confirm that Explorer shows `START-HERE.md`, `CLAUDE.md`, and `.claude`. Open **Terminal → New Terminal**, run `claude`, and sign in if prompted. Keep this window open.

## Give Claude this prompt

Paste this into the **Claude Code conversation**, then press Enter. Commands beginning with `sf`, `node`, or `npm` go in a separate terminal later; this paragraph goes to Claude.

```text
I’m a certified Salesforce admin with no coding experience. Read START-HERE.md
and use the salesforce-learning and dev-baseline skills in this folder.
Verify that you can read both skills and the example files. Ask about my
operating system and learning org, and check which tools are already installed.
Guide me through the remaining setup, a fresh DX project, and the supplied
Related Activity Board LWC on its own Lightning App Page. Give me one step
at a time and wait for my result before the next step. Explain each command,
where to run it, and what I should see. Use Winter ’27 / API 68.0 and synthetic
Tasks and Cases. Run the local tests before deployment. Let me sign in in the
browser, and confirm the learning org and change with me before deployment
or Setup edits. Show me the App Builder field controls and how to check what
allowed and restricted users can see. Help me save the baseline and identify
what still needs checking before a real release.
```

**First checkpoint:** Claude should identify both skills and the Related Activity Board, ask about your operating system and practice org, then give you one next step. If it cannot find the files, check the folder and hidden `.claude` directory before continuing.

You can also follow the [setup walkthrough](.claude/skills/salesforce-learning/references/setup.md) and [board walkthrough](.claude/skills/salesforce-learning/references/first-lwc.md) directly.

*Adapted from Firechicken Solutions’ Spaghetti Library development patterns and Salesforce engineering guidance.*
