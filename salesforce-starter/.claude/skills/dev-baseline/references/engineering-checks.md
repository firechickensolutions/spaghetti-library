# Engineering checks

Read the relevant section when its trigger matches.

## Raw input and defensive branches

Convert external input into the shape the rest of the code expects at the point where it enters. Check required fields, accepted values, and constraints there. Downstream code still enforces business invariants, such as a permitted status transition. Recheck input shape when data crosses a new trust boundary.

Give each fallback a specific failure case. For a Salesforce wire adapter, loading, returned data, and a service error are real outcomes. A failed read should produce a helpful error state rather than look like an empty successful result. Give the learner sanitized details for troubleshooting. [Alexis King, “Parse, don’t validate”](https://lexi-lambda.github.io/blog/2019/11/05/parse-don-t-validate/) · [John Ousterhout, *A Philosophy of Software Design*](https://web.stanford.edu/~ouster/cgi-bin/book.php)

## Speculative abstractions

A direct call is a good starting point for one component. Add an interface or shared helper when multiple real consumers share the same contract, or when a defined integration boundary requires it. Keep data, decisions, and effects easy to trace. Give a meaningful condition a name if understanding it would otherwise require tracking several flags at once. [Sandi Metz, “The Wrong Abstraction”](https://sandimetz.com/blog/2016/1/20/the-wrong-abstraction)

## Safety and denial

Use a synthetic fixture with a known value. Show an allowed user can read it, then run the same flow as an actual restricted user who can reach the relevant screen. Assert that the protected value is absent while the allowed part still works. Test object and record denial separately when the feature relies on those controls. Use the application’s normal identity and path. A mocked UI test can cover rendering and error states. The deployed permission test establishes what the real user can access. [Barr et al., “The Oracle Problem in Software Testing”](https://doi.org/10.1109/TSE.2014.2372785)

## Writes, failures, and recovery

Before a write, identify what might already exist and what confirms success. A timeout can leave the remote action running. Look up the existing operation before sending it again. Where retrying can duplicate records or charges, preserve the operation identity and use the system’s transaction, uniqueness, or idempotency mechanism. Report an unresolved outcome as pending or unknown, with a way to resume checking. Keep prior behavior and a recovery path for consequential changes.

*Adapted from Firechicken Solutions’ development guidance and the Spaghetti Library’s [code-generation patterns](https://github.com/firechickensolutions/spaghetti-library/tree/master/library/dev).*
