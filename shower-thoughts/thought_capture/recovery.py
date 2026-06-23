"""Crash recovery for thought-capture.

The coherent capture path used to hold the whole session in an in-memory
bytearray and write the note only at stop, so a crash / OOM / kill mid-capture
lost everything. This module makes capture durable: mic PCM is appended to a raw
`.pcm` file on disk AS IT ARRIVES (flushed each write), and the session is
transcribed FROM that file at stop. A crash leaves the `.pcm` behind; the next
capture run recovers it into a note. A clean stop discards it.

Raw LINEAR16 16 kHz mono, no container header — append-only, so a kill at any
instant leaves a fully-decodable file (there is no WAV header to finalize). This
also bounds capture-time memory: only the final decode loads the audio.

Rule 8 env override:
  SHOWER_THOUGHT_RECOVERY_DIR   default <vault>/.library/recovery
"""
from __future__ import annotations

import os
from pathlib import Path

from audio.transcript_sink import vault_path

SAMPLE_RATE_HZ = 16000


def recovery_dir() -> Path:
    raw = os.environ.get("SHOWER_THOUGHT_RECOVERY_DIR")
    if raw:
        return Path(raw)
    return vault_path() / ".library" / "recovery"


class IncrementalAudioRecorder:
    """Appends mic PCM to <recovery>/<session_id>.pcm as it arrives.

    Each write is flushed so a process kill keeps everything captured up to that
    instant (OS-buffer durable; not power-loss durable, which would need fsync)."""

    def __init__(self, session_id: str, directory: Path | None = None) -> None:
        self.session_id = session_id
        d = Path(directory) if directory is not None else recovery_dir()
        d.mkdir(parents=True, exist_ok=True)
        self.path = d / f"{session_id}.pcm"
        self._f = open(self.path, "wb")
        self._closed = False

    def write(self, pcm: bytes) -> None:
        if self._closed:
            return
        self._f.write(pcm)
        self._f.flush()

    def read_all(self) -> bytes:
        self._f.flush()
        return self.path.read_bytes()

    def discard(self) -> None:
        """Clean-stop cleanup: close and delete the .pcm (the note is safely
        written, so the recovery copy is no longer needed)."""
        self.close()
        self.path.unlink(missing_ok=True)

    def preserve_failed(self) -> Path:
        """Close and keep the .pcm as .pcm.failed (audio captured but it could
        not be transcribed — preserve it for salvage rather than discard)."""
        self.close()
        return preserve_failed(self.path)

    def close(self) -> None:
        if not self._closed:
            self._closed = True
            try:
                self._f.close()
            except OSError:
                pass


def orphans(directory: Path | None = None) -> list[Path]:
    """Unrecovered .pcm files from interrupted captures, oldest first.

    Only matches *.pcm — a *.pcm.failed (preserved un-decodable capture) is left
    alone so it is neither auto-retried nor auto-deleted."""
    d = Path(directory) if directory is not None else recovery_dir()
    return sorted(d.glob("*.pcm")) if d.exists() else []


def preserve_failed(path: Path) -> Path:
    """Keep a non-empty but un-decodable capture for manual salvage instead of
    deleting it: rename to <name>.failed so orphans() won't retry or remove it.
    Silent audio loss is the one outcome this feature must never produce."""
    path = Path(path)
    failed = path.with_name(path.name + ".failed")
    path.replace(failed)
    return failed


def recover(path: Path, stt: object, sink: object) -> Path | None:
    """Transcribe an orphan .pcm into a full note (same pipeline as a live
    capture: correct -> write -> enrich/index), then delete the .pcm. Returns the
    note path, or None if it was already recovered / empty / decoded to nothing.

    The transcript is the floor: it is written before enrichment, and enrichment
    degrades gracefully, so a recovered session is never lost to an Ollama outage.
    Audio that decodes to nothing is PRESERVED as .pcm.failed, never deleted."""
    path = Path(path)
    # Already recovered? (a crash between note-write and .pcm discard leaves both
    # on disk) — drop the orphan, do not write a duplicate note for the session.
    if hasattr(sink, "has_note_for") and sink.has_note_for(path.stem):
        path.unlink(missing_ok=True)
        return None
    pcm = path.read_bytes()
    if not pcm:
        path.unlink(missing_ok=True)  # genuinely empty: nothing to preserve
        return None
    from audio.stt_engine import decode_chunked  # noqa: PLC0415

    text = decode_chunked(stt, pcm, SAMPLE_RATE_HZ)  # chunked: long captures don't crash
    if not text:
        preserve_failed(path)  # real bytes, empty decode -> keep for salvage
        return None

    from thought_capture.correct import apply_corrections  # noqa: PLC0415
    from thought_capture.library import ingest_capture  # noqa: PLC0415
    from thought_capture.vocab import load_corrections  # noqa: PLC0415

    text, _ = apply_corrections(text, load_corrections())
    note = sink.write_session_note(path.stem, text)
    path.unlink(missing_ok=True)  # note (the floor) is written -> orphan consumed
    ingest_capture(note, text)  # best-effort enrichment, after the .pcm is gone
    return note
