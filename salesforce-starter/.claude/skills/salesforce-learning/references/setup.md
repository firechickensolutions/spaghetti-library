# Set up the tools and create a DX project

Keep the Claude Code session open in `salesforce-starter`. Use the VS Code terminal for the project commands, or give Claude the project path and have it run them from there. In VS Code, **Terminal → New Terminal** opens a shell. Run each command separately and stop on errors.

## Install and check the tools

1. Install VS Code for your operating system. In **Extensions**, search for **Salesforce Extension Pack** and check that Salesforce is the publisher. Follow the extension guide for any JDK requirements of features you enable. [VS Code download](https://code.visualstudio.com/download) · [Salesforce extension installation](https://developer.salesforce.com/docs/platform/sfvscode-extensions/guide/install.html)
2. Install Salesforce CLI using the official instructions for your OS. Where offered, the standalone installer or archive bundles Node. The npm installation uses your system Node. Winter ’27 Salesforce CLI requires Node.js 22 or later. Close and reopen VS Code and the terminal after installation so the shell finds `sf`. [Salesforce CLI installation](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-setup-install-cli.html) · [Winter ’27 tooling changes](https://developer.salesforce.com/blogs/2026/10/developers-guide-to-the-winter-27-release)
3. Run `sf --version`. Expect a line containing `@salesforce/cli/` and a version. If the command is missing, check the official install for your OS, then check the new shell’s PATH. On Windows, if PowerShell blocks an npm script shim, try `sf.cmd --version` or select the Command Prompt terminal profile. Keep the shell’s security policy in place.

## Choose and verify your learning org

Use your own [Developer Edition org](https://developer.salesforce.com/signup), a Trailhead Playground that supports the exercise, or an approved development sandbox. Choose an org where you can deploy metadata and add a Lightning App Page for the learning exercise. A scratch org, Dev Hub, package, or company org is unnecessary for this walkthrough.

Check that `sf-learning` is unused in `sf org list` before assigning it. If the alias exists, verify the existing connection or choose a fresh alias and substitute it consistently in every command. Use Salesforce’s browser sign-in and confirm the account in the browser. A Developer Edition or Playground generally uses the production **login endpoint** or its My Domain, even though the org is a learning org. For a sandbox, use its exact My Domain URL with `--instance-url`, or `https://test.salesforce.com` if your sandbox allows that login endpoint. The URL identifies a login route. Verify the actual org after authentication. [Salesforce CLI browser login](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_org_login_web.html)

```text
sf org login web --alias sf-learning
sf org list
sf data query --target-org sf-learning --api-version 68.0 --query "SELECT Id FROM Organization LIMIT 1"
```

For sandbox login, add `--instance-url` and the correct URL to the first command. For an existing connection you already checked, skip login and use its alias. Match the alias and username in `sf org list` to the learner’s signed-in browser. Match the query’s organization ID to **Setup → Company Information** in that browser. Compare locally, keeping usernames, org IDs, and URLs out of shared examples. The query is read-only and also checks whether the target serves API 68.0. If authentication, permissions, or the version check fails, diagnose the actual error before proceeding. If the learning org does not support 68.0, continue with local practice until you have a compatible org. [Salesforce CLI data query](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html)

Keep `--target-org` explicit for every data or deployment command in this exercise. The login command uses `--alias`; `sf org list` lists your connections and does not take a target flag. Avoid token-bearing CLI output such as `sf org display` or `sf org open --url-only`. Keep passwords and MFA codes in the browser.

## Generate the local project

From `salesforce-starter`, choose an unused child directory name. The example creates `salesforce-learning-lab`. First use `--help` to see the flags on your installed CLI. Run the generation commands from the parent directory and the remaining project commands from the new child directory.

```text
sf project generate --help
sf project generate --name salesforce-learning-lab --template standard --api-version 68.0
cd salesforce-learning-lab
```

In VS Code, use **File → New Window**, then **File → Open Folder** to open `salesforce-learning-lab`. Leave the original Claude Code session running in the starter folder. Check that `sfdx-project.json` and the `force-app` folder are visible at that level. In `sfdx-project.json`, confirm `"sourceApiVersion": "68.0"` and note the package directory, normally `force-app`. `sfdx-project.json` defines how Salesforce CLI reads your project and `force-app` holds source-format Salesforce metadata. A project command should run from the folder with `sfdx-project.json`. [Salesforce DX project generator](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_template_generate_project.html)

If you use Git for the lab, keep the generated ignore rules and check that local `.sf` and `.sfdx` state, auth exports, keys, and real data stay out of version control. A local history is enough for this exercise.

Continue with [your first LWC](first-lwc.md).
