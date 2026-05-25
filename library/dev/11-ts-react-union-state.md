# React Union State

**Language(s):** TypeScript / React

**Rework-prevention rationale:** Prevents defensive accumulation by replacing optional-prop component state, which creates impossible render combinations, with mutually exclusive states that the compiler enforces.

**Canonical source:** Microsoft, *TypeScript Handbook*, "Discriminating Unions"; React Team, *React Documentation*, "Conditional Rendering" (react.dev); Matt Pocock, "TypeScript Discriminated Unions for Frontend Developers" (totaltypescript.com).

## Trigger condition

Halt and read this entry when defining React component state with optional `loading`, `data`, `error`, `empty`, or `status` fields that can form impossible combinations.

## Before

```tsx
type ViewState = {
  loading?: boolean;
  data?: User;
  error?: Error;
};

// Impossible: loading=true AND data=user AND error=someError simultaneously valid to TS
function ProfileView({ state }: { state: ViewState }) {
  if (state.loading) return <Spinner />;
  if (state.error)   return <ErrorBanner error={state.error} />;
  return state.data ? <Profile user={state.data} /> : null;   // null case unhandled
}
```

## After

```tsx
type ViewState =
  | { status: "loading" }
  | { status: "ready";  data: User }
  | { status: "error";  error: Error }
  | { status: "empty" };

function ProfileView({ state }: { state: ViewState }) {
  switch (state.status) {
    case "loading": return <Spinner />;
    case "ready":   return <Profile user={state.data} />;   // data guaranteed
    case "error":   return <ErrorBanner error={state.error} />;
    case "empty":   return <EmptyState />;
  }
}
```

**What discriminated union state prevents:**
- `data` accessed when `loading` is still true (runtime error)
- `error` branch missing because `data` was truthy (silent wrong render)
- New status added without updating the render: compiler flags the missing case

**Relationship to entry 10:** entry 10 covers TypeScript-wide discriminated unions; this entry is specifically about React component view state and render exhaustiveness.
