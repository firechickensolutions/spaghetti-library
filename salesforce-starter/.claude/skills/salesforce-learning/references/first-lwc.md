# Deploy the Related Activity Board

Imagine a service team that needs to see follow-up Tasks by status and know which Case each Task is about. Standard Salesforce Kanban is based on a single list view and shows up to four fields on a card. The supplied board uses the same column-and-card pattern on its own **Lightning App Page**. Opening a card or related record takes the user to the usual Salesforce record page. The board itself performs read-only queries. [Salesforce Kanban configuration](https://help.salesforce.com/s/articleView?id=xcloud.kanban_configuration.htm&language=en_US&type=5) · [Kanban display limits](https://help.salesforce.com/s/articleView?id=kanban_considerations_admin.htm&language=en_US&type=5)

In a real design, first check whether an existing view or configuration meets the need. A cross-object formula can expose a related value to users who can’t open the parent record. Use one only when that exposure is intended. This sample reads related records as the signed-in user. [Cross-object formula access](https://help.salesforce.com/s/articleView?id=fields_creating_cross_object_advanced.htm&language=en_US&type=5)

## Copy the example into your project

Complete [setup](setup.md) first. In VS Code Explorer, open the DX project that contains `sfdx-project.json`. Copy the entire [relatedActivityBoard](../assets/relatedActivityBoard/) folder into `force-app/main/default/lwc`. Create the `lwc` directory if it’s missing. If your package directory differs, substitute it in the path and commands. Check that the board name is fresh in the project and learning org before copying or deploying.

Keep Claude open in the starter folder and ask it to inspect the copied component in the DX project. Have it explain the HTML and CSS that lay out the board, the JavaScript that reads and groups records, the XML that exposes the board and its settings in App Builder, and the Jest file that tests the user-visible behavior. Use the supplied source as your baseline.

The board queries the **first 50 Tasks visible to the signed-in user**, sorted by Status and record ID, and groups the results into columns. The counts reflect loaded cards. A notice appears if more Tasks are available. This view uses its own query and scope. The two read queries fetch Tasks and their permitted Related To links, then request optional Case details in one batch for the visible Case IDs. The batch may return fewer details than requested and the Task cards remain useful in that case. [GraphQL record and optional-field behavior](https://developer.salesforce.com/docs/platform/graphql/guide/query-record-objects.html) · [Task and Event API support](https://developer.salesforce.com/docs/platform/graphql/guide/query-limits.html)

## Preview, validate, and deploy the bundle

From the folder with `sfdx-project.json`, confirm the alias maps to your learning org. Use the installed CLI help for `sf project deploy preview`, `sf project deploy start`, and `sf project deploy report`. Each command below is a separate step.

**Preview the bundle.** Investigate unexpected files, deletes, name collisions, and conflicts. Some learning orgs lack source tracking. Check the target’s existing metadata if preview can’t show conflicts.

```text
sf project deploy preview --source-dir force-app/main/default/lwc/relatedActivityBoard --target-org sf-learning
```

**Validate in the learning org.** The dry run checks server deployment without saving the metadata. Wait for the job to finish. The LWC’s Jest tests run locally in a later step.

```text
sf project deploy start --dry-run --source-dir force-app/main/default/lwc/relatedActivityBoard --target-org sf-learning --api-version 68.0 --wait 10
```

**Deploy after confirming the change and target.** Verify the alias again and apply the same bundle.

```text
sf project deploy start --source-dir force-app/main/default/lwc/relatedActivityBoard --target-org sf-learning --api-version 68.0 --wait 10
```

If a command returns before the job finishes, substitute its ID for `DEPLOY_JOB_ID` and check the result before trying another deployment.

```text
sf project deploy report --job-id DEPLOY_JOB_ID --target-org sf-learning --wait 10
```

[Preview](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_preview.html) · [Validate and deploy](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_start.html) · [Report job status](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_project_deploy_report.html)

## See the board as two users

1. Create a synthetic Case with a distinguishable value in **Priority** and at least two synthetic Tasks in different statuses. Set one Task’s **Related To** field to the Case. Leave the other Task’s Related To blank. Use the statuses and required fields available in the learning org.
2. In **Setup → Lightning App Builder**, create an **App Page** named **Practice Activity Board** with a single region. Drag **Related Activity Board** from Custom Components. Use its settings to choose Case number, status, and priority. Save, activate, and add the page to an app available to your two test users. Use a dedicated learning app or pilot assignment where available. [Lightning App Page setup](https://trailhead.salesforce.com/content/learn/modules/lightning_app_builder/lightning_app_builder_apphome) · [App Builder properties](https://developer.salesforce.com/docs/platform/lwc/guide/targets-lightning-app-page.html)
3. In Lightning Experience, confirm the Tasks are in the right columns, the counts match, and the Task and related record buttons open the expected records. Enable **Show case priority** and confirm the allowed user sees the synthetic value. Disable it, save the page, and confirm the field row goes away. Re-enable it for the permission check. Change a synthetic Task’s status from its regular record page and select **Refresh** on the board. The card should move to the new column.
4. Use a non-admin test user who can reach the app, Task, and Case, with effective Case Status read access and **no** Case Priority read access. If a suitable license is available, use a dedicated training user with a minimal profile and narrowly scoped access. Check the combined profile, permission sets, and groups. Open the same board in that user’s browser session or use Salesforce’s supported **Login** action for the training user. The Task and permitted Case details should remain, while Case Priority is absent. If Priority’s field permission can’t be narrowed for this user, record the field check as pending or adapt the board to a field you can verify. Check an inaccessible Case or an omitted parent separately. Salesforce’s activity access rules can also hide the Task itself. Compare with what the same user can open through standard Salesforce. Record any untested case as pending. [Field permissions](https://help.salesforce.com/s/articleView?id=sf.users_profiles_field_perms.htm&type=5) · [Activity access](https://help.salesforce.com/s/articleView?id=sales.activities_view.htm&language=en_US&type=5)

Check the learning org’s API 68.0 GraphQL schema for the intended viewers. Confirm `Task`, the `Task.What` relationship, and the related record fields the board uses. Salesforce builds the schema from the user’s permissions and supported objects. If `Task.What` is absent, the Task query can fail even with `@optional` and needs to be adapted to that schema. When the Task query succeeds, the separate Case query can fail or omit data and the Task cards remain visible with a notice. A dry run checks metadata deployment. Verify the actual board with the two users to check the queries and access. [GraphQL schema and record access](https://developer.salesforce.com/docs/platform/graphql/guide/query-record-objects.html) · [Polymorphic relationships](https://developer.salesforce.com/docs/platform/graphql/guide/filter-polymorphic.html) · [GraphQL query command](https://developer.salesforce.com/docs/platform/salesforce-cli-reference/guide/cli_reference_api_request_graphql.html)

## Run the bundled local tests

From the DX project folder, check `node --version` and `npm --version`. The standalone Salesforce CLI has its own Node runtime. For the local tests, install a current supported patch of [Node.js 24 LTS](https://nodejs.org/en/download) and use it in your shell. The sample was tested with Node.js 24.12.0 and the pinned Jest and LWC engine versions below. Use `npm.cmd` in place of `npm` if PowerShell blocks the npm script shim.

Run the install once in the new DX project and keep the resulting lockfile. The standard project template provides the `test:unit` script and Jest config. Check that `.forceignore` excludes local tests with `**/__tests__/**`.

```text
npm install --save-dev --save-exact @salesforce/sfdx-lwc-jest@7.9.0 @lwc/engine-dom@8.28.2 --ignore-scripts
```

```text
npm run test:unit
```

The supplied tests use synthetic wire data for grouping, field choices, missing or denied data, the training cap, and refresh. Verify org access separately in the browser. [Install Jest](https://developer.salesforce.com/docs/platform/lwc/guide/unit-testing-using-jest-installation.html) · [Run Jest](https://developer.salesforce.com/docs/platform/lwc/guide/unit-testing-using-jest-run-tests.html)

## Small build lessons to keep

- The test-tool versions are pinned because a newer LWC engine was hoisted into an incompatible Jest runtime during verification. Keep the lockfile, and check compiler, engine, and Jest compatibility together before upgrading. An install that succeeds does not prove the tests can run.
- Public Boolean properties start as `false` in JavaScript. The preferred App Builder values belong in the component's XML settings. This avoids a compiler/configuration failure and keeps the controls switchable. [Salesforce Boolean properties](https://developer.salesforce.com/docs/platform/lwc/guide/js-props-boolean.html)
- A query can return useful data and errors together. Preserve permitted Task cards when the separate Case-details query fails, show a useful notice, and clear stale details before retrying. The bundled tests keep these failure cases visible.

## Save and adapt the baseline

Keep the DX source, local tests, and dependency lockfile together. Record the CLI and API versions, bundle path, learning alias, page assignment, and outcomes you observed. To undo the exercise, remove its app page assignment before removing any bundle metadata. Remove only the synthetic data and exercise access you added, with the org owner’s authorization.

For another Task parent, inspect the actual object and its supported fields and confirm that it allows activities. The board can link to a returned Related To record, and the packaged extra fields are specific to Case. To add details for a different parent, verify the relationship and schema for the intended users. Add a fixed, scoped batch read and explicitly chosen fields to the card configuration, then test absent, allowed, and denied results. To board a different card object, choose that object’s scope, grouping field, and permissions as a separate design choice. [Enable activities for a custom object](https://help.salesforce.com/s/articleView?id=000385007&language=en_US&type=1)

Before relying on the board for a complete workload view, implement and test paging or agree on and test a business filter whose bounded scope meets the need. Follow [production readiness](production-readiness.md) before proposing a release.
