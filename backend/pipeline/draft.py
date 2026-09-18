"""
Ticket #8 — Draft appeal -> letter + structured claims.

Real seam: when GROQ_API_KEY is set, draft() calls Groq (OpenAI-compatible Chat
Completions API) to read the denial + policy sources and emit a letter plus schema-valid
claims as JSON. When no key is present, it falls back to the original hardcoded sample
(the PED-after-36-months case, including the ONE deliberately planted fabrication citing
policy clause §7.9 — Beat 1 / ticket #17) so `demo.py` and the invariant tests keep
working fully offline with no AWS and no API keys, exactly as the README promises.

The verifier (verify.py) is what catches whatever draft() gets wrong — including a real
model's real hallucinations, not just the planted one. Any provider's safety filter is a
coarse net, NOT the hallucination defense (Bible §4A).

SEAM (later): swap the Groq call below for a Bedrock call (Strands agent loop) — same
prompt contract (JSON-schema-constrained claims + letter), different transport.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

import requests

from backend.schema import Claim, ClaimType, DraftResult

_GROQ_URL = "https://api.groq.com/openai/v1/chat/completions"
_GROQ_MODEL = os.environ.get("GROQ_MODEL", "llama-3.3-70b-versatile")

_SYSTEM_PROMPT = """You are drafting a grievance-redressal appeal letter for a denied \
health insurance claim. You will be given the denial letter and the policy text.

Respond with ONLY a JSON object, no prose, no markdown fences, matching exactly:
{
  "letter": "<opening paragraph of the appeal letter, body left as a placeholder — the \
body is assembled later from verified claims>",
  "claims": [
    {
      "claim_id": "c1",
      "text": "<one material, checkable assertion>",
      "claim_type": "FACTUAL | NUMERIC | COVERAGE | PROCEDURAL | PRECEDENTIAL",
      "cited_source_ref": "<'policy', 'denial', 'precedent:<slug>', or a section ref \
like 'policy§4.2' — the exact clause/fact this claim rests on>",
      "asserted_value": "<the specific number/value claimed, or null>"
    }
  ]
}

Rules:
- Every claim must cite a specific, real source ref. Never invent a clause number.
- One claim per material assertion — do not bundle unrelated facts into one claim.
- Do not include a probability, confidence, or likelihood anywhere.
"""

_SAMPLE_CLAIMS: List[Claim] = [
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

_SAMPLE_LETTER = (
    "To the Grievance Redressal Officer,\n\n"
    "I am writing to formally appeal the repudiation of my claim. "
    "[body assembled from verified claims below]\n"
)


def _sample_draft() -> DraftResult:
    return DraftResult(letter=_SAMPLE_LETTER, claims=list(_SAMPLE_CLAIMS))


def _call_groq(sources: Dict[str, str]) -> Optional[DraftResult]:
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        return None

    user_content = (
        f"DENIAL LETTER:\n{sources.get('denial', '')}\n\n"
        f"POLICY:\n{sources.get('policy', '')}\n"
    )

    try:
        resp = requests.post(
            _GROQ_URL,
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": _GROQ_MODEL,
                "messages": [
                    {"role": "system", "content": _SYSTEM_PROMPT},
                    {"role": "user", "content": user_content},
                ],
                "response_format": {"type": "json_object"},
                "temperature": 0,
            },
            timeout=60,
        )
        resp.raise_for_status()
        text = resp.json()["choices"][0]["message"]["content"].strip()
        if text.startswith("```"):
            text = text.strip("`")
            text = text.split("\n", 1)[1] if "\n" in text else text
        payload = json.loads(text)

        claims = [
            Claim(
                claim_id=c["claim_id"],
                text=c["text"],
                claim_type=ClaimType(c["claim_type"]),
                cited_source_ref=c.get("cited_source_ref"),
                asserted_value=c.get("asserted_value"),
            )
            for c in payload["claims"]
        ]
        return DraftResult(letter=payload["letter"], claims=claims)
    except Exception:
        return None


def draft(sources: Dict[str, str]) -> DraftResult:
    result = _call_groq(sources)
    if result is not None:
        return result
    return _sample_draft()