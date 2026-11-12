# Your first Salesforce component with Claude Code

**For certified Salesforce admins who are new to coding.** You already know how objects, fields, permissions, and business processes fit together. That knowledge tells you what to build, when Salesforce configuration already solves it, and what to check as the people who will use it. The new part is keeping a small change in files, deploying it, and proving it works.

You’ll set up VS Code and Salesforce CLI, create a fresh Salesforce DX project, and deploy a **Related Activity Board** in a learning org on **Winter ’27 / API 68.0**. It’s a separate, read-only Lightning Web Component (LWC) modeled on Kanban. Task cards group by status and show related record links and selected Case fields when Salesforce allows them. You choose which Case fields to show in Lightning App Builder. Use a personal Developer Edition org, a suitable Trailhead Playground, or an approved development sandbox with synthetic data. [Salesforce Winter ’27 developer guide](https://developer.salesforce.com/blogs/2026/10/developers-guide-to-the-winter-27-release)

## Start a session

1. On the repository page, choose **Code → Download ZIP** and extract it. Copy the whole `salesforce-starter` folder to a learning workspace, including the hidden `.claude` directory. If you need Claude Code, follow Anthropic’s installation and sign-in instructions for your operating system and available account. [Claude Code quickstart](https://code.claude.com/docs/en/quickstart)
2. Open a terminal in `salesforce-starter`, the folder containing this file, and run `claude`. In VS Code, you can open this folder with **File → Open Folder** and then **Terminal → New Terminal**. [Claude Code project skills](https://code.claude.com/docs/en/skills)
3. Paste the prompt below. Enter Salesforce credentials directly in the browser.

```text
I’m a certified Salesforce admin with no coding experience. Read START-HERE.md
and use the salesforce-learning and dev-baseline skills in this folder.
Ask what operating system and learning org I use. Guide me one step at a time
through VS Code, Salesforce CLI, a fresh DX project, and deploying the supplied
Related Activity Board LWC on its own Lightning App Page. Use Winter ’27 / API
68.0 and synthetic Tasks and Cases. Show me how to choose the Case fields in
Lightning App Builder, run the local tests, and check what an allowed user and
a restricted user can see. Explain what each command does, where to run it, and
what I should see. Let me sign in in the browser and confirm the learning org
and change with me before deployment or Setup edits. Help me save the baseline
and identify what still needs checking before a real release.
```

You can also follow the [setup walkthrough](.claude/skills/salesforce-learning/references/setup.md) and [board walkthrough](.claude/skills/salesforce-learning/references/first-lwc.md) directly.

*Adapted from Firechicken Solutions’ Spaghetti Library development patterns and Salesforce engineering guidance.*
