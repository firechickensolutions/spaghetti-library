# Exhaustive Union Handling

**Language(s):** TypeScript

**Rework-prevention rationale:** Prevents defensive accumulation and silent state drift by making every variant of an application state or API payload compile-time exhaustive, so adding a new variant forces the compiler to flag every unhandled path.

**Canonical source:** Microsoft, *TypeScript Handbook*, "Discriminating Unions" and "Exhaustiveness checking" (typescriptlang.org/docs/handbook); Basarat Ali Syed, *TypeScript Deep Dive*, "Discriminated Union."

## Trigger condition

Halt and read this entry when defining TypeScript state, action, API payload, or task objects using a string `status` field plus optional payload fields.

## Before

```ts
interface Task {
  status: string;          // open-ended string, no compiler help
  outputUri?: string;
  failureReason?: string;
}

function label(t: Task): string {
  return t.outputUri ?? t.failureReason ?? "pending";
  // silent: outputUri present on a "failed" task, or failureReason on "success"
}
```

## After

```ts
type Task =
  | { status: "pending" }
  | { status: "success"; outputUri: string }
  | { status: "failed"; failureReason: string; exitCode: number };

function assertNever(x: never): never {
  throw new Error(`Unhandled variant: ${JSON.stringify(x)}`);
}

function label(task: Task): string {
  switch (task.status) {
    case "pending":  return "queued";
    case "success":  return task.outputUri;          // outputUri guaranteed present
    case "failed":   return task.failureReason;      // failureReason guaranteed present
    default:         return assertNever(task);        // compiler flags if a variant is missing
  }
}
```

**Why `assertNever`:** the `default` branch with `assertNever` makes the exhaustiveness check explicit. If a new variant is added to `Task` and the `switch` is not updated, the compiler errors on the `assertNever(task)` call because `task` is no longer `never`.

**Optional fields create impossible states:** `{ isLoading?: boolean; data?: T; error?: Error }` allows `{ isLoading: true, data: user, error: new Error() }`: a state that cannot exist in the real system but is valid to the type checker. Discriminated unions eliminate the impossible combinations.
