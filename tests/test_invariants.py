"""
Invariant tests — the Ground rule, enforced mechanically (Bible §2, §5).

Run:  python -m pytest -q   (or)   python tests/test_invariants.py
"""
from __future__ import annotations

import json
import os
import re
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from backend.pipeline.run import run_appeal  # noqa: E402

VERIFY_SRC = os.path.join(os.path.dirname(__file__), "..", "backend", "pipeline", "verify.py")

# Tokens that would indicate a generative model call leaked into the verifier.
FORBIDDEN_IN_VERIFY = [
    "boto3", "bedrock", "invoke_model", "openai", "anthropic",
    "llm", ".complete(", ".chat(", "generate(",
]


def _strip_prose(src: str) -> str:
    """Remove triple-quoted strings and # comments so the guard scans real code, not prose."""
    src = re.sub(r'""".*?"""', "", src, flags=re.DOTALL)
    src = re.sub(r"'''.*?'''", "", src, flags=re.DOTALL)
    src = "\n".join(line.split("#", 1)[0] for line in src.splitlines())
    return src


def test_verifier_has_no_model_call():
    """The verifier must contain NO generative model call. Ever. (grep guard)"""
    with open(VERIFY_SRC, "r", encoding="utf-8") as fh:
        code = _strip_prose(fh.read()).lower()
    for tok in FORBIDDEN_IN_VERIFY:
        assert tok not in code, f"model-call token '{tok}' found in verify.py"


def test_no_probability_anywhere():
    """No probability / score / likelihood is ever emitted (the Data Gap rule)."""
    result = run_appeal()
    blob = json.dumps(result.model_dump()).lower()
    assert "probability" not in blob
    assert "likelihood" not in blob
    assert not re.search(r"\b\d{1,3}\s?%", result.final_letter), "no percentage in the letter"


def test_planted_fabrication_is_stripped():
    """Beat 1: the fabricated clause-7.9 claim must be stripped before the human sees it."""
    result = run_appeal()
    kept_ids = {v.claim_id for v in result.kept_claims}
    stripped_ids = {v.claim_id for v in result.stripped_claims}
    assert "c4" in stripped_ids, "the planted fabrication (c4) was not stripped"
    assert "c4" not in kept_ids
    assert "7.9" not in result.final_letter, "fabricated clause leaked into the final letter"


def test_lead_is_rule_backed():
    """Beat 2: the promoted lead argument is the rule-backed impermissible-denial claim."""
    result = run_appeal()
    assert result.lead_argument and "40 months" in result.lead_argument


if __name__ == "__main__":
    for name, fn in sorted(globals().items()):
        if name.startswith("test_") and callable(fn):
            fn()
            print(f"PASS  {name}")
    print("all invariants hold")
