"""
Ticket #7 — Structured-claim schema. The seam between AGENT (draft) and VERIFY.

This is the contract every stage keys off. Two invariants are enforced *structurally*
here, because they are the whole thesis (Bible §2, §5):

  1. There is NO probability / score / "likelihood" field anywhere. The Data Gap forbids
     it (Bible §0, §10). A claim is graded by which witnesses concur, not by odds.
  2. `tier` is a discrete corroboration level, never a number.
"""
from __future__ import annotations

from enum import Enum
from typing import List, Optional

from pydantic import BaseModel


class ClaimType(str, Enum):
    FACTUAL = "FACTUAL"
    NUMERIC = "NUMERIC"
    COVERAGE = "COVERAGE"          # checked against Cedar (Witness 2)
    PROCEDURAL = "PROCEDURAL"
    PRECEDENTIAL = "PRECEDENTIAL"  # checked against the precedent library (Witness 3)


class Grounding(str, Enum):
    """Witness 1 verdict — is the claim entailed by the user's own documents?"""
    DOCUMENTED = "DOCUMENTED"
    ABSENT = "ABSENT"
    CONTRADICTED = "CONTRADICTED"
    UNVERIFIED = "UNVERIFIED"


class PolicyDecision(str, Enum):
    """Witness 2 verdict — the Cedar rules engine over IRDAI + policy terms."""
    PERMIT = "PERMIT"   # the claim is payable under the contract
    FORBID = "FORBID"   # the *repudiation* is impermissible under IRDAI (this is a win)
    NA = "N/A"


class Tier(str, Enum):
    """Corroboration level — which witnesses concur. NOT a probability."""
    A = "A"          # rule/precedent-backed AND grounded  -> the strongest sentences
    B = "B"          # grounded only                        -> documented fact
    C = "C"          # weak / topic-present-not-entailed
    STRIP = "STRIP"  # contradicted or absent              -> removed before the human sees it


class Claim(BaseModel):
    """What the draft (AGENT) emits, one per material assertion."""
    claim_id: str
    text: str
    claim_type: ClaimType
    cited_source_ref: Optional[str] = None   # pointer into the retrieved sources
    asserted_value: Optional[str] = None     # for NUMERIC/COVERAGE: the specific value claimed


class PrecedentHit(BaseModel):
    case: str
    holding: str


class VerifiedClaim(BaseModel):
    """What the verifier (VERIFY) emits, one per input claim."""
    claim_id: str
    text: str
    tier: Tier
    grounding: Grounding
    policy: PolicyDecision = PolicyDecision.NA
    precedent: Optional[PrecedentHit] = None
    evidence_span: Optional[str] = None
    kept: bool
    chip: str   # human-readable citation shown in the UI — a rule §, a case, or a source span.
                # NEVER a percentage. (Bible §4 corroboration)


class DraftResult(BaseModel):
    letter: str
    claims: List[Claim]


class AppealResult(BaseModel):
    lead_argument: Optional[str] = None
    final_letter: str
    kept_claims: List[VerifiedClaim]
    stripped_claims: List[VerifiedClaim]
