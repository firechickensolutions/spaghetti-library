# Signature Pressure Relief

**Language(s):** Python

**Rework-prevention rationale:** Prevents premature abstraction and defensive accumulation by replacing long positional signatures, which callers cannot safely read or reorder, with explicit named contracts.

**Canonical source:** Dustin Boswell and Trevor Foucher, *The Art of Readable Code*, Chapter 3 "Names That Can't Be Misconstrued" and Chapter 7 "Making Control Flow Easy to Read"; David Beazley and Brian K. Jones, *Python Cookbook, Third Edition*, recipes on keyword-only arguments.

## Trigger condition

Halt and read this entry when defining or modifying a function with four or more positional parameters.

## Before

```python
def deploy(name, path, env, dry_run, retries):
    if dry_run:
        return preview(name, path, env, retries)
    return apply(name, path, env, retries)
```

## After: parameter object (preferred when fields travel together)

```python
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class DeployRequest:
    name: str
    path: Path
    env: str
    dry_run: bool = False
    retries: int = 3

def deploy(request: DeployRequest) -> Result:
    if request.dry_run:
        return preview(request)
    return apply(request)
```

## After: keyword-only (preferred for independent scalar flags)

```python
def deploy(name: str, path: Path, *, env: str, dry_run: bool = False, retries: int = 3) -> Result:
    ...
```

**Resolution guide:**

| Condition | Resolution |
|---|---|
| Parameters form a coherent record that travels as a unit | `@dataclass` parameter object |
| Parameters are independent scalars and callers name them explicitly | Keyword-only (`*` separator) |
| Parameters are a JSON-like payload from an external boundary | `TypedDict` (see entry 07) |
| Parameters are a forwarded open-ended call | `**kwargs`: only for genuine forwarding |

**Never use `*args`/`**kwargs` to "solve" a long signature.** It hides the contract rather than fixing it. The agent's instinct to add `**kwargs` for "flexibility" is the failure mode this entry prevents.
