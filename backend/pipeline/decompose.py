"""
Ticket #14 — Claim decomposition (entity-pair, not naive atomic).

SCAFFOLD: passthrough — returns claims unchanged.

SEAM (later): decompose into units that PRESERVE relationships (date <-> policy limit,
procedure <-> waiting period). Do NOT over-decompose into orphaned atoms — splitting
"denied because the annual limit was exceeded" into two atoms severs the causal link
the appeal turns on. Do NOT build an LLM repair loop (non-monotone) (Bible §4).
"""
from __future__ import annotations

from typing import List

from backend.schema import Claim


def decompose(claims: List[Claim]) -> List[Claim]:
    # TODO(#14): entity-pair decomposition preserving date<->limit relationships.
    return claims
