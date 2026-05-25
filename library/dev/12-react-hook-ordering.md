# Hook Ordering Rules

**Language(s):** React / TypeScript / JavaScript

**Rework-prevention rationale:** Prevents hook-order drift, stale closures, hidden stateful logic, and exceptional control-flow bugs by preserving React's required hook call graph across renders.

**Canonical source:** React Team, *React Documentation*, "Rules of Hooks" (react.dev/reference/rules/rules-of-hooks); React Team, *eslint-plugin-react-hooks Documentation*, `rules-of-hooks` and `exhaustive-deps` (react.dev/reference/eslint-plugin-react-hooks).

## Trigger condition

Halt and read this entry when about to call a React hook inside a condition, loop, nested function, event handler, `try`/`catch`/`finally`, after an early return, or with an incomplete dependency array.

## Before

```tsx
function Panel({ enabled }: { enabled: boolean }) {
  if (!enabled) return null;              // early return before hooks: rule violation
  const [open, setOpen] = useState(false);
  if (open) useEffect(syncPanel, []);     // hook inside condition: rule violation
  return <button onClick={() => setOpen(!open)} />;
}
```

## After

```tsx
function Panel({ enabled }: { enabled: boolean }) {
  const [open, setOpen] = useState(false);
  useEffect(() => {
    if (enabled && open) syncPanel();
  }, [enabled, open]);                    // full dependency array
  if (!enabled) return null;             // early return after all hooks
  return <button onClick={() => setOpen(!open)} />;
}
```

**The four sub-rules with rework rationale:**

| Rule | Failure mode prevented |
|---|---|
| No hooks inside conditions or loops | Render-count drift: React tracks hooks by call order; conditional calls desync the order |
| No hooks after an early return | Same: an early return makes hooks conditional on the return path |
| No hooks inside event handlers, nested functions, class components, or callbacks passed to `useMemo`/`useReducer`/`useEffect` | Stateful logic hidden outside React's render model; state updates do not trigger re-renders |
| No hooks inside `try`/`catch`/`finally` | Exceptional flow changes the hook call graph when an exception short-circuits a hook call |

**`exhaustive-deps`:** the `eslint-plugin-react-hooks/exhaustive-deps` rule validates dependency arrays. A missing dependency causes the effect or memo to close over a stale value silently, one of the most common React bugs in AI-generated components.
