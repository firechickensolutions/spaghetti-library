# Cognitive Chunking Limits

**Language(s):** Cross-language

**Rework-prevention rationale:** Prevents complexity underestimation by forcing decomposition when generated code requires the reader to simultaneously track too many live concepts, flags, branches, or side effects — making agent errors invisible to a single-pass reviewer.

**Canonical source:** George A. Miller, "The Magical Number Seven, Plus or Minus Two: Some Limits on Our Capacity for Processing Information," *Psychological Review*, 1956 (the original; chunk count applies to working memory items, not lines of code); Dustin Boswell and Trevor Foucher, *The Art of Readable Code*, chapters on explaining variables, summary variables, and simplifying loops; Steve McConnell, *Code Complete, Second Edition*, sections on routine complexity and cognitive limits.

## Trigger condition

Halt and read this entry when a function accumulates many live booleans, nested branches, mutable side effects, optional values, or intermediate variables that cannot be named as a small coherent set of concepts.

## Before

```python
def sync(a, b, c, dry, retry, force, seen):
    if a and not b or c:
        seen.add(a)
        if not dry:
            result = push(a, retry, force)
            if result and not result.get("err"):
                log(a, result)
                return result
    return None
```

## After

```python
@dataclass(frozen=True)
class SyncRequest:
    source: str
    is_allowed: bool
    dry_run: bool

def sync(request: SyncRequest, seen: set[str]) -> Result | None:
    should_push = bool(request.source) and request.is_allowed
    if not should_push or request.dry_run:
        return None
    seen.add(request.source)
    return push_source(request)
```

**What Miller's Law means for code:** the 7 ± 2 limit applies to *chunks* in working memory, not lines of code. A chunk is a named, coherent unit a reader can reason about without holding its internals in mind simultaneously. A function that requires tracking 6+ live variables, 3 nested conditions, 2 mutable collections, and an optional return value exceeds the chunk budget — a reviewer cannot hold the full state in their head and catch an agent error in one pass.

**Explaining variables and summary variables (Boswell and Foucher):**
- *Explaining variable:* breaks a subexpression into a named step (`should_push = bool(source) and is_allowed`)
- *Summary variable:* condenses a broad logical criterion into a readable boolean flag

Both reduce chunk count without changing correctness. If you need a comment to explain what a block does, it should be a named function or variable instead.

**The AI generation failure mode:** agents generate "single-pass clever" functions — many live flags, accumulated intermediate state, and nested conditionals — then compensate with comments. The comments describe what the code does instead of decomposing the cognitive load.
