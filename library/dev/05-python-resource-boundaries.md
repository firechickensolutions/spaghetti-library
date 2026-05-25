# Resource Lifetime Boundaries

**Language(s):** Python

**Rework-prevention rationale:** Prevents untestable coupling and complexity underestimation by making resource acquisition and cleanup structurally paired instead of relying on fragile `try/finally` paths that break silently under later edits.

**Canonical source:** Python Software Foundation, *Python Standard Library Documentation*, `contextlib` (docs.python.org/3/library/contextlib.html); Brett Slatkin, *Effective Python, Third Edition*, item on `contextlib` and reusable `with` behavior.

## Trigger condition

Halt and read this entry when about to acquire a file, lock, transaction, temporary directory, environment mutation, subprocess, or any external resource that must be released.

## Before

```python
lock.acquire()
try:
    write_manifest(path, data)
finally:
    lock.release()   # silently dropped if a later edit restructures the try block
```

## After

```python
# Built-in context managers handle acquire/release structurally
with lock:
    write_manifest(path, data)

with open(path, "w", encoding="utf-8") as f:
    f.write(payload)

with tempfile.TemporaryDirectory() as tmp:
    process(tmp)
```

**Custom context managers via `contextlib.contextmanager`:**

```python
from contextlib import contextmanager

@contextmanager
def managed_connection(dsn: str):
    conn = connect(dsn)
    try:
        yield conn
    finally:
        conn.close()

with managed_connection(dsn) as conn:
    conn.execute(query)
```

**When `try/finally` is still correct:** when the cleanup is genuinely conditional or cannot be modeled as a symmetric enter/exit. In all other cases, `with` makes the boundary explicit and prevents the agent from omitting the release on refactor.
