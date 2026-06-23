"""D29 local vector store — flat cosine over SQLite.

Lean by decision: embeddings live in
a single local SQLite file; similarity is computed in numpy over the full set at
query time. No sqlite-vec native extension, no chromadb service. For a personal
thinking library (hundreds-to-low-thousands of chunks) this is instant,
dependency-free, and trivially inspectable. The trade — a linear scan per query
— only matters past ~100k chunks, far beyond a personal corpus; if it is ever
reached, swap the query() internals for sqlite-vec without touching callers.

All local. The store file sits beside the notes.

Rule 8 env override:
  SHOWER_THOUGHT_STORE_PATH   default <vault>/.library/index.sqlite
"""
from __future__ import annotations

import os
import sqlite3
from pathlib import Path

from audio.transcript_sink import vault_path

_SCHEMA = """
CREATE TABLE IF NOT EXISTS chunks (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    note_path   TEXT NOT NULL,
    session_id  TEXT,
    created_at  TEXT,
    chunk_idx   INTEGER NOT NULL,
    text        TEXT NOT NULL,
    embedding   BLOB NOT NULL
);
CREATE INDEX IF NOT EXISTS idx_chunks_note ON chunks(note_path);
"""


def store_path() -> Path:
    raw = os.environ.get("SHOWER_THOUGHT_STORE_PATH")
    if raw:
        return Path(raw)
    return vault_path() / ".library" / "index.sqlite"


def _pack(vector: list[float]) -> bytes:
    import numpy as np  # noqa: PLC0415

    return np.asarray(vector, dtype="float32").tobytes()


def _unpack(blob: bytes) -> object:
    import numpy as np  # noqa: PLC0415

    return np.frombuffer(blob, dtype="float32")


class VectorStore:
    """Append-and-query store for capture chunks. One row per (note, chunk)."""

    def __init__(self, path: Path | None = None) -> None:
        self.path = Path(path) if path is not None else store_path()
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self._conn() as conn:
            conn.executescript(_SCHEMA)

    def _conn(self) -> sqlite3.Connection:
        return sqlite3.connect(self.path)

    def upsert_note(
        self,
        note_path: str,
        session_id: str | None,
        created_at: str | None,
        chunks: list[tuple[str, list[float]]],
    ) -> int:
        """Replace all chunks for `note_path` with the given (text, vector) pairs.

        Delete-then-insert makes re-ingesting the same note idempotent — no
        duplicate rows when a capture is re-processed. Returns rows written.

        The DELETE + INSERT run in ONE transaction: Python's sqlite3 default
        (isolation_level="") opens an implicit transaction before the DELETE and
        the `with conn:` block commits on success or rolls back on any exception,
        so a crash between the two steps cannot leave a note half-indexed. (The
        index is also rebuildable from the notes, so it is never the floor.)"""
        with self._conn() as conn:
            conn.execute("DELETE FROM chunks WHERE note_path = ?", (str(note_path),))
            conn.executemany(
                "INSERT INTO chunks (note_path, session_id, created_at, chunk_idx, text, embedding) "
                "VALUES (?, ?, ?, ?, ?, ?)",
                [
                    (str(note_path), session_id, created_at, idx, text, _pack(vec))
                    for idx, (text, vec) in enumerate(chunks)
                ],
            )
            return len(chunks)

    def query(self, embedding: list[float], k: int = 5) -> list[dict]:
        """Return the top-k chunks by cosine similarity to `embedding`.

        Each result: note_path, session_id, created_at, chunk_idx, text, score.
        Empty store -> []."""
        import numpy as np  # noqa: PLC0415

        q = np.asarray(embedding, dtype="float32")
        qn = float(np.linalg.norm(q))
        if qn == 0.0:
            return []
        q = q / qn

        rows = []
        with self._conn() as conn:
            cur = conn.execute(
                "SELECT note_path, session_id, created_at, chunk_idx, text, embedding FROM chunks"
            )
            for note_path, session_id, created_at, chunk_idx, text, blob in cur:
                vec = _unpack(blob)
                vn = float(np.linalg.norm(vec))
                if vn == 0.0:
                    continue
                score = float(np.dot(q, vec) / vn)
                rows.append(
                    {
                        "note_path": note_path,
                        "session_id": session_id,
                        "created_at": created_at,
                        "chunk_idx": chunk_idx,
                        "text": text,
                        "score": score,
                    }
                )
        rows.sort(key=lambda r: r["score"], reverse=True)
        return rows[:k]

    def count(self) -> int:
        with self._conn() as conn:
            return int(conn.execute("SELECT COUNT(*) FROM chunks").fetchone()[0])
