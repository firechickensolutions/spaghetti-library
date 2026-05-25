# Sound TypeIs Narrowing

**Language(s):** Python

**Rework-prevention rationale:** Prevents defensive accumulation by letting a sound predicate narrow both the positive and negative branches of a closed union, eliminating duplicate `isinstance` checks, `hasattr` guards, and second-pass type tests.

**Canonical source:** Jelle Zijlstra, Carl Meyer, and contributors, *PEP 742, Narrowing types with TypeIs* (peps.python.org/pep-0742); Python Software Foundation, *typing documentation*, `typing.TypeIs`; mypy 1.10 release notes (mypy-lang.blogspot.com/2024/04/mypy-110-released.html).

## Trigger condition

Halt and read this entry when writing a boolean type predicate over a closed union where both the `if` and `else` branches need narrowing.

## Before

```python
def stage(value: LocalPath | RemoteUri) -> str:
    if isinstance(value, LocalPath):
        return value.path
    if isinstance(value, RemoteUri):   # redundant: union is already closed
        return value.uri
    raise TypeError("unknown location")  # unreachable, but agent adds it defensively
```

## After

```python
from typing import TypeIs

def is_local(value: LocalPath | RemoteUri) -> TypeIs[LocalPath]:
    return isinstance(value, LocalPath)

def stage(value: LocalPath | RemoteUri) -> str:
    return value.path if is_local(value) else value.uri
    # else branch: checker narrows to RemoteUri without casting
```

**Sound predicate requirement:** The predicate must not return `True` for values that do not satisfy the target type. The `all(isinstance(x, str) for x in items)` pattern is unsound: `all([])` returns `True` for an empty list of any element type. Use nominal `isinstance` over concrete classes.

**Else-branch narrowing:** works when the union is a closed two-member union and the predicate is an exact isinstance check. In wider unions, the else branch narrows to "not T," not automatically to a specific alternative; verify with mypy or pyright in those cases.

**Checker support (2025):** mypy 1.10+, pyright (TypeIs issue closed), pytype (PEP 742 issue closed). Confirm negative-branch behavior with a local type check before relying on it across all three checkers.

**Backport:** `from typing import TypeIs` (Python 3.13+) or `from typing_extensions import TypeIs` (earlier versions via typing-extensions 4.10+).
