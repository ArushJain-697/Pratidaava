"""
Tickets #16 (strip + render) and #20 (contradiction -> lead-argument promotion).

Removes STRIP claims BEFORE the human sees the letter, promotes the strongest
rule/precedent-backed claim to the lead argument, and builds the final letter body
from the kept claims only. NO model call.
"""
from __future__ import annotations

from typing import List

from backend.schema import AppealResult, Tier, VerifiedClaim


def assemble(verified: List[VerifiedClaim]) -> AppealResult:
    kept = [v for v in verified if v.kept]
    stripped = [v for v in verified if not v.kept]

    # #20 — lead argument: prefer a Tier-A claim backed by an impermissible-denial rule,
    # else any Tier-A, else the first kept claim.
    lead = None
    for v in kept:
        if v.tier == Tier.A and v.policy.value == "FORBID":
            lead = v
            break
    if lead is None:
        lead = next((v for v in kept if v.tier == Tier.A), None)
    if lead is None:
        lead = kept[0] if kept else None

    body_lines = []
    if lead is not None:
        body_lines.append(f"1. {lead.text}  [{lead.chip}]")
    n = 2
    for v in kept:
        if lead is not None and v.claim_id == lead.claim_id:
            continue
        body_lines.append(f"{n}. {v.text}  [{v.chip}]")
        n += 1

    final_letter = (
        "To the Grievance Redressal Officer,\n\n"
        "I am writing to formally appeal the repudiation of my claim on the following "
        "grounds, each of which is supported by my policy documents, the IRDAI Master "
        "Circular, or binding precedent:\n\n"
        + "\n".join(body_lines)
        + "\n\nI request that the repudiation be reviewed and the claim settled.\n\n"
        "Yours faithfully,\n[Claimant]\n"
    )

    return AppealResult(
        lead_argument=(lead.text if lead else None),
        final_letter=final_letter,
        kept_claims=kept,
        stripped_claims=stripped,
    )
