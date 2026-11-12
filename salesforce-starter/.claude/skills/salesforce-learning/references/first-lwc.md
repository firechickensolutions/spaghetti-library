# Deploy the Related Activity Board

Imagine a service team that needs to see follow-up Tasks by status and know which Case each Task is about. Standard Salesforce Kanban is based on a single list view and shows up to four fields on a card. The supplied board uses the same column-and-card pattern on its own **Lightning App Page**. Opening a card or related record takes the user to the usual Salesforce record page. The board itself performs read-only queries. [Salesforce Kanban configuration](https://help.salesforce.com/s/articleView?id=xcloud.kanban_configuration.htm&language=en_US&type=5) · [Kanban display limits](https://help.salesforce.com/s/articleView?id=kanban_considerations_admin.htm&language=en_US&type=5)

In a real design, first check whether an existing view or configuration meets the need. A cross-object formula can expose a related value to users who can’t open the parent record. Use one only when that exposure is intended. This sample reads related records as the signed-in user. [Cross-object formula access](https://help.salesforce.com/s/articleView?id=fields_creating_cross_object_advanced.htm&language=en_US&type=5)

## Copy the example into your project

Complete the tool and local-project steps in [setup](setup.md) first. You can copy and test the component before signing in to Salesforce.

1. In the **starter** VS Code window, expand `.claude → skills → salesforce-learning → assets`. Right-click the entire `relatedActivityBoard` folder and choose **Copy**.
2. In the **lab** window, expand `force-app → main → default`. Select its `lwc` folder and **Paste**. Create `lwc` if the template does not include it. Check that no `relatedActivityBoard` folder already exists there before pasting; ask Claude to inspect an existing copy instead of replacing it.
3. Confirm the result below. Copy the folder once, so there is no extra `relatedActivityBoard/relatedActivityBoard` nesting. The files are already complete; you do not need to paste code from GitHub or create a new component with the wizard.

```text
salesforce-learning-lab/
  sfdx-project.json
  package.json
  force-app/main/default/lwc/relatedActivityBoard/
    relatedActivityBoard.js
    relatedActivityBoard.html
    relatedActivityBoard.css
    relatedActivityBoard.js-meta.xml
    __tests__/relatedActivityBoard.test.js
```

You can also ask Claude: “Copy the supplied `relatedActivityBoard` folder from this starter's `.claude/skills/salesforce-learning/assets` into the lab's `force-app/main/default/lwc`, preserving any existing work, then check the five files.” If your package directory differs from `force-app`, substitute it consistently.

Keep Claude open in the starter folder and ask it to inspect the copied component in the DX project. Have it explain the HTML and CSS that lay out the board, the JavaScript that reads and groups records, the XML that exposes the board and its settings in App Builder, and the Jest file that tests the user-visible behavior. Use the supplied source as your baseline.

The board queries the **first 50 Tasks visible to the signed-in user**, sorted by Status and record ID, and groups the results into columns. The counts reflect loaded cards. A notice appears if more Tasks are available. This view uses its own query and scope. The two read queries fetch Tasks and their permitted Related To IDs (`WhatId`), then request optional Case details in one batch for those parent IDs. Only matching Cases that the user can read contribute details. Other parent types still have a standard record link; their extra fields require a separate extension. A visible Related To ID does not grant access to its record: Salesforce checks access when the user opens the link. The batch may return fewer details than requested and the Task cards remain useful in that case. [GraphQL record and optional-field behavior](https://developer.salesforce.com/docs/platform/graphql/guide/query-record-objects.html) · [Task and Event API support](https://developer.salesforce.com/docs/platform/graphql/guide/query-limits.html)

## Install the checked dependency set and run the tests

The pack includes a dependency manifest and lockfile so you can install the same versions that were tested together. In the **lab** window, open **Terminal → New Terminal** and confirm `sfdx-project.json` is at this folder level. Check `node --version` and `npm --version`; use Node 24 LTS from [setup](setup.md). The release rehearsal uses Salesforce CLI 2.158.7, Node 24.22.3 and npm 11.19.1. On Windows, use `npm.cmd` if PowerShell blocks the `npm.ps1` shim.

Before the first package install, copy the four files from [test-tooling](../assets/test-tooling/) into the **root of the fresh lab**, beside `sfdx-project.json`:

| File | Purpose |
|---|---|
| `package.json` | Keeps the standard project commands and selects compatible, repaired dependencies |
| `package-lock.json` | Records the exact dependency versions and download integrity checks |
| `eslint.config.js` | Checks the component's JavaScript and permits test-only timers in `__tests__` |
| `toolchain.test.cjs` | Checks the repaired dependency against the unsafe input that caused its advisory |

In the starter window, expand `.claude → skills → salesforce-learning → assets → test-tooling`, select these four files, and choose **Copy**. Select the lab's root folder in the other window and **Paste**. This replaces the generated `package.json` and `eslint.config.js`; leave the generated `jest.config.js`, project settings, and Salesforce source in place. The copied files must be at the lab root, not inside a `test-tooling` subfolder.

You can ask Claude to do the copy and show the changes. These files are for a **fresh standard project**. If you have already customized the lab's package files, have Claude compare and preserve that work before applying the dependency repairs. Keep the copied lockfile with your project. Check that `.forceignore` includes `**/__tests__/**` and `node_modules/`.

Run each command separately. First, install the locked packages:

```text
npm ci --ignore-scripts
```

**Expected:** installation finishes and the audit summary reports **0 vulnerabilities**. `npm ci` installs the lockfile's exact versions; `--ignore-scripts` skips dependency setup hooks, including the generated Git-hook setup. This lets the lab run before you install Git. It can take several minutes. [npm ci](https://docs.npmjs.com/cli/v11/commands/npm-ci)

The stable Salesforce test tools still have upstream **deprecation notices**, such as the notice for `@lwc/engine-server`. These notices remain visible and are separate from security advisories. Do not run a forced major-version upgrade to clear a notice. If the audit reports vulnerabilities, stop and have Claude investigate; the checked baseline reported zero. Registry advisories can change after this pack is published. [npm audit](https://docs.npmjs.com/cli/v11/commands/npm-audit)

Confirm the full dependency audit, including development tools:

```text
npm audit
```

**Expected:** `found 0 vulnerabilities`. Next, test the component:

```text
npm run test:unit
```

**Expected:** one passing suite and **12 passing tests**, then the terminal prompt. The tests use synthetic responses for grouping, field choices, denied or missing data, the training cap, and refresh. They do not sign in to Salesforce or create records.

Check the dependency repair itself:

```text
node --test toolchain.test.cjs
```

**Expected:** **2 passing tests**, covering normal merging and rejection of unsafe prototype keys. Then check the JavaScript rules:

```text
npm run lint
```

**Expected:** the terminal returns without lint errors. The component keeps the production rules; the timer exception applies only to Jest tests.

If npm reports a missing `package.json` or script, check your terminal folder. If `npm ci` reports a manifest/lockfile mismatch, check that you copied both matching files; do not delete the lockfile as a shortcut. If Jest finds no tests, check the component's `__tests__` folder. Ask Claude to explain an error before changing versions, and keep `npm audit fix --force` out of the setup routine.

These checks establish the local baseline. Verify the deployed board and user access separately in the browser. [Install Jest](https://developer.salesforce.com/docs/platform/lwc/guide/unit-testing-using-jest-installation.html) · [Run Jest](https://developer.salesforce.com/docs/platform/lwc/guide/unit-testing-using-jest-run-tests.html)

## Preview, validate, and deploy the bundle

Finish the learning-org sign-in and identity check in [setup](setup.md#choose-and-verify-your-learning-org) and get passing local tests first. In the **lab** terminal, confirm the alias maps to your learning org. Use the installed CLI help for `sf project deploy preview`, `sf project deploy start`, and `sf project deploy report`. Each command below is a separate step.

**Preview the bundle.** Investigate unexpected files, deletes, name collisions, and conflicts. Developer Edition orgs do not support source tracking, so preview cannot establish whether you would overwrite an existing component. Ask Claude to check the target metadata for a name collision before deployment; do not treat a missing conflict report as an empty org. [Source tracking limits](https://developer.salesforce.com/docs/platform/sfdx-dev/guide/sfdx-setup-enable-source-tracking-sandboxes.html)

```text
sf project deploy preview --source-dir force-app/main/default/lwc/relatedActivityBoard --target-org sf-learning
```

**Validate in the learning org.** The dry run checks server deployment without saving the metadata. Wait for the job to finish. This is separate from the local Jest tests you just ran.

```text
sf project deploy start --dry-run --source-dir force-app/main/default/lwc/relatedActivityBoard --target-org sf-learning --api-version 68.0 --wait 10
```

**Expected after validation:** the command reaches terminal status `Succeeded` for `relatedActivityBoard`, with no deployment errors. If validation fails, stop here and ask Claude to explain the error. An operation still in progress is not success.

**Deploy after confirming the change and target.** Verify the alias again and apply the same bundle.

```text
sf project deploy start --source-dir force-app/main/default/lwc/relatedActivityBoard --target-org sf-learning --api-version 68.0 --wait 10
```

**Expected after deployment:** status `Succeeded` for the same bundle. You still need to place it on a page; deploying the files does not create a tab automatically.

If a command returns before the job finishes, substitute its ID for `DEPLOY_JOB_ID` and check the result before trying another deployment.

```text
sf project deploy report --job-id DEPLOY_JOB_ID --target-org sf-learning --wait 10
```

[Preview](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_preview.html) · [Validate and deploy](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_start.html) · [Report job status](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_report.html)

## Create practice records and open the board

1. In the practice org, open **Cases** from the App Launcher and create a Case with Subject **Practice delivery question**. Choose a Priority you can recognize and fill the required fields. In **Tasks**, create **Practice: check sample case**, assigned to yourself, with **Related To** set to that Case. Create **Practice: prepare follow-up**, also assigned to yourself, with Related To blank. Choose two available Task statuses. Use only fictional data. Existing sample Tasks can also appear: this board reads up to 50 visible Tasks, not just the two you created.
2. In **Setup → Lightning App Builder**, create an **App Page** named **Practice Activity Board** with a single region. Drag **Related Activity Board** from Custom Components. For a keyboard-friendly alternative, select **Add Component(s) Here** in the empty region, then select **Related Activity Board** in the component list. Use its labeled checkboxes to choose Case number, status, and priority; verify each checkmark changes. Save and select **Activation**. On **Page Settings**, choose **Activate for system administrators only** for this first rehearsal; the initial default can be all users. On **Lightning Experience**, select a suitable learning app (for example, Sales), select **Add page to app**, then save. Confirm the activation succeeds. Return to that app and select **Practice Activity Board** from its navigation menu; refresh the browser if it is not listed yet. Add the same app/page access for the second user when you do the permission exercise. Use a dedicated learning app or pilot assignment where available. [Lightning App Page setup](https://trailhead.salesforce.com/content/learn/modules/lightning_app_builder/lightning_app_builder_apphome) · [App Builder properties](https://developer.salesforce.com/docs/platform/lwc/guide/targets-lightning-app-page.html)
3. In Lightning Experience, confirm the Tasks are in the right columns, the counts match, and the Task and related record buttons open the expected records. Enable **Show case priority** and confirm the allowed user sees the synthetic value. Disable it, save the page, and confirm the field row goes away. Re-enable it for the permission check. Change a synthetic Task’s status from its regular record page and select **Refresh** on the board. The card should move to the new column.

The board is read-only: move a Task by changing its Status on the standard record page, then refresh. It does not implement drag-and-drop.

## Check access with a second user

Your first working screen is a useful checkpoint. A practice org may lack a spare suitable user license. If so, keep the actual-user permission checks pending and continue learning locally; they remain required before a production release. Do not change your own admin profile or grant broad access to manufacture a passing test.

Use a dedicated non-admin training user and a narrowly scoped permission set. Preserve existing users, profiles, and sharing defaults. Have Claude help with these steps after you confirm the target and changes:

1. Start with a minimum-access profile. Check **Object Manager → Case → Page Layouts → Page Layout Assignment**, and the equivalent Task assignment, for this user's profile and record type. A profile can have record access without a usable layout. If a shared profile needs changes, use a dedicated test profile rather than changing other users' experience. [Minimum Access layout troubleshooting](https://help.salesforce.com/s/articleView?id=005299592&language=en_US&type=1)
2. Grant the test user Lightning Experience, the practice app/tab, Case Read, and the optional fields needed for the example: **Case Subject**, **Task Related To**, and **Task Due Date**. Keep **Case Priority** unreadable initially. Case Number and Status aren't configurable FLS fields in the checked API 68.0 schema. Grant only the exercise's access; inspect the profile, every permission set, and any groups for additional grants. Task access follows activity ownership, sharing, and activity permissions. Do not try to create an `ObjectPermissions` Read grant for Task as if it were Case. [Activity access](https://help.salesforce.com/s/articleView?id=sales.activities_view.htm&language=en_US&type=5) · [Tab settings](https://help.salesforce.com/s/articleView?id=permissions_tab_settings_ref.htm&language=en_US)
3. As the administrator, create a fictional Case-related Task and an unrelated Task owned by the test user. Keep a separate fictional, unrelated Task owned by the administrator and unshared with the test user for the record-denial check. Confirm the actual sharing behavior; do not change org-wide sharing defaults to force a result.
4. Open the board in the training user's session or use Salesforce's supported **Login** action. Confirm the user's identity. If Login isn't available, use an approved individual login grant or have the user sign in. The org-wide **Administrators Can Log in as Any User** setting needs the owner's explicit approval; record its original value and restore it after testing. [Administrator login access](https://help.salesforce.com/s/articleView?id=004333094&language=en_US&type=1)
5. Leave **Show case priority** enabled in App Builder. The restricted user should see permitted Case details without the Priority row. Grant Case Priority Read in the isolated test permission set, reopen or refresh the board, and confirm its known value appears. Remove that grant and confirm it disappears again. Verify effective access after each change; hiding a row with the App Builder checkbox alone is not an FLS test. Also open the permitted Task and Case from their cards and confirm the standard record pages work.
6. For the object-denial check, remove Case Read from the isolated test permission set and confirm no other assignment grants it. Reopen and refresh the board. Tasks the user owns should remain usable, while Case details and the Case subject label disappear; the board shows its unavailable-details notice. Opening the remaining generic parent link must not grant access. For the separate record-sharing check, confirm the administrator's unshared Task is absent from the board and cannot be opened by its direct record URL. Activity access can also remove Tasks related to an inaccessible parent; compare with standard Salesforce for the same user. [Field permissions](https://help.salesforce.com/s/articleView?id=sf.users_profiles_field_perms.htm&type=5)

When finished, log out of the test session, revoke temporary assignments, deactivate a disposable training user, and remove only the temporary synthetic records you created with the org owner's authorization. Restore any temporary login policy. Keep the original learning board and baseline records if you plan to continue using them.

### Observed permission checks

The published component passed this browser rehearsal in a Winter ’27 / API 68.0 Developer Edition org on **November 12, 2026**. The dedicated test user had no administrative, View All Data, or Modify All Data grant. Its actual assignments and the rendered results were checked separately.

| Check | Observed result |
|---|---|
| Case Priority denied, display checkbox enabled | Permitted Case number/status remained; Priority was absent |
| Same user granted Case Priority, then grant removed | Priority appeared, then disappeared again |
| Case object access removed | The user's two Tasks remained; Case values and subject label disappeared; refresh preserved the safe result |
| Denied Case opened through the remaining parent link | Salesforce rejected access |
| Administrator's private unrelated Task | Absent from the board; direct navigation was rejected |
| Permitted Task and Case links | Standard record pages opened after correcting the test profile's layout assignments |

Case record sharing was permissive in that rehearsal, so the individual-record denial used a private Task; Case **object** denial was tested independently. This is evidence for the supplied example and that tested configuration. Your production audience, record types, sharing rules, and schema still need their own checks. The temporary user was deactivated, its permission assignment revoked, its extra Tasks removed, and the login policy restored. No component-code change was needed for these checks.

Check the learning org’s API 68.0 GraphQL schema for the intended viewers. Confirm `Task`, its optional `WhatId` field, and the related Case fields the board uses. Salesforce builds the schema from the user’s permissions and supported objects. The board reads the direct Related To ID without expanding the polymorphic `Task.What` relationship. The separate Case query can omit inaccessible rows or fields without removing Task cards; an actual query error or missing Case connection shows a notice. An absent Case row can also mean the parent is a different object type. A dry run checks metadata deployment. Verify the actual board with the two users to check the queries and access. [GraphQL schema and record access](https://developer.salesforce.com/docs/platform/graphql/guide/query-record-objects.html) · [Polymorphic relationships](https://developer.salesforce.com/docs/platform/graphql/guide/filter-polymorphic.html) · [GraphQL query command](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_api_request_graphql.html)

## Small build lessons to keep

The checked dependencies contain three scoped repairs: Babel core 7.29.13, minimatch 11.0.8 for affected versions, and `@stackline/deepmerge` 1.1.2 in Jest's configuration reader. The merge replacement blocks the unsafe key before reading either input. `toolchain.test.cjs` resolves the dependency from Jest itself and checks that behavior, as well as ordinary merging. The original upstream merge package had no patched release when this pack was checked. [Babel advisory](https://github.com/advisories/GHSA-4x5r-pxfx-6jf8) · [minimatch advisory](https://github.com/advisories/GHSA-g3hv-75wg-m249) · [Merge advisory](https://github.com/advisories/GHSA-gcqx-w48m-w2h4) · [Replacement source](https://github.com/alexandroit/stackline-deepmerge)

When upgrading later, review the manifest and lockfile changes together, repeat the five commands above, and check the current upstream advisories. The lockfile preserves a tested install; the live audit detects newly reported problems.

- The test-tool versions are pinned because a newer LWC engine was hoisted into an incompatible Jest runtime during verification. Keep the lockfile, and check compiler, engine, and Jest compatibility together before upgrading. An install that succeeds does not prove the tests can run.
- A minimum-access user could load the Case header but its standard Details panel failed because the profile had no Case layout assignment. Assigning existing Case and Task layouts to a dedicated test profile fixed navigation without widening data permissions. Check layouts separately from object and field access.
- Public Boolean properties start as `false` in JavaScript. The preferred App Builder values belong in the component's XML settings. This avoids a compiler/configuration failure and keeps the controls switchable. [Salesforce Boolean properties](https://developer.salesforce.com/docs/platform/lwc/guide/js-props-boolean.html)
- A query that worked against an empty org failed after practice Tasks were added during the live rehearsal. Expanding the broad `Task.What` polymorphic relationship produced a Salesforce complex-field error. Reading `WhatId` and fetching Case fields separately resolved that observed failure. Always test with actual records; a deployment and mocked tests cannot prove live query behavior. Parent navigation uses the standard record page, which accepts a record ID without an object API name in Lightning Experience. [Record page navigation](https://developer.salesforce.com/docs/platform/lwc/guide/reference-page-reference-type.html)
- A successful GraphQL refresh can return without another callback when the data is unchanged. The live walkthrough caught a bug that erased Case details before that refresh. The board now hides cards while refreshing, retains confirmed unchanged values, and clears details on a changed parent or failed read. Its tests cover both unchanged success and failure.
- A query can return useful data and errors together. Preserve permitted Task cards when the separate Case-details query fails, show a useful notice, and clear old details when the parent changes or a refresh fails. The bundled tests keep these failure cases visible.

## If the board does not look right

| Symptom | Check with Claude |
|---|---|
| Related Activity Board is missing from Custom Components | Confirm deployment succeeded in this org and that you created an **App Page**, the supported page type; refresh App Builder |
| The page is saved but there is no tab | Reopen Activation, confirm its Lightning app assignment, then open that app's navigation menu |
| The board has no cards | Create the synthetic Tasks and check that the same user can open them in standard Tasks; select Refresh |
| Cards appear but Case rows do not | Select the board in App Builder, enable the desired Case fields, save, and refresh; check the Task's Related To and actual Case/field access |
| The old behavior remains immediately after redeploying | Salesforce can cache a component version for up to ten minutes. Confirm the deployment and target, then allow the cache to expire and reload. For repeated development, use per-user Debug Mode in the learning org; the general Session Settings cache switch does not control this HTTP cache. [Component caching](https://developer.salesforce.com/docs/platform/lwc/guide/debug-http-caching.html) |
| A loading or query error persists | Keep the error distinct from an empty board. Have Claude inspect the actual GraphQL response and this user's schema using the reference above; share only sanitized error details |

## Save and adapt the baseline

Use **File → Save All** in the lab. Keep the DX source, local tests, and generated `package-lock.json` together. Ask Claude to update the lab's existing `README.md` with the completed steps, test result and any pending org/user checks so you can resume. The learning baseline is complete when local tests pass, deployment succeeds, the app page shows the synthetic Tasks, its field controls and links work, and Refresh reflects a Task change. Actual-user access checks must either be observed or explicitly listed as pending. Do not label an untested check as passed. Record the CLI and API versions, bundle path, learning alias, page assignment, and outcomes you observed. To undo the exercise, remove its app page assignment before removing any bundle metadata. Remove only the synthetic data and exercise access you added, with the org owner’s authorization.

For guided practice after this baseline, use [Make the board your own](../../../../NEXT-STEPS.md). Start with the existing records and App Builder controls, then make one small code change before planning an extension.

For another Task parent, inspect the actual object and its supported fields and confirm that it allows activities. The board can link using a returned Related To ID, and the packaged extra fields and parent subject label are specific to accessible Cases. Other parent types use a generic link label when no display label is returned. To add details for a different parent, verify the relationship and schema for the intended users. Add a fixed, scoped batch read and explicitly chosen fields to the card configuration, then test absent, allowed, and denied results. To board a different card object, choose that object’s scope, grouping field, and permissions as a separate design choice. [Enable activities for a custom object](https://help.salesforce.com/s/articleView?id=000385007&language=en_US&type=1)

Before relying on the board for a complete workload view, implement and test paging or agree on and test a business filter whose bounded scope meets the need. Follow [production readiness](production-readiness.md) before proposing a release.
