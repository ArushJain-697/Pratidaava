"""
Tests for the two pieces that were stubs and are now real: cedar.py Group A (permit)
and decompose.py (entity-pair splitting). Kept separate from test_invariants.py, which
is the mechanically-enforced Ground rule suite — these are ordinary unit tests.

Run:  python -m pytest -q   (or)   python tests/test_cedar_and_decompose.py
"""
from __future__ import annotations

import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.pipeline import cedar, decompose  # noqa: E402
from backend.schema import Claim, ClaimType, PolicyDecision  # noqa: E402


_GOOD_REIMBURSE_FACTS = {
    "action": "ReimburseClaim",
    "plan": {
        "covered_procedures": ["CPT-99213", "CPT-99214"],
        "effective_date": "2021-01-01",
        "waiting_period_end": "2021-07-01",
        "annual_limit": 500000,
        "annual_used": 100000,
    },
    "resource": {
        "procedure_code": "CPT-99213",
        "claim_amount": 50000,
    },
    "context": {
        "service_date": "2024-03-01",
    },
}


def test_permit_when_all_conditions_hold():
    decision = cedar.evaluate(_GOOD_REIMBURSE_FACTS)
    assert decision == PolicyDecision.PERMIT


def test_na_when_procedure_not_covered():
    facts = {**_GOOD_REIMBURSE_FACTS, "resource": {"procedure_code": "CPT-00000", "claim_amount": 50000}}
    assert cedar.evaluate(facts) == PolicyDecision.NA


def test_na_when_before_waiting_period_ends():
    facts = {**_GOOD_REIMBURSE_FACTS, "context": {"service_date": "2021-03-01"}}
    assert cedar.evaluate(facts) == PolicyDecision.NA


def test_na_when_annual_limit_exceeded():
    facts = {
        **_GOOD_REIMBURSE_FACTS,
        "plan": {**_GOOD_REIMBURSE_FACTS["plan"], "annual_used": 480000},
    }
    assert cedar.evaluate(facts) == PolicyDecision.NA


def test_na_on_malformed_facts_does_not_crash():
    facts = {"action": "ReimburseClaim", "plan": {"covered_procedures": ["X"]}, "resource": {}, "context": {}}
    assert cedar.evaluate(facts) == PolicyDecision.NA


def test_group_b_still_unaffected_by_group_a_changes():
    facts = {
        "denial_reason": "pre_existing_disease",
        "continuous_coverage_months": 40,
        "channel": "reimbursement",
        "proven_intentional_fraud": False,
    }
    assert cedar.evaluate(facts) == PolicyDecision.FORBID


def test_independent_claim_is_split():
    claim = Claim(
        claim_id="c9",
        text="The claim amount was Rs 45,000 and the hospital is a network provider.",
        claim_type=ClaimType.FACTUAL,
        cited_source_ref="policy",
    )
    out = decompose.decompose([claim])
    assert len(out) == 2
    assert out[0].claim_id == "c9"
    assert out[1].claim_id == "c9a"
    assert "Rs 45,000" in out[0].text
    assert "network provider" in out[1].text


def test_dependent_clause_is_not_split():
    # Mirrors the sample c1 claim: the second half is dependent on the first
    # ("exceeding..."), so splitting would sever the causal link (Bible §4).
    claim = Claim(
        claim_id="c1",
        text=("The policy has been continuously in force for 40 months, exceeding the "
              "36-month waiting period for pre-existing diseases."),
        claim_type=ClaimType.COVERAGE,
        cited_source_ref="policy",
        asserted_value="40",
    )
    out = decompose.decompose([claim])
    assert len(out) == 1
    assert out[0].claim_id == "c1"
    assert out[0].text == claim.text


def test_fragment_half_blocks_the_split():
    # "and denied" is too short/fragmentary to stand alone -> whole claim kept intact.
    claim = Claim(
        claim_id="c2",
        text="The claim was submitted on time and denied.",
        claim_type=ClaimType.FACTUAL,
        cited_source_ref="denial",
    )
    out = decompose.decompose([claim])
    assert len(out) == 1


def test_passthrough_on_sample_claims_unchanged():
    # The 4 original sample claims must decompose to exactly themselves, or
    # test_invariants.py's claim_id assertions (e.g. "c4" stripped) would break.
    from backend.pipeline.draft import _SAMPLE_CLAIMS
    out = decompose.decompose(list(_SAMPLE_CLAIMS))
    assert [c.claim_id for c in out] == [c.claim_id for c in _SAMPLE_CLAIMS]
    assert [c.text for c in out] == [c.text for c in _SAMPLE_CLAIMS]


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
    print("all tests pass")