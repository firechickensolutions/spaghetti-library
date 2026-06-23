"""Safe verbatim correction — exact mis-hear -> canonical, nothing fuzzy.

The earlier fuzzy/phonetic approach was abandoned: it corrupted real words
(rewriting a common word into a product name it merely rhymes with) and could
not safely target product names that are also dictionary words (a word vs a
product spelled the same) — text cannot disambiguate those without the audio.

This replacement is corruption-free by construction: it replaces a token ONLY
when the whole token matches an explicit correction-map key exactly (case-
insensitively). The map holds non-word mis-hears (e.g. "speeck" -> "Speck"), so a
real English word can never be rewritten. Meaning-level fixes (the summary using the right spelling) come from priming
the extraction LLM, which has the context the corrector lacks.
"""
from __future__ import annotations

import re

_WORD = re.compile(r"[A-Za-z][A-Za-z']*")


def apply_corrections(text: str, corrections: dict[str, str]) -> tuple[str, list[tuple[str, str]]]:
    """Replace whole-token exact matches of a mis-hear key with its canonical
    value. Returns (corrected_text, [(original, replacement), ...]). No-op on
    empty input or empty map. Casing of the key is ignored; the canonical value
    is written as-is."""
    if not text or not corrections:
        return text, []

    fixes: list[tuple[str, str]] = []

    def _repl(m: re.Match[str]) -> str:
        token = m.group(0)
        canonical = corrections.get(token.lower())
        if canonical is not None and token != canonical:
            fixes.append((token, canonical))
            return canonical
        return token

    return _WORD.sub(_repl, text), fixes
