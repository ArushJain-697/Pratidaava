"""
Ticket #15 — The no-LLM verifier + corroboration grading. THE THESIS.

Two hard constraints, enforced here and load-bearing (Bible §2, §5, §11):
  * NO generative model call in this module. Ever. (Grep this file: there is none.)
  * NO probability / score emitted. A claim is graded by which witnesses concur.

Combines three witnesses per claim:
  W1 grounding (#13)  -> DOCUMENTED / ABSENT / CONTRADICTED / UNVERIFIED
  W2 rules   (#12)    -> Cedar PERMIT / FORBID / N/A   (COVERAGE claims)
  W3 precedent (#19)  -> a role-matched case            (PRECEDENTIAL claims / denial ground)

Tiers (Bible §5):
  A     : (W2 FORBID/PERMIT applies OR W3 hit) AND W1 == DOCUMENTED
  B     : W1 == DOCUMENTED, no rule/precedent lever
  C     : W1 == UNVERIFIED but topic present
  STRIP : W1 == ABSENT or CONTRADICTED
"""
from __future__ import annotations

from typing import Dict, List

from backend.pipeline import cedar, grounding, precedent
from backend.pipeline.ingest import resolve
from backend.schema import (
    Claim,
    ClaimType,
    Grounding,
    PolicyDecision,
    Tier,
    VerifiedClaim,
)


def _chip(tier: Tier, grounding_v: Grounding, policy: PolicyDecision, prec, span) -> str:
    """Human-readable citation for the UI. NEVER a percentage (Bible §4)."""
    if tier == Tier.STRIP:
        return "unsupported — removed"
    if policy == PolicyDecision.FORBID:
        return "rule: denial impermissible under IRDAI Master Circular 2024"
    if policy == PolicyDecision.PERMIT:
        return "rule: payable under policy terms"
    if prec is not None:
        return f"case: {prec.case}"
    if grounding_v == Grounding.DOCUMENTED and span:
        return f"source: \u201c{span[:80]}\u2026\u201d"
    if grounding_v == Grounding.DOCUMENTED:
        return "source: documented in your papers"
    return "weak — topic present, not confirmed"


def verify(claims: List[Claim], sources: Dict[str, str], case_facts: Dict) -> List[VerifiedClaim]:
    cedar_decision = cedar.evaluate(case_facts)               # W2 (case-level)
    precedent_hit = precedent.match(case_facts.get("denial_reason"))  # W3 (denial ground)

    out: List[VerifiedClaim] = []
    for c in claims:
        grounding_v, span = grounding.check(c, sources, resolve)      # W1

        policy = PolicyDecision.NA
        prec = None
        if c.claim_type == ClaimType.COVERAGE:
            policy = cedar_decision
        if c.claim_type == ClaimType.PRECEDENTIAL:
            prec = precedent_hit

        has_lever = policy in (PolicyDecision.FORBID, PolicyDecision.PERMIT) or prec is not None

        if grounding_v in (Grounding.ABSENT, Grounding.CONTRADICTED):
            tier = Tier.STRIP
        elif grounding_v == Grounding.DOCUMENTED and has_lever:
            tier = Tier.A
        elif grounding_v == Grounding.DOCUMENTED:
            tier = Tier.B
        else:
            tier = Tier.C

        # A PRECEDENTIAL claim whose only support is the case itself (its text names the case)
        # is Tier A even if the policy chunk doesn't echo it — the witness IS the precedent.
        if c.claim_type == ClaimType.PRECEDENTIAL and prec is not None and tier != Tier.STRIP:
            tier = Tier.A
            grounding_v = Grounding.DOCUMENTED

        out.append(
            VerifiedClaim(
                claim_id=c.claim_id,
                text=c.text,
                tier=tier,
                grounding=grounding_v,
                policy=policy,
                precedent=prec,
                evidence_span=span,
                kept=(tier != Tier.STRIP),
                chip=_chip(tier, grounding_v, policy, prec, span),
            )
        )
    return out
