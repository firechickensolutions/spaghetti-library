"""Render a D28 extraction into the capture note.

The transcript note is written first by the sink and is never at risk; this
module *enriches* an existing note in place — it inserts a Summary + the
non-empty taxonomy sections above the transcript and stamps the frontmatter
`extraction: complete`. If extraction never runs (Ollama down), the note simply
stays transcript-only and the caller degrades gracefully.

Atomic rewrite (temp + os.replace): a crash mid-enrich leaves the original
transcript note intact, never a truncated file.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

from thought_capture.schema import SECTION_ORDER, ThoughtExtraction

_SECTION_TITLES = {
    "threads": "Threads",
    "claims": "Claims",
    "decisions": "Decisions",
    "open_questions": "Open questions",
    "actions": "Actions",
    "artifacts": "Artifacts",
    "links": "Links",
}

_TRANSCRIPT_ANCHOR = "## Transcript\n"


def _sanitize(s: str) -> str:
    """Collapse all whitespace (including newlines) to single spaces.

    Extraction content is model output; without this a summary or item
    containing a newline + "## " or "---" could forge a markdown header or a
    frontmatter fence in the note. Collapsing newlines makes that impossible —
    an extraction value is always one clean inline string."""
    return " ".join(s.split()).strip()


def _split_frontmatter(text: str) -> tuple[str, str]:
    """Return (frontmatter_body, rest). `frontmatter_body` is the content
    between the opening and closing `---` fences (no fences); `rest` is the
    note body after the closing fence. No frontmatter -> ("", text)."""
    if not text.startswith("---\n"):
        return "", text
    end = text.find("\n---\n", 4)
    if end == -1:
        return "", text
    return text[4:end], text[end + len("\n---\n") :]


def frontmatter_value(text: str, key: str) -> str | None:
    """Read a top-level scalar value from the note's YAML frontmatter, or None.

    Deliberately tiny — the store only needs `session_id` and `created_at` for
    provenance, not a YAML parser dependency."""
    frontmatter, _ = _split_frontmatter(text)
    prefix = f"{key}:"
    for line in frontmatter.splitlines():
        if line.startswith(prefix):
            return line[len(prefix) :].strip()
    return None


def render_extraction_block(extraction: ThoughtExtraction) -> str:
    """Markdown for the summary + every non-empty taxonomy section.

    Empty lists are skipped entirely so the note never shows hollow headers.
    All content is sanitized to a single inline line. Returns "" if there is
    nothing at all to render."""
    parts: list[str] = []
    summary = _sanitize(extraction.summary)
    if summary:
        parts.append("## Summary\n\n" + summary + "\n")
    for field in SECTION_ORDER:
        items = [_sanitize(s) for s in getattr(extraction, field)]
        items = [s for s in items if s]
        if not items:
            continue
        lines = "\n".join(f"- {item}" for item in items)
        parts.append(f"## {_SECTION_TITLES[field]}\n\n{lines}\n")
    return "\n".join(parts)


def enrich_note(path: Path, extraction: ThoughtExtraction) -> bool:
    """Insert the extraction block above the transcript and stamp the
    frontmatter. Returns True if enriched, False if there is nothing to add
    (empty extraction) or the note is already enriched.

    The idempotency guard is scoped to the FRONTMATTER, not the whole note, so
    a transcript whose spoken words include the literal phrase
    `extraction: complete` cannot wedge the note un-enrichable."""
    text = path.read_text(encoding="utf-8")
    frontmatter, body = _split_frontmatter(text)
    if "extraction: complete" in frontmatter:
        return False
    block = render_extraction_block(extraction)
    if not block:
        return False
    if _TRANSCRIPT_ANCHOR not in body:
        raise ValueError(f"note has no '## Transcript' anchor to insert above: {path}")

    # First body occurrence of the anchor is always the real header — any
    # '## Transcript' the speaker uttered can only appear later in the prose.
    new_body = body.replace(_TRANSCRIPT_ANCHOR, block + "\n" + _TRANSCRIPT_ANCHOR, 1)
    new_frontmatter = frontmatter.rstrip("\n") + "\nextraction: complete"
    _atomic_write(path, f"---\n{new_frontmatter}\n---\n{new_body}")
    return True


def _atomic_write(path: Path, content: str) -> None:
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=".note-", suffix=".md.tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write(content)
        os.replace(tmp, path)
    except Exception:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise
