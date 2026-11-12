# Set up the tools and create a DX project

If Claude and VS Code are not ready, begin with [First-time setup](../../../../FIRST-TIME-SETUP.md). Keep Claude open in `salesforce-starter`. When you run a command yourself, open a **separate terminal** with the `+` button. Use PowerShell on Windows and the default terminal on Mac. Claude can also run a step after explaining it. Run one command at a time and stop on errors.

## Install and check the tools

Ask Claude to check for installed tools first. Install only what is missing, using the official installer for your operating system and processor. On Mac, **About This Mac** identifies Apple silicon or Intel; on Windows, **Settings → System → About → System type** identifies the architecture. Use a single Salesforce CLI installation method.

| Tool | What to install | What it does here |
|---|---|---|
| Salesforce CLI | The official Windows `.exe` or Mac `.pkg` from [Salesforce's installation guide](https://developer.salesforce.com/docs/platform/sfdx-setup/guide/sfdx-setup-install-cli.html) | Generates the project and deploys the component; the standalone installer bundles its own Node runtime |
| Node.js and npm | Choose the **24 LTS** line in the version selector on [Node's download page](https://nodejs.org/en/download), then the Windows `.msi` or Mac `.pkg` installer | Runs the local component tests; npm is included. The CLI's bundled Node does not replace this installation |
| Java JDK | **JDK 21**, following [Salesforce's Java setup guide](https://developer.salesforce.com/docs/platform/sfvscode-extensions/guide/java-setup.html) | Supports the Apex language server included in Salesforce's extension pack |
| Salesforce Extension Pack | In VS Code's **Extensions** view, search for **Salesforce Extension Pack**, check publisher **Salesforce**, and select **Install** | Adds Salesforce editing tools. It does not install Salesforce CLI for you |

The sample uses Node 24 even when the download page recommends a newer LTS major. You can choose the current supported patch within 24. Use the ordinary installer defaults; optional native-module build tools are not needed for this sample. [Salesforce extension installation](https://developer.salesforce.com/docs/platform/sfvscode-extensions/guide/install.html)

Close all VS Code windows after installations, reopen the starter, and resume Claude as described in First-time setup. In a new terminal, run each check separately:

```text
sf --version
```

```text
node --version
```

```text
npm --version
```

```text
java -version
```

**Expected:** a Salesforce CLI version, Node `v24.x`, an npm version, and Java 21. Java may print its version on the terminal's error-output stream; a version message alone is not an installation failure. If the Apex extension still cannot find Java, follow the Java guide to set `salesforcedx-vscode-apex.java.home` to the installed JDK folder through VS Code Settings.

On Windows, if PowerShell blocks `sf.ps1` or `npm.ps1`, use `sf.cmd` or `npm.cmd` for that command and subsequent commands. For example, `npm.cmd --version`. Keep the shell's security policy in place. If a command is missing, reopen VS Code first, then check the official installation and PATH instructions with Claude. **PATH** is the list of folders the terminal searches for installed commands.

## Generate the local project

This step works before Salesforce sign-in. In the starter window, open a separate terminal; `pwd` should end in `salesforce-starter`. Make sure there is no existing child folder named `salesforce-learning-lab`. If there is, inspect it with Claude and resume it or choose a fresh name; do not overwrite it.

Run these separately. `--help` explains the command. The second command creates local files. `cd` changes the terminal's current directory.

```text
sf project generate --help
```

```text
sf project generate --name salesforce-learning-lab --template standard --api-version 68.0
```

```text
cd salesforce-learning-lab
```

**Expected:** the CLI reports created files, and VS Code Explorer shows a `salesforce-learning-lab` folder containing `sfdx-project.json`, `package.json`, and `force-app`. A DX project is the local folder that holds your Salesforce source and tool settings; generating it does not create or change an org.

Use **File → New Window**, then **File → Open Folder** to open `salesforce-learning-lab` in the second window. Leave Claude in the starter window. Open a new terminal in the lab window for all remaining project commands. Confirm `pwd` ends in `salesforce-learning-lab` and `sfdx-project.json` is visible at the top of Explorer. Its `sourceApiVersion` should be `68.0`; its package directory is normally `force-app`. [DX project generator](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_template_generate_project.html)

You can now copy the component and run the [local tests](first-lwc.md#run-the-bundled-local-tests) without an org. Connect a learning org before proceeding to that guide's deployment steps.

## Choose and verify your learning org

Use your own [Developer Edition org](https://developer.salesforce.com/signup), a suitable Trailhead Playground, or an approved development sandbox. For a new Developer Edition org, complete the signup and email activation, then verify you can sign in to Lightning Experience and open Setup. You need metadata deployment and app-page access in that practice org. A scratch org, Dev Hub, package, or company production org is unnecessary.

For a **Trailhead Playground**, the Launch button may sign you in without showing the credentials Salesforce CLI needs. Follow [Get Your Playground Username and Password](https://trailhead.salesforce.com/content/learn/modules/trailhead_playground_management/get-your-trailhead-playground-username-and-password) first. A Trailhead login and its playground's username can differ.

An **alias** is a local nickname for an authenticated org. From the lab terminal, run:

```text
sf org list
```

An empty list is normal on a new computer. Check that `sf-learning` is unused before assigning it. If it exists, verify that connection or choose a fresh alias and substitute it consistently. For a Developer Edition or Playground, run:

```text
sf org login web --alias sf-learning
```

**Expected:** a Salesforce browser sign-in opens. Sign in to the practice org, review the access prompt, and return to the terminal; it should report successful authorization. A Developer Edition or Playground usually uses the production **login endpoint** or its My Domain even though it is a learning org. For a sandbox, ask Claude to add `--instance-url` with its exact My Domain URL, or `https://test.salesforce.com` where that login endpoint is supported. [Browser login](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_org_login_web.html)

Run these separately after login:

```text
sf org list
```

```text
sf data query --target-org sf-learning --api-version 68.0 --query "SELECT Id FROM Organization LIMIT 1"
```

Match the alias and username in the list to your browser's practice account. In that browser, open **Setup → Company Information** and compare the organization ID with the single query result. Salesforce can display a 15-character ID while the CLI returns its 18-character form; the first 15 characters must match exactly, including case. Ask Claude to explain the comparison without pasting either value. The read-only query also checks API 68.0 support. [Find the org ID](https://help.salesforce.com/s/articleView?id=000006019&language=en_US&type=1) · [15- and 18-character IDs](https://help.salesforce.com/s/articleView?id=000004383&language=en_US&type=1) · [Data query](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_data_query.html)

If authentication, access, or API support fails, diagnose the actual error before deployment. Local project work and tests can continue while org access is pending. Keep `--target-org` explicit on every data or deployment command; login uses `--alias`, and `sf org list` has no target flag. Keep passwords and MFA codes in the browser, and keep usernames, org IDs, and URLs out of shared examples. Avoid token-bearing output such as `sf org display` or `sf org open --url-only`.

## If a step fails

| What you see | Next step |
|---|---|
| `NotInProject` or a missing `sfdx-project.json` | Use the lab window's terminal; check `pwd` and open the folder containing that file |
| The project directory already exists | Resume the existing lab after inspecting it, or use a new name consistently |
| A command is not recognized | Restart all VS Code windows after installation, then check that tool's PATH with Claude |
| Sign-in succeeds but org verification fails | Check the actual alias/account and error; do not retry against a different org by guesswork |
| A firewall, proxy, or managed-computer policy blocks a download | Use the organization's approved configuration; keep certificate and security checks enabled |

Tell Claude the command, which step failed, and the relevant error text with private values removed. Do not paste complete authentication logs.

Continue with [your first LWC](first-lwc.md). If you use Git later, keep the generated ignore rules: local `.sf` and `.sfdx` state, auth exports, keys and real data must stay out of version control.
