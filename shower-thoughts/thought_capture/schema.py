"""Thought-extraction schema — the thinking taxonomy.

The structured shape the local LLM fills from a transcript. Pydantic v2 at the
boundary.
"""
from __future__ import annotations

from pydantic import BaseModel, Field


class ThoughtExtraction(BaseModel):
    """Structured taxonomy extracted from one coherent capture transcript (D28).

    Every list field degrades to empty: a transcript with no decisions yields
    `decisions: []`, never a hallucinated one. The model READS the transcript;
    it does not invent content that is not there. `summary` defaults to "" so an
    extraction is always constructible even from a near-empty capture.
    """

    summary: str = Field(
        default="", description="2-4 sentence plain summary of what this capture is about."
    )
    threads: list[str] = Field(
        default_factory=list, description="Recurring themes or lines of thinking."
    )
    claims: list[str] = Field(
        default_factory=list, description="Things asserted or discovered as true."
    )
    decisions: list[str] = Field(
        default_factory=list, description="Choices made or settled in this capture."
    )
    open_questions: list[str] = Field(
        default_factory=list, description="Unresolved questions raised."
    )
    actions: list[str] = Field(
        default_factory=list, description="Concrete next steps to take."
    )
    artifacts: list[str] = Field(
        default_factory=list,
        description="Things to create or update (docs, code, notes).",
    )
    links: list[str] = Field(
        default_factory=list,
        description="Suggested connections to existing vault topics or notes.",
    )


# The list-section order used when an extraction is rendered into a note
# (summary is rendered separately, above these).
SECTION_ORDER = (
    "threads",
    "claims",
    "decisions",
    "open_questions",
    "actions",
    "artifacts",
    "links",
)
