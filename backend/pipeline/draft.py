"""
Ticket #8 — Draft appeal -> letter + structured claims.

SCAFFOLD: returns a hardcoded DraftResult for the sample PED-after-36-months case,
including ONE deliberately fabricated claim (it cites policy clause §7.9, which does
not exist in the sample policy) so the verifier has something to catch on camera —
this is Beat 1 / ticket #17.

SEAM (later): replace `draft()` with a Bedrock call (Strands agent loop) that reads
the denial + policy + bill and emits the letter plus schema-valid claims. Bedrock
Guardrails is a coarse net, NOT the hallucination defense — the verifier is (Bible §4A).
"""
from __future__ import annotations

from typing import Dict

from backend.schema import Claim, ClaimType, DraftResult


def draft(sources: Dict[str, str]) -> DraftResult:
    claims = [
        Claim(
            claim_id="c1",
            text=("The policy has been continuously in force for 40 months, exceeding the "
                  "36-month waiting period for pre-existing diseases."),
            claim_type=ClaimType.COVERAGE,
            cited_source_ref="policy",
            asserted_value="40",
        ),
        Claim(
            claim_id="c2",
            text=("Per Manmohan Nanda v. United India Insurance (2022), an insurer that issued "
                  "the policy despite a disclosed condition cannot later repudiate on that ground."),
            claim_type=ClaimType.PRECEDENTIAL,
            cited_source_ref="precedent:manmohan_nanda",
        ),
        Claim(
            claim_id="c3",
            text="The insured disclosed a history of Type-II diabetes at the proposal stage.",
            claim_type=ClaimType.FACTUAL,
            cited_source_ref="policy",
        ),
        # --- PLANTED FABRICATION (Beat 1 / #17): cites a clause that isn't in the policy ---
        Claim(
            claim_id="c4",
            text=("Clause 7.9 of the policy grants an unconditional overseas-emergency waiver "
                  "of all exclusions."),
            claim_type=ClaimType.FACTUAL,
            cited_source_ref="policy§7.9",
        ),
    ]
    letter = (
        "To the Grievance Redressal Officer,\n\n"
        "I am writing to formally appeal the repudiation of my claim. "
        "[body assembled from verified claims below]\n"
    )
    return DraftResult(letter=letter, claims=claims)
