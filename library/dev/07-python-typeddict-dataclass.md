# TypedDict vs Dataclass Boundary

**Language(s):** Python

**Rework-prevention rationale:** Prevents imaginary extensibility and defensive accumulation by distinguishing JSON-like boundary shapes (TypedDict) from Python-owned domain records (dataclass) instead of using plain dicts throughout or converting everything into classes.

**Canonical source:** Ivan Levkivskyi and contributors, *PEP 589 — TypedDict: Type Hints for Dictionaries with a Fixed Set of Keys* (peps.python.org/pep-0589); Eric V. Smith, *PEP 557 — Data Classes* (peps.python.org/pep-0557).

## Trigger condition

Halt and read this entry when a plain `dict` with fixed keys is being passed between functions, or when the agent is about to turn every structured value into a class without checking whether it is boundary JSON or a Python-owned domain record.

## Decision rule

| If the value... | Use |
|---|---|
| Arrives from or goes to JSON, an API, a config file, or a database row | `TypedDict` — stays a dict, serializes without conversion |
| Is a Python-owned domain record that benefits from construction, attribute access, equality, defaults, frozen semantics, or methods | `@dataclass` |

## Before

```python
def enqueue(job: dict) -> None:
    run_id = job["run_id"]        # no type safety, key typos silent at definition time
    retries = job.get("retries", 0)
    submit(run_id, retries)
```

## After — boundary payload (TypedDict)

```python
from typing import TypedDict

class JobPayload(TypedDict):
    run_id: str
    retries: int

def enqueue(job: JobPayload) -> None:
    submit(job["run_id"], job["retries"])   # key access is type-checked
```

## After — Python domain record (dataclass)

```python
from dataclasses import dataclass

@dataclass(frozen=True)
class Job:
    run_id: str
    retries: int = 0

def enqueue(job: Job) -> None:
    submit(job.run_id, job.retries)        # attribute access, immutable, equality built in
```

**Mixing:** parse a `JobPayload` dict at the API boundary, then convert to a `Job` dataclass inside the domain core. The boundary type and the domain type serve different masters.
