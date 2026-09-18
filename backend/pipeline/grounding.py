"""
Ticket #13 — Grounding check v1 (Witness 1). NO model call.

SCAFFOLD: real, runnable substring/keyword grounding — the weekend approach. Resolves
the claim's cited_source_ref and checks whether the claim's key phrase is supported by
the source chunk. Returns (Grounding, evidence_span).

Known weakness (say it on stage, don't hide it): substring fails on paraphrase
("elevated core temperature" -> "fever") and arithmetic ("3 days at Rs 1,000" -> "Rs 3,000").
SEAM (#29): swap for an NLI/entailment endpoint on SageMaker + Semantic-F1 (Bible §4 W1).
"""
from __future__ import annotations

import re
from typing import Dict, Tuple

from backend.schema import Claim, Grounding

_STOP = {
    "the", "a", "an", "of", "for", "to", "in", "on", "at", "and", "or", "is", "has",
    "been", "that", "this", "with", "per", "by", "as", "it", "its", "not", "no",
}


def _keywords(text: str) -> list[str]:
    words = re.findall(r"[a-z0-9]+", text.lower())
    return [w for w in words if w not in _STOP and len(w) > 2]


def check(claim: Claim, sources: Dict[str, str], resolve) -> Tuple[Grounding, str | None]:
    chunk = resolve(sources, claim.cited_source_ref)

    # Rule 1 & 2 (Bible §5): no ref, or a ref that doesn't resolve -> ABSENT (fabricated cite).
    if chunk is None:
        return Grounding.ABSENT, None

    # A cite to a section that the chunk doesn't actually contain -> ABSENT.
    # (Sample: 'policy§7.9' resolves to the policy chunk, but '7.9' appears nowhere in it.)
    if "§" in (claim.cited_source_ref or ""):
        section = claim.cited_source_ref.split("§", 1)[1].strip()
        if section and section not in chunk:
            return Grounding.ABSENT, None

    # Substring/keyword support: enough of the claim's keywords must appear in the chunk.
    kws = _keywords(claim.text)
    if not kws:
        return Grounding.UNVERIFIED, None
    hits = [w for w in kws if w in chunk.lower()]
    ratio = len(hits) / len(kws)

    if ratio >= 0.4:
        # crude evidence span: first sentence of the chunk that contains a hit keyword
        for sentence in re.split(r"(?<=[.\n])\s+", chunk):
            if any(w in sentence.lower() for w in hits):
                return Grounding.DOCUMENTED, sentence.strip()[:240]
        return Grounding.DOCUMENTED, chunk[:240]
    return Grounding.UNVERIFIED, None
