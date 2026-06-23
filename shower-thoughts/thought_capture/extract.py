"""Semantic-extraction head — a local LLM turns a transcript into a taxonomy.

A thin Ollama call using structured output (JSON-schema-constrained) plus a
single repair retry. The model READS the transcript; the system prompt forbids
inventing content. This is a thinking surface, not a generator.

Rule 8 env overrides:
  SHOWER_THOUGHT_LLM_MODEL    default qwen2.5:7b
  SHOWER_THOUGHT_LLM_TIMEOUT  default 60.0         (seconds; whole-session, not per-utterance)
  SHOWER_THOUGHT_LLM_TEMP     default 0.2          (low: extraction, not generation)
"""
from __future__ import annotations

import json
import os

from pydantic import ValidationError

from thought_capture.schema import ThoughtExtraction

_SYSTEM = (
    "You read a transcript of a person thinking out loud and extract a structured "
    "thinking taxonomy. You READ — you never invent content that is not present in "
    "the transcript. If a section has nothing in the transcript, return an empty "
    "list for it. Be concise and concrete, and use the speaker's own framing rather "
    "than generic paraphrase. Output only JSON that matches the provided schema."
)


def _user_prompt(transcript: str) -> str:
    return (
        "Extract the thinking taxonomy from this captured monologue. Return JSON "
        "matching the schema — summary plus the lists. Leave any list empty if the "
        "transcript does not support it.\n\nTRANSCRIPT:\n" + transcript
    )


class ThoughtExtractor:
    """Transcript -> ThoughtExtraction via a local Ollama model."""

    def __init__(
        self,
        model: str | None = None,
        timeout_s: float | None = None,
        client: object | None = None,
        known_terms: list[str] | None = None,
    ) -> None:
        self.model = model or os.environ.get("SHOWER_THOUGHT_LLM_MODEL", "qwen2.5:7b")
        # Operator coined names — primed into the system prompt so the model uses
        # exact spellings and never invents expansions (e.g. your coined names, not
        # "BIDI (Bidirectional Text)").
        self.known_terms = known_terms or []
        self.timeout_s = (
            timeout_s
            if timeout_s is not None
            else float(os.environ.get("SHOWER_THOUGHT_LLM_TIMEOUT", "60.0"))
        )
        self.temperature = float(os.environ.get("SHOWER_THOUGHT_LLM_TEMP", "0.2"))
        # Injectable for tests: any object with a chat(model, messages, format,
        # options) -> {"message": {"content": str}} signature. None -> a live
        # Ollama client built lazily on first use.
        self._client = client

    def extract(self, transcript: str) -> ThoughtExtraction:
        """Return a structured extraction for `transcript`.

        An empty/whitespace transcript returns an empty `ThoughtExtraction`
        without calling the model. A live failure (Ollama unreachable, or two
        invalid responses) raises — the caller decides how to degrade (the
        capture path keeps the transcript note and marks extraction pending).
        """
        if not transcript.strip():
            return ThoughtExtraction()

        client = self._client
        if client is None:
            # Lazy import: unit tests inject a fake and never need a live Ollama
            # or the package installed.
            from ollama import Client  # noqa: PLC0415

            client = Client(timeout=self.timeout_s)
        schema = ThoughtExtraction.model_json_schema()
        system = _SYSTEM
        if self.known_terms:
            system += (
                "\n\nThe speaker's known proper nouns / product names: "
                + ", ".join(self.known_terms)
                + ". Use these exact spellings and never invent an expansion or "
                "meaning for them."
            )
        last_err: str | None = None

        for _attempt in range(2):  # initial + one repair retry
            messages = [
                {"role": "system", "content": system},
                {"role": "user", "content": _user_prompt(transcript)},
            ]
            if last_err is not None:
                messages.append(
                    {
                        "role": "user",
                        "content": (
                            f"Your previous output failed validation: {last_err}. "
                            "Return valid JSON for the schema."
                        ),
                    }
                )
            resp = client.chat(
                model=self.model,
                messages=messages,
                format=schema,
                options={"temperature": self.temperature},
            )
            content = resp["message"]["content"]
            try:
                return ThoughtExtraction.model_validate_json(content)
            except (ValidationError, json.JSONDecodeError) as exc:
                last_err = str(exc)[:300]

        raise RuntimeError(
            f"thought extraction failed schema validation after one repair: {last_err}"
        )
