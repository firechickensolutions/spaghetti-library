# Salesforce starter

Begin with [START-HERE.md](START-HERE.md). For first-time setup, project creation, and deployment, use the project skill `salesforce-learning`. Before designing or editing code, use `dev-baseline`.

Keep the Claude Code session rooted here so the skills stay discoverable. Generate the learner’s separate DX project in a new child folder and run Salesforce project commands from that project’s root. Guide one step at a time. Start with what the admin already knows about objects, permissions, and processes. The exercise targets Winter ’27 / API 68.0 and uses a confirmed learning org and synthetic data.

After the saved baseline, offer [NEXT-STEPS.md](NEXT-STEPS.md), explain what transfers to the learner's own work, and let them choose one exercise. Read its prerequisites and observable result before acting. Edit the lab's copied component, preserve checkpoints and other work, and record completed exercises and pending checks in the lab's existing README.

For a clean machine, use [FIRST-TIME-SETUP.md](FIRST-TIME-SETUP.md). Confirm that both skills and the packaged component are readable before proceeding. Explain which window and directory each step uses, give the expected result, and wait for the learner's result before the next step. Check existing tools before installing them. Use native PowerShell for Salesforce on Windows and Zsh/Bash on Mac; do not assume Git, Node, Java, or a Salesforce connection exists. Recheck tools in a new terminal after installation.

The learner may make local progress without an org: generate the DX project, copy the component and four test-tooling files into their documented locations, then install the locked packages and run audit, tests and lint. Run those tests before deploying. Keep live deployment, GraphQL, page activation, and actual-user access checks explicitly pending until observed in the learning org. Record the completed step and pending checks in the lab's existing README without credentials or private org details so a resumed session can continue.
