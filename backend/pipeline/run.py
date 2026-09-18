"""
Ticket #11 — End-to-end wire. Orchestrates the full pipeline:

    ingest -> draft -> decompose -> verify -> assemble

This is the single entry point the API (#app) and the demo (#demo) both call.
"""
from __future__ import annotations

from typing import Dict, Optional

from backend.pipeline import assemble, decompose, draft, ingest, verify
from backend.schema import AppealResult

# For the sample PED-after-36-months case. Later these facts are parsed from the
# denial letter + policy schedule rather than hardcoded.
SAMPLE_CASE_FACTS: Dict = {
    "denial_reason": "pre_existing_disease",
    "continuous_coverage_months": 40,
    "channel": "reimbursement",
    "proven_intentional_fraud": False,
}


def run_appeal(
    denial_text: Optional[str] = None,
    policy_text: Optional[str] = None,
    case_facts: Optional[Dict] = None,
) -> AppealResult:
    sources = ingest.load_sources(denial_text=denial_text, policy_text=policy_text)
    drafted = draft.draft(sources)                       # #8
    claims = decompose.decompose(drafted.claims)         # #14
    verified = verify.verify(claims, sources, case_facts or SAMPLE_CASE_FACTS)  # #15
    return assemble.assemble(verified)                   # #16 / #20
