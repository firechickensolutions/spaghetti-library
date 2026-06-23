"""Durable Markdown note writer for thought-capture.

Writes one Obsidian-compatible Markdown note per capture session to the vault
directory (SHOWER_CAPTURE_VAULT_PATH). The whole-session transcript is written at
once from a single coherent STT pass: frontmatter + the transcript formatted into
readable paragraphs.

Env override:
  SHOWER_CAPTURE_VAULT_PATH    default ~/ShowerThoughts
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass
from datetime import UTC, datetime
from pathlib import Path
from threading import Lock

# Default vault: a plain folder in the user's home. Point SHOWER_CAPTURE_VAULT_PATH
# at an Obsidian vault subfolder to make these notes part of an existing vault.
DEFAULT_VAULT_PATH = str(Path.home() / "ShowerThoughts")


def vault_path() -> Path:
    """Resolve the capture vault directory (env override)."""
    raw = os.environ.get("SHOWER_CAPTURE_VAULT_PATH", DEFAULT_VAULT_PATH)
    return Path(raw)


@dataclass
class _NoteState:
    path: Path
    created_at: datetime


def _yaml_safe_scalar(value: str) -> str:
    """Make a string safe to interpolate as an unquoted YAML frontmatter scalar:
    collapse newlines to spaces and strip the flow-list delimiters."""
    cleaned = " ".join(str(value).split())
    for ch in ("[", "]", ","):
        cleaned = cleaned.replace(ch, "")
    return cleaned.strip()


def _format_transcript_prose(text: str) -> str:
    """Group a punctuated whole-session transcript into ~3-sentence paragraphs so a
    long monologue reads as paragraphs, not one wall of text."""
    stripped = text.strip()
    sentences = [s for s in re.split(r"(?<=[.!?])\s+", stripped) if s]
    if not sentences:
        return stripped
    paragraphs = [" ".join(sentences[i : i + 3]) for i in range(0, len(sentences), 3)]
    return "\n\n".join(paragraphs)


class MarkdownVaultTranscriptSink:
    """Writes one Markdown note per session from a coherent whole-session transcript."""

    def __init__(self, vault_dir: Path | None = None) -> None:
        self._vault_dir = Path(vault_dir) if vault_dir is not None else vault_path()
        self._sessions: dict[str, _NoteState] = {}
        self._lock = Lock()

    def note_path_for(self, session_id: str) -> Path | None:
        """The note path written for session_id, or None if none written yet."""
        with self._lock:
            state = self._sessions.get(session_id)
            return state.path if state is not None else None

    def has_note_for(self, session_id: str) -> bool:
        """True if a note file for this session_id already exists on disk.

        Crash recovery uses this to avoid writing a duplicate note when a capture
        crashed in the window between the note being written and its recovery .pcm
        being discarded. Checks disk (not the in-memory map), since recovery runs
        in a fresh process."""
        if not self._vault_dir.exists():
            return False
        return any(self._vault_dir.glob(f"*-{session_id}.md"))

    def write_session_note(
        self, session_id: str, text: str, source_stream: str = "operator_mic"
    ) -> Path:
        """Write a whole-session coherent transcript as a prose note: frontmatter
        + the transcript formatted into readable paragraphs."""
        with self._lock:
            self._vault_dir.mkdir(parents=True, exist_ok=True)
            created_at = datetime.now(UTC)
            stamp = created_at.strftime("%Y%m%d-%H%M%S")
            session_id = _yaml_safe_scalar(session_id)
            source_stream = _yaml_safe_scalar(source_stream)
            path = self._vault_dir / f"{stamp}-{session_id}.md"
            note = (
                "---\n"
                f"session_id: {session_id}\n"
                f"created_at: {created_at.isoformat()}\n"
                "mode: thought_capture\n"
                f"source_streams: [{source_stream}]\n"
                "status: captured\n"
                "---\n\n"
                f"# Thought capture {created_at.strftime('%Y-%m-%d %H:%M')}\n\n"
                "## Transcript\n\n"
                f"{_format_transcript_prose(text)}\n"
            )
            with open(path, "w", encoding="utf-8") as f:
                f.write(note)
            self._sessions[session_id] = _NoteState(path=path, created_at=created_at)
            return path
