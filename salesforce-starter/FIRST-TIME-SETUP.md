# First-time setup: from a new computer to Claude

Do these steps once. After that, Claude can guide you through Salesforce setup one step at a time. A **terminal** is a window where you type commands; **VS Code** is the editor where you see and change files. Salesforce CLI is the tool that will later send those files to your practice org.

## 1. Check account access

You need an internet connection, permission to install software on this computer, and a Claude account with **Claude Code access**. The free Claude chat plan does not include it. Use your existing eligible subscription or an account your organization provides; a GitHub or Salesforce login does not provide Claude access. Check [Anthropic's account options](https://code.claude.com/docs/en/quickstart) before starting. You do not need to buy API credits or create an API key for the subscription route.

VS Code and Salesforce CLI are free downloads. Use a learning Salesforce org later. If this is a managed work computer, use your organization's software-installation process when an installer is blocked.

## 2. Download and extract the folder

1. Open the [Spaghetti Library repository](https://github.com/firechickensolutions/spaghetti-library). Select the green **Code** button, then **Download ZIP**.
2. Find the ZIP in Downloads. On **Windows**, right-click it and choose **Extract All**, then **Extract**. On **Mac**, double-click the ZIP in Finder. Open the extracted `spaghetti-library-master` folder.
3. Copy the entire `salesforce-starter` folder to a local folder you can write to, such as a learning folder in Documents. Copy the folder itself, including its contents. Do not work inside the ZIP or copy only the visible Markdown files: the hidden `.claude` folder contains the skills and example.

You will use this separate copy throughout the exercise. Leave the rest of the repository in Downloads.

## 3. Install VS Code and open the starter

1. Visit [Visual Studio Code](https://code.visualstudio.com/download), download the installer for your computer, and open it. On Windows, the **User Installer** is a per-user option. On Mac, open the download and move Visual Studio Code to Applications. Follow Microsoft's [Windows](https://code.visualstudio.com/docs/setup/windows) or [Mac](https://code.visualstudio.com/docs/setup/mac) instructions if needed.
2. Launch **Visual Studio Code**. Choose **File → Open Folder**, then select your copied `salesforce-starter` folder. Review any Workspace Trust prompt for this downloaded folder before enabling its tools.
3. In the left-hand **Explorer**, you should see `START-HERE.md`, `FIRST-TIME-SETUP.md`, `CLAUDE.md`, and a folder named `.claude`. If you see only `salesforce-starter` inside another folder, open the starter itself. If `.claude` is missing, recopy the entire extracted folder. VS Code normally shows dot-folders even when Finder hides them.
4. Open `START-HERE.md`. Right-click its editor tab and choose **Open Preview** if you prefer formatted reading.

## 4. Install Claude Code in the terminal

Choose **Terminal → New Terminal** from the top menu. A panel opens at the bottom. This is a command window, separate from any AI chat panel. Its current folder should end in `salesforce-starter`. You can check it with `pwd` in PowerShell or on Mac.

Copy only the command inside a code box, paste it into the terminal, and press Enter. Do not copy the backticks or a prompt symbol. Run one command at a time and wait for it to finish.

**Windows:** use a **PowerShell** terminal. If necessary, choose **Select Default Profile → PowerShell** from the arrow next to the terminal's `+`, then open a new terminal. Run:

```powershell
irm https://claude.ai/install.ps1 | iex
```

**Mac:** use the normal terminal in VS Code, usually Zsh. Run:

```sh
curl -fsSL https://claude.ai/install.sh | bash
```

These commands download and run Anthropic's installer. It can be quiet while downloading. Wait for completion or an error. These are the [official native installation commands](https://code.claude.com/docs/en/setup); Node and Git are not prerequisites for that installation. On Windows, Git for Windows is optional for Claude's Bash tool; this walkthrough uses native PowerShell for Salesforce commands.

After installation, close **all VS Code windows**, reopen VS Code, and open the starter folder again. Open a fresh terminal and run:

```text
claude --version
```

**Expected:** a version number and `Claude Code`. If it says the command is not found, follow the installer's Setup notes or Anthropic's [terminal troubleshooting](https://code.claude.com/docs/en/terminal-guide#troubleshooting), then reopen VS Code. If a managed computer blocks installation, get the approved installation from your administrator instead of changing its security policy.

## 5. Start the conversation

In that terminal, run:

```text
claude
```

Complete the browser sign-in and return to VS Code. Review Claude's folder-trust prompt for your starter copy. Use the normal permission prompts; ask Claude to explain an unfamiliar proposed action. Keep passwords, authentication codes and tokens in the sign-in flow.

At the Claude prompt, paste the prompt from [START-HERE.md](START-HERE.md#give-claude-this-prompt). This is **Claude Code running in the terminal**; the VS Code chat sidebar or a claude.ai browser chat does not automatically read this folder.

**Expected:** Claude can read `salesforce-learning`, `dev-baseline`, and the packaged component. It should ask about your OS and learning org before leading you through the next step. If the skills are missing, check `.claude/skills` in Explorer and restart Claude from the starter folder. [Project skills](https://code.claude.com/docs/en/skills)

## Know which window to use

| Place | What goes there |
|---|---|
| Claude Code conversation in the starter window | Questions, the starter prompt, and requests to explain or run a step |
| A separate terminal opened with `+` | Commands beginning with `sf`, `node`, or `npm` when you run them yourself |
| Salesforce in your browser | Sign-in, Setup, synthetic records and the finished board |

Leave Claude open in the starter. Later, the walkthrough opens a second VS Code window for `salesforce-learning-lab`; its terminal is for project commands. If you close the session, reopen the starter, run `claude`, then use `/resume` to select the conversation. If you start over, paste the starter prompt and tell Claude the last step you completed.
