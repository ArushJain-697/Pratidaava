"""
Ticket #12 — Cedar rules (Witness 2). NO model call.

Real Python evaluator for policies/coverage.cedar (the source of truth — see that file
for the canonical policy text). This mirrors Cedar's authorization model: a single
(principal, action, resource, context) request is evaluated against `permit` and
`forbid` statements, and `forbid` always overrides `permit`. In this domain the two
policy groups target different actions, so they don't actually collide — but the
combinator below is written the way it would be if a real Cedar engine were doing it,
so swapping in the real thing (open-source Cedar, AgentCore Policy / Amazon Verified
Permissions) later is a drop-in replacement, not a rewrite.

SEAM (later): replace `evaluate()` with a call into the actual Cedar engine, loading
policies/coverage.cedar directly instead of mirroring it by hand.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Dict, Optional

from backend.schema import PolicyDecision


@dataclass
class Plan:
    covered_procedures: tuple
    effective_date: date
    waiting_period_end: date
    annual_limit: float
    annual_used: float
    continuous_coverage_months: int


@dataclass
class ReimburseRequest:
    plan: Plan
    procedure_code: str
    claim_amount: float
    service_date: date


def _parse_date(value) -> Optional[date]:
    if value is None:
        return None
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value))


def _parse_reimburse_request(case_facts: Dict) -> Optional[ReimburseRequest]:
    """Build a ReimburseRequest from case_facts["plan"]/["resource"]/["context"], or
    None if the fields Group A needs aren't present (e.g. the sample PED case, which
    only ever exercises Group B)."""
    plan_raw = case_facts.get("plan")
    resource_raw = case_facts.get("resource")
    context_raw = case_facts.get("context")
    if not plan_raw or not resource_raw or not context_raw:
        return None

    try:
        plan = Plan(
            covered_procedures=tuple(plan_raw["covered_procedures"]),
            effective_date=_parse_date(plan_raw["effective_date"]),
            waiting_period_end=_parse_date(plan_raw["waiting_period_end"]),
            annual_limit=float(plan_raw["annual_limit"]),
            annual_used=float(plan_raw["annual_used"]),
            continuous_coverage_months=int(
                plan_raw.get("continuous_coverage_months",
                             case_facts.get("continuous_coverage_months", 0))
            ),
        )
        return ReimburseRequest(
            plan=plan,
            procedure_code=str(resource_raw["procedure_code"]),
            claim_amount=float(resource_raw["claim_amount"]),
            service_date=_parse_date(context_raw["service_date"]),
        )
    except (KeyError, ValueError, TypeError):
        # Malformed/incomplete request facts -> Group A can't evaluate. Fail closed
        # to NA rather than raising, matching Bible §5 check 2 (never crash on bad input).
        return None


def _evaluate_reimburse(case_facts: Dict) -> Optional[PolicyDecision]:
    """Group A — coverage oracle. Mirrors coverage.cedar lines 10-20 exactly."""
    req = _parse_reimburse_request(case_facts)
    if req is None:
        return None

    conditions = (
        req.procedure_code in req.plan.covered_procedures,
        req.service_date >= req.plan.effective_date,
        req.service_date >= req.plan.waiting_period_end,
        req.plan.annual_used + req.claim_amount <= req.plan.annual_limit,
    )
    return PolicyDecision.PERMIT if all(conditions) else None


def _evaluate_repudiate(case_facts: Dict) -> Optional[PolicyDecision]:
    """Group B — denial-validity oracle. Mirrors coverage.cedar lines 24-56 exactly."""
    reason = case_facts.get("denial_reason")
    months = int(case_facts.get("continuous_coverage_months", 0))
    channel = case_facts.get("channel", "reimbursement")
    proven_fraud = bool(case_facts.get("proven_intentional_fraud", False))

    # 36-month PED cap.
    if reason == "pre_existing_disease" and months >= 36:
        return PolicyDecision.FORBID
    # 60-month moratorium on non-disclosure (absent proven intentional fraud).
    if reason == "non_disclosure" and months >= 60 and not proven_fraud:
        return PolicyDecision.FORBID
    # Missing-document prohibition on cashless claims.
    if reason == "missing_documents" and channel == "cashless":
        return PolicyDecision.FORBID
    return None


def evaluate(case_facts: Dict) -> PolicyDecision:
    action = case_facts.get("action")
    if action is None:
        action = "RepudiateClaim" if case_facts.get("denial_reason") else "ReimburseClaim"

    if action == "RepudiateClaim":
        decision = _evaluate_repudiate(case_facts)
    elif action == "ReimburseClaim":
        decision = _evaluate_reimburse(case_facts)
    else:
        decision = None

    return decision or PolicyDecision.NA