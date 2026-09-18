"""
Ticket #14 — Claim decomposition (entity-pair, not naive atomic).

Real rule-based decomposer. Splits a compound claim into independent units ONLY when
both halves can stand alone as separately-groundable assertions; refuses to split a
clause off its governing clause (date <-> policy limit, procedure <-> waiting period),
because that's exactly the causal link an appeal turns on (Bible §4).

Deliberately NOT an LLM repair loop (non-monotone, per Bible §4) — this is a fixed,
inspectable rule, not a model call. That means it's conservative: it only ever splits on
an explicit top-level conjunction ("and" / ";") between two clauses, and only when the
second clause doesn't open with a connector that makes it dependent on the first
(relative pronouns, comparatives, causal/temporal linkers). Anything else is left whole.

SEAM (later): nothing generative planned here — if a smarter decomposer is ever wanted,
it should stay a rule/grammar-based pass, not an LLM, per the same invariant.
"""
from __future__ import annotations

import re
from typing import List

from backend.schema import Claim

# Connectors that make a clause dependent on what precedes it — a clause that opens
# with one of these is NEVER split off, because doing so severs the relationship the
# whole claim exists to state (e.g. "..., exceeding the 36-month waiting period").
_DEPENDENT_OPENERS = (
    "which", "that", "this", "it", "its", "then", "thus", "hence", "so",
    "because", "since", "exceeding", "before", "after", "under", "per",
    "despite", "although", "though", "whereas", "while", "as a result",
    "therefore", "consequently",
)

# Only split on a top-level " and " / "; " — never inside a parenthetical or a quoted
# span, and never on commas (commas overwhelmingly introduce a dependent clause here,
# e.g. "40 months, exceeding the 36-month waiting period").
_SPLIT_RE = re.compile(r"\s+and\s+|;\s*")

_MIN_WORDS = 4  # a split half must be a real assertion, not a fragment


def _is_independent(clause: str) -> bool:
    words = clause.strip().split()
    if len(words) < _MIN_WORDS:
        return False
    opener = words[0].lower().strip(",.")
    if opener in _DEPENDENT_OPENERS:
        return False
    return True


def _split_one(claim: Claim) -> List[Claim]:
    parts = [p.strip() for p in _SPLIT_RE.split(claim.text) if p.strip()]
    if len(parts) < 2:
        return [claim]

    # Every part must independently qualify, or we don't split at all — a partial
    # split that orphans one half is worse than no split (Bible §4).
    if not all(_is_independent(p) for p in parts):
        return [claim]

    out: List[Claim] = []
    for i, part in enumerate(parts):
        suffix = "" if i == 0 else chr(ord("a") + i - 1)
        text = part if part.endswith((".", "!", "?")) else part + "."
        out.append(
            Claim(
                claim_id=f"{claim.claim_id}{suffix}",
                text=text,
                claim_type=claim.claim_type,
                cited_source_ref=claim.cited_source_ref,
                asserted_value=claim.asserted_value if i == 0 else None,
            )
        )
    return out


def decompose(claims: List[Claim]) -> List[Claim]:
    out: List[Claim] = []
    for c in claims:
        out.extend(_split_one(c))
    return out