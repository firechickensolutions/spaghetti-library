# Structural Protocols

**Language(s):** Python

**Rework-prevention rationale:** Prevents interface-with-one-implementation and imaginary extensibility by replacing nominal inheritance hierarchies with structural contracts that only declare polymorphism when it is actually needed.

**Canonical source:** Guido van Rossum, Jukka Lehtosalo, and Łukasz Langa, *PEP 544, Protocols: Structural subtyping (static duck typing)* (peps.python.org/pep-0544); Brett Slatkin, *Effective Python, Third Edition*, item on accepting functions and simple interfaces before classes.

## Trigger condition

Halt and read this entry when about to write `from abc import ABC`, `@abstractmethod`, or an interface/base class with only one known implementation.

## Before

```python
from abc import ABC, abstractmethod

class Archiver(ABC):
    @abstractmethod
    def archive(self, files: list[str]) -> bool: ...

class DiskArchiver(Archiver):
    def archive(self, files: list[str]) -> bool:
        return True
```

## After

```python
from typing import Protocol

class Archiver(Protocol):
    def archive(self, files: list[str]) -> bool: ...

# DiskArchiver needs no import of Archiver; structural match is implicit
class DiskArchiver:
    def archive(self, files: list[str]) -> bool:
        return True

def run_archive(archiver: Archiver, files: list[str]) -> None:
    archiver.archive(files)
```

**When ABC is still correct:** use `abc.ABC` when you need enforced method registration, shared mixin state, or `register()` for virtual subclasses. For pure type contracts with no shared implementation, Protocol is always preferable.

**`@runtime_checkable`:** add only when `isinstance()` checks against the protocol are needed at runtime. Without it, Protocol is a static-only contract with no runtime cost.
