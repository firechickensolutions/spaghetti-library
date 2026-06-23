"""D29 embedding — turn transcript text into local vectors via nomic-embed-text.

Self-contained, same fence as the rest of thought_capture: a thin Ollama
embeddings call, injectable for tests. All local; nothing leaves the machine.

Rule 8 env overrides:
  SHOWER_THOUGHT_EMBED_MODEL    default nomic-embed-text
  SHOWER_THOUGHT_EMBED_TIMEOUT  default 30.0
  SHOWER_THOUGHT_CHUNK_CHARS    default 1000  (target max chars per chunk)
"""
from __future__ import annotations

import os


def chunk_transcript(text: str, max_chars: int | None = None) -> list[str]:
    """Split a coherent transcript into embeddable passages.

    Paragraph-first: the prose note already separates ~3-sentence paragraphs by
    blank lines, which are coherent units. Adjacent paragraphs are packed
    together up to `max_chars`; a single paragraph longer than the budget stands
    as its own chunk (never split mid-sentence). Empty input -> []."""
    if max_chars is None:
        max_chars = int(os.environ.get("SHOWER_THOUGHT_CHUNK_CHARS", "1000"))
    paragraphs = [p.strip() for p in text.split("\n\n") if p.strip()]
    chunks: list[str] = []
    current = ""
    for para in paragraphs:
        if not current:
            current = para
        elif len(current) + 2 + len(para) <= max_chars:
            current = f"{current}\n\n{para}"
        else:
            chunks.append(current)
            current = para
    if current:
        chunks.append(current)
    return chunks


class Embedder:
    """Text -> embedding vector via a local Ollama embedding model."""

    def __init__(
        self,
        model: str | None = None,
        timeout_s: float | None = None,
        client: object | None = None,
    ) -> None:
        self.model = model or os.environ.get(
            "SHOWER_THOUGHT_EMBED_MODEL", "nomic-embed-text"
        )
        self.timeout_s = (
            timeout_s
            if timeout_s is not None
            else float(os.environ.get("SHOWER_THOUGHT_EMBED_TIMEOUT", "30.0"))
        )
        self._client = client

    def _get_client(self) -> object:
        if self._client is not None:
            return self._client
        from ollama import Client  # noqa: PLC0415

        self._client = Client(timeout=self.timeout_s)
        return self._client

    def embed(self, text: str) -> list[float]:
        """Embed one passage. Raises on Ollama failure or an empty embedding —
        the caller (library ingest) degrades."""
        client = self._get_client()
        resp = client.embeddings(model=self.model, prompt=text)
        vector = list(resp["embedding"])
        if not vector:
            raise RuntimeError(f"embedding model {self.model} returned an empty vector")
        return vector

    def embed_batch(self, texts: list[str]) -> list[list[float]]:
        """Embed many passages, in order. (nomic-embed-text has no batch API in
        Ollama; this is a simple per-text loop.)"""
        return [self.embed(t) for t in texts]
