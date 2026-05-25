# Lazy Generator Streams

**Language(s):** Python

**Rework-prevention rationale:** Prevents complexity underestimation by stopping the agent from eagerly materializing large, one-shot, or I/O-backed data into a list when the consumer can process items one at a time.

**Canonical source:** Brett Slatkin, *Effective Python, Third Edition*, items on comprehensions, generators, and iteration; David Beazley and Brian K. Jones, *Python Cookbook, Third Edition*, Chapter 4, "Iterators and Generators."

## Trigger condition

Halt and read this entry when about to build and return a list from a loop over a file, API page stream, database cursor, log, or any potentially large iterable.

## Before

```python
def read_events(path: str) -> list[dict]:
    rows = []
    for line in open(path, encoding="utf-8"):   # file handle never closed
        rows.append(json.loads(line))
    return rows                                  # entire file in memory before any processing
```

## After

```python
def iter_events(path: str) -> Iterator[dict]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            yield json.loads(line)

for event in iter_events(path):
    handle(event)
```

**Decision rule:** Use a generator when:
- The consumer processes items one at a time (loop, filter, accumulator)
- The data source is I/O-backed (file, API, cursor) or potentially unbounded
- The caller does not need random access, length, sorting, or multiple passes

Use a list when:
- The caller needs `len()`, indexing, sorting, or iterating more than once
- The full result must be available before the first item is consumed

**Composing generators:**

```python
def parse_lines(path: str) -> Iterator[dict]:
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                yield json.loads(line)

def filter_errors(events: Iterator[dict]) -> Iterator[dict]:
    return (e for e in events if e.get("level") == "error")
```

Compose generators rather than building intermediate lists between pipeline stages.
