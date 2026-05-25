# State Colocation

**Language(s):** React / TypeScript / JavaScript

**Rework-prevention rationale:** Prevents premature abstraction and render-cascade drift by keeping state as close as possible to its consumer instead of lifting it into shared scope before multiple consumers actually need it.

**Canonical source:** Kent C. Dodds, "State Colocation will make your React app faster" (kentcdodds.com/blog/state-colocation-will-make-your-react-app-faster); Kent C. Dodds, "Application State Management with React."

## Trigger condition

Halt and read this entry when lifting React state to a parent component, context, store, or global module before confirming that two or more independent consumers need it.

## Before

```tsx
// Parent owns state that only SearchBox uses
function App() {
  const [draft, setDraft] = useState("");
  const [results, setResults] = useState<Result[]>([]);
  return (
    <>
      <SearchBox draft={draft} setDraft={setDraft} />
      <ResultList results={results} />
    </>
  );
}
// Any App re-render (from unrelated state) re-renders SearchBox and ResultList
```

## After

```tsx
// State lives where it is used
function App() {
  return (
    <>
      <SearchBox />
      <ResultList />
    </>
  );
}

function SearchBox() {
  const [draft, setDraft] = useState("");
  return <input value={draft} onChange={e => setDraft(e.target.value)} />;
}
```

**Decision rule:** State belongs in the lowest component that is the common ancestor of all components that read or write it. If only one component uses it, it stays in that component. Lift only when a second independent consumer appears.

**Common AI generation mistake:** the agent lifts all form state into the parent "for flexibility" before any child actually shares it. This creates prop drilling, unnecessary re-renders, and a global state dependency that is harder to remove later than it was to add.

**When to lift:** when two sibling components genuinely need to read or react to the same value. When to use context: when the same value is needed by deeply nested components across multiple branches of the tree. When to use a store: when state changes must be observed outside the component tree (persisted, synced, time-traveled).
