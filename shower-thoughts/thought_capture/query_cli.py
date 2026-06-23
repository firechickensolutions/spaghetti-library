"""Query the thought-capture library from the CLI (D29).

    python -m thought_capture.query_cli "what have I been thinking about governance?"
    python -m thought_capture.query_cli "trade handoffs" -k 8

Embeds the question with the same local model used at ingest, ranks the stored
chunks by cosine, and prints the top matches with their source note. All local.
"""
from __future__ import annotations

import argparse
import sys

from thought_capture.embed import Embedder
from thought_capture.store import VectorStore


def _format_hit(rank: int, hit: dict) -> str:
    note = hit.get("note_path", "?")
    score = hit.get("score", 0.0)
    created = hit.get("created_at") or ""
    snippet = " ".join((hit.get("text") or "").split())
    if len(snippet) > 240:
        snippet = snippet[:240].rstrip() + "…"
    head = f"[{rank}] {score:.3f}  {note}"
    if created:
        head += f"  ({created})"
    return f"{head}\n    {snippet}"


def run_query(question: str, k: int, *, embedder=None, store=None) -> int:
    store = store or VectorStore()
    if store.count() == 0:
        print("The thought-capture library is empty — capture a session first (make capture).")
        return 0
    embedder = embedder or Embedder()
    try:
        vector = embedder.embed(question)
    except Exception as exc:  # noqa: BLE001
        print(f"Could not embed the query (is Ollama up?): {type(exc).__name__}: {exc}")
        return 2
    hits = store.query(vector, k=k)
    if not hits:
        print("No matches.")
        return 0
    print(f'Top {len(hits)} for: "{question}"\n')
    for i, hit in enumerate(hits, 1):
        print(_format_hit(i, hit))
        print()
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Query the local thought-capture library (D29)."
    )
    parser.add_argument("question", help="The question to search your captured thinking with.")
    parser.add_argument("-k", type=int, default=5, help="Number of passages to return (default 5).")
    args = parser.parse_args(argv)
    return run_query(args.question, args.k)


if __name__ == "__main__":
    sys.exit(main())
