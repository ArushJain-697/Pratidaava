"""
Ticket #12 — Cedar rules (Witness 2). NO model call.

SCAFFOLD: a Python stand-in that mirrors policies/coverage.cedar so the pipeline runs
offline with zero AWS. `policies/coverage.cedar` is the source of truth for the rules;
this function must stay behavior-identical to it.

SEAM (later): replace `evaluate()` with a real Cedar evaluation — the open-source Cedar
engine locally (Build It), or AgentCore Policy / Amazon Verified Permissions (Ship It,
#30). Coverage is modeled as an authorization decision; `forbid` overrides `permit`, so
an impermissible repudiation is a FORBID (Bible §6).
"""
from __future__ import annotations

from typing import Dict

from backend.schema import PolicyDecision


def evaluate(case_facts: Dict) -> PolicyDecision:
    reason = case_facts.get("denial_reason")
    months = int(case_facts.get("continuous_coverage_months", 0))
    channel = case_facts.get("channel", "reimbursement")
    proven_fraud = bool(case_facts.get("proven_intentional_fraud", False))

    # Group B — denial-validity oracle: IRDAI protections that VOID a repudiation.
    # 36-month PED cap.
    if reason == "pre_existing_disease" and months >= 36:
        return PolicyDecision.FORBID
    # 60-month moratorium on non-disclosure (absent proven intentional fraud).
    if reason == "non_disclosure" and months >= 60 and not proven_fraud:
        return PolicyDecision.FORBID
    # Missing-document prohibition on cashless claims.
    if reason == "missing_documents" and channel == "cashless":
        return PolicyDecision.FORBID

    # Group A — coverage oracle would go here (permit when contract conditions hold).
    # TODO(#12): port the full permit conditions from coverage.cedar.
    return PolicyDecision.NA
