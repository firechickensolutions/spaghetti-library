"""Your vocabulary — coined names the STT cannot know.

Two roles, both safe by construction:
  - `terms`: your product/person/project names, primed into the extraction LLM so
    the structured note uses correct spellings (the LLM sees context, so it safely
    maps a mis-hear -> the right name in the summary). This is the primary fix.
  - `corrections`: an EXACT-match map (mis-hear -> canonical) applied to the raw
    transcript. Exact whole-token only, keyed on non-word mis-hears, so it can
    never rewrite a real English word — the failure mode that kills fuzzy matching
    (a fuzzy "buddy"/"slat" -> a product name).

Ships EMPTY. Add your own names with add_term()/add_correction(), or hand-edit
the seeded vocab.json in the vault's .library/ folder. No per-capture interaction.

Example:
    from thought_capture.vocab import add_term, add_correction
    add_term("Photerra")                 # primes the LLM to spell it right
    add_correction("photera", "Photerra")  # fixes an exact mis-hear in the raw text

Env override:
  SHOWER_THOUGHT_VOCAB_PATH   default <vault>/.library/vocab.json
"""
from __future__ import annotations

import json
import os
from pathlib import Path

from audio.transcript_sink import vault_path

# Ships empty — add your own. Keys in corrections are LOWERCASE and must be
# non-words (never a real English word) so exact replacement is corruption-free.
SEED_TERMS: tuple[str, ...] = ()
SEED_CORRECTIONS: dict[str, str] = {}


def vocab_path() -> Path:
    raw = os.environ.get("SHOWER_THOUGHT_VOCAB_PATH")
    if raw:
        return Path(raw)
    return vault_path() / ".library" / "vocab.json"


def _load(path: Path | None = None) -> dict:
    p = path or vocab_path()
    if not p.exists():
        p.parent.mkdir(parents=True, exist_ok=True)
        data = {"terms": list(SEED_TERMS), "corrections": dict(SEED_CORRECTIONS)}
        p.write_text(json.dumps(data, indent=2), encoding="utf-8")
        return data
    return json.loads(p.read_text(encoding="utf-8"))


def load_terms(path: Path | None = None) -> list[str]:
    """Your known terms (for LLM priming). Seeds on first use."""
    seen: dict[str, str] = {}
    for t in _load(path).get("terms", []):
        if t and t.strip():
            seen.setdefault(t.strip().lower(), t.strip())
    return list(seen.values())


def load_corrections(path: Path | None = None) -> dict[str, str]:
    """The exact mis-hear -> canonical map (for the raw transcript). Keys lowercased."""
    out: dict[str, str] = {}
    for k, v in _load(path).get("corrections", {}).items():
        if k and v and k.strip():
            out[k.strip().lower()] = v.strip()
    return out


def add_term(term: str, path: Path | None = None) -> bool:
    """Add a known term (idempotent, case-insensitive). The one low-load knob for a
    new coined name. Returns True if newly added."""
    term = term.strip()
    if not term:
        return False
    p = path or vocab_path()
    data = _load(p)
    terms = data.setdefault("terms", [])
    if any(t.lower() == term.lower() for t in terms):
        return False
    terms.append(term)
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True


def add_correction(mishear: str, canonical: str, path: Path | None = None) -> bool:
    """Map an exact mis-hear to a canonical spelling. The key must be a genuine
    non-word mis-hear (a real English word as the key would be unsafe); the caller
    is trusted to pass one. Returns True if set."""
    mishear, canonical = mishear.strip().lower(), canonical.strip()
    if not mishear or not canonical:
        return False
    p = path or vocab_path()
    data = _load(p)
    corrections = data.setdefault("corrections", {})
    if corrections.get(mishear) == canonical:
        return False
    corrections[mishear] = canonical
    p.write_text(json.dumps(data, indent=2), encoding="utf-8")
    return True
