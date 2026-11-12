# Permissions, Apex, and tests

Open this reference when Salesforce’s built-in UI or Lightning Data Service (LDS) cannot meet the requirement, or when the work changes access or introduces Apex.

## Keep access checks distinct

- **Page assignment and component visibility** determine where users see the card. Use Salesforce data controls to protect the records and fields behind it.
- **Object permissions** determine whether the user can create, read, update, or delete a type of record. **Field-level security (FLS)** controls which fields they can read or edit. **Record sharing** controls which individual records they can reach.
- For `@AuraEnabled` methods, a user also needs Apex class access from a profile or assigned permission set. Class access lets the user call the method. Keep object, field, and record checks in the method’s data path.
- For a permission metadata change, inspect the current permission set and its related metadata first. In standard source format it is `<package-directory>/main/default/permissionsets/<name>.permissionset-meta.xml`. Review `objectPermissions`, `fieldPermissions`, and `classAccesses` as applicable. Deploying partial permission set contents can disable omitted permissions. Review the full set and verify the effective access of the actual assignee after the change.

[Salesforce data access model](https://help.salesforce.com/s/articleView?id=platform.security_data_access.htm&type=5) · [Secure Apex classes](https://developer.salesforce.com/docs/platform/lwc/guide/apex-security.html) · [PermissionSet metadata](https://developer.salesforce.com/docs/platform/api-metadata/references/meta-types/metadata-permissionset.html)

## Debug permission failures before granting more access

These checks capture recurring lessons from building and repairing Salesforce features:

| What you see | What to check first |
|---|---|
| It works as an admin but fails for the intended user | Reproduce through the same page as that user. Check app/page access, object permissions, field permissions, and record sharing independently. Avoid fixing a narrow failure by granting administrator, View All, or Modify All access. |
| A field still appears after you omit it from one permission set | Access is additive. Review the profile, other permission sets, and permission set groups; omission from one grant does not revoke another grant. |
| The record header loads but its Details panel errors for a minimum-access user | Check the profile and record type’s page-layout assignment. Assign a suitable existing layout on a dedicated test profile if necessary; extra object or field grants do not repair a missing layout. |
| The component appears but its Apex call is denied | Check Apex class access separately from the records and fields the method reads. A visible component is not an authorization grant. |
| Existing access changes after a metadata deployment | Compare the complete permission set and dependencies with the target before deployment. A partial permission-set payload can remove omitted grants. Preserve and test the intended existing access. |
| Optional related fields disappear, or the entire query fails | Distinguish a field the user cannot read from a relationship or object absent from that user's schema. Inspect the actual response and schema; do not widen access just to make the query succeed. |

The [minimum-access layout issue](https://help.salesforce.com/s/articleView?id=005299592&language=en_US&type=1) was reproduced and repaired during this starter’s live permission rehearsal. Keep the failed case in the test or release notes with synthetic data so the same mistake is caught next time. The permission and schema checks above use the linked Salesforce documentation; the deployed-user exercise is the proof for the target org.

## Use the saved API version when reading Apex

Winter ’27 is **API 68.0**. In Apex compiled at API 67.0 and later, database operations default to user mode and classes without an explicit sharing declaration default to `with sharing`. Older API versions have different defaults. Inspect the class’s own `.cls-meta.xml`, especially in a project that mixes versions. A change to `sourceApiVersion` in the project alone does not change the versions at which existing classes were saved.

Make intent explicit. For a user-facing controller, use `with sharing` to express record-level sharing, and prefer `WITH USER_MODE` for user-scoped SOQL and the documented user-mode DML form for writes. `with sharing` covers record visibility. User-mode operations also enforce object and field permissions. For a graceful result with inaccessible fields removed, consider `Security.stripInaccessible` and verify the record-access design separately. Review data paths before recompiling older classes at 68.0. Legacy `WITH SECURITY_ENFORCED` queries no longer compile at 67.0 and later. Check queries, DML, and sharing assumptions as part of a targeted upgrade.

[Winter ’27 developer guide](https://developer.salesforce.com/blogs/2026/10/developers-guide-to-the-winter-27-release) · [Versioned Apex behavior changes](https://developer.salesforce.com/docs/platform/apex-dev/references/apex-dev/versioned-behavior-changes.html) · [Apex security and sharing model](https://developer.salesforce.com/docs/platform/apex-dev/references/apex-dev/apex-security-sharing-chapter.html)

Triggers have an implicit `without sharing` context. At API 67.0 and later, database operations in the trigger body still default to user mode, which enforces the user’s data access. At API 66.0 and earlier, those operations default to system mode. Prefer a handler for permission-sensitive work and specify the operation access mode explicitly. [Apex sharing keywords and triggers](https://developer.salesforce.com/docs/platform/apex-dev/references/apex-dev/apex-classes-keywords-sharing.html)

## Test behavior and transaction limits

Create synthetic records in the Apex test or its `@TestSetup` method. Rely on test data isolation and avoid `SeeAllData=true` for ordinary unit tests. Assert outcomes, including a real denied case when access is part of the requirement. Exercise the deployed entry point separately as the intended user and as a user with narrower access. An Apex test or Jest mock can prove its asserted behavior. The deployed-user check verifies the permission assignments and access paths of the actual org.

For Apex called on record batches, test more than one record in the same transaction. Collect IDs, query in sets, and perform collection DML outside record loops. Where Flow, triggers, and Apex share a transaction, budget for the combined work and verify the limit relevant to the action.

[Apex test data isolation](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_testing_data_access.htm) · [Apex governor limits](https://developer.salesforce.com/docs/atlas.en-us.apexcode.meta/apexcode/apex_gov_limits.htm)

*Adapted from Firechicken Solutions’ Salesforce engineering guidance. The linked official documentation supplies the release and API behavior.*
