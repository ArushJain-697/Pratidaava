"""
Ticket #9 — Doc ingest + text extraction.

SCAFFOLD: loads the sample corpus from backend/data/ as clean text and exposes a
`sources` dict keyed by a stable ref (doc + optional section). The grounding check
(#13) resolves a claim's `cited_source_ref` against this dict.

SEAM (later): replace file reads with S3 objects; replace whole-doc chunks with
OpenSearch hybrid retrieval (#31) so a ref resolves to the exact clause. Keep the
ref scheme deterministic — an unresolvable ref must read as a fabricated citation,
not crash (Bible §5, check 2).
"""
from __future__ import annotations

import os
from typing import Dict

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "data")


def _read(*parts: str) -> str:
    with open(os.path.join(DATA_DIR, *parts), "r", encoding="utf-8") as fh:
        return fh.read().strip()


def load_sources(denial_text: str | None = None, policy_text: str | None = None) -> Dict[str, str]:
    """Return {ref: chunk_text}. Uploaded text overrides the sample when provided."""
    sources: Dict[str, str] = {
        "policy": policy_text or _read("policy.txt"),
        "denial": denial_text or _read("denial_letter.txt"),
        "precedent:manmohan_nanda": _read("precedents", "manmohan_nanda.txt"),
        "precedent:gurmel_singh": _read("precedents", "gurmel_singh.txt"),
    }
    return sources


def resolve(sources: Dict[str, str], ref: str | None) -> str | None:
    """Resolve a claim's cited_source_ref to its chunk text, or None if it doesn't resolve.

    A ref like 'policy§7.9' resolves to the 'policy' chunk (section-level resolution is a
    later refinement); an unknown doc key resolves to None -> treated as a fabricated cite.
    """
    if not ref:
        return None
    doc_key = ref.split("§")[0].strip()
    return sources.get(doc_key)
