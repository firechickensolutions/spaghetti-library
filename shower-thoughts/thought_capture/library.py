"""Thought-capture library ingest — the post-capture orchestration.

One call turns a raw capture into both an enriched note (D28) and a retrievable
library entry (D29): extract the taxonomy and enrich the note, then chunk + embed
the transcript and upsert it into the local vector store.

Graceful degradation is the load-bearing property, and each stage degrades
INDEPENDENTLY: the transcript note is already durable on disk before this runs,
so an extraction failure does not block indexing, an indexing failure does not
undo enrichment, and any failure leaves the transcript note untouched.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

from thought_capture.embed import Embedder, chunk_transcript
from thought_capture.extract import ThoughtExtractor
from thought_capture.note import enrich_note, frontmatter_value
from thought_capture.store import VectorStore


@dataclass
class IngestResult:
    """Outcome of ingesting one capture. Both stages report independently."""

    enriched: bool = False
    indexed_chunks: int = 0
    notes: list[str] = field(default_factory=list)  # degradation messages, if any


def ingest_capture(
    note_path: str | Path,
    transcript: str,
    *,
    extractor: object | None = None,
    embedder: object | None = None,
    store: object | None = None,
    verbose: bool = True,
) -> IngestResult:
    """Extract + enrich the note, then embed + store the transcript.

    Returns an IngestResult; never raises on a live (Ollama/store) failure. The
    durable transcript note written by the sink is the floor and is never put at
    risk here."""
    note_path = Path(note_path)
    result = IngestResult()

    # --- D28: extract + enrich --------------------------------------------
    if extractor is None:
        from thought_capture.vocab import load_terms  # noqa: PLC0415

        extractor = ThoughtExtractor(known_terms=load_terms())
    try:
        extraction = extractor.extract(transcript)
        try:
            result.enriched = enrich_note(note_path, extraction)
        except (OSError, ValueError) as exc:
            result.notes.append(f"enrich failed: {exc}")
    except Exception as exc:  # noqa: BLE001 - degrade on any extraction failure
        result.notes.append(f"extraction skipped ({type(exc).__name__}: {exc})")

    # --- D29: embed + store (independent of the above) --------------------
    chunks = chunk_transcript(transcript)
    if chunks:
        try:
            vectors = (embedder or Embedder()).embed_batch(chunks)
            text = note_path.read_text(encoding="utf-8")
            session_id = frontmatter_value(text, "session_id")
            created_at = frontmatter_value(text, "created_at")
            result.indexed_chunks = (store or VectorStore()).upsert_note(
                str(note_path), session_id, created_at, list(zip(chunks, vectors, strict=True))
            )
        except Exception as exc:  # noqa: BLE001 - degrade on any indexing failure
            result.notes.append(f"indexing skipped ({type(exc).__name__}: {exc})")

    if verbose:
        bits = []
        if result.enriched:
            bits.append("enriched with semantic extraction")
        if result.indexed_chunks:
            bits.append(f"indexed {result.indexed_chunks} chunk(s) into the library")
        if bits:
            print(f"note: {', '.join(bits)} -> {note_path}")
        for msg in result.notes:
            print(f"note: {msg}; transcript note is saved at {note_path}.")

    return result
