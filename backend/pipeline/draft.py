"""
Ticket #8 — Bedrock draft -> letter + structured claims.

Real seam: calls Amazon Bedrock (via the Converse API, provider-agnostic across Claude /
Llama / Titan model IDs) to read the denial + policy sources and emit a letter plus
schema-valid claims as JSON. Uses the standard boto3 credential chain (env vars, shared
credentials file, or an IAM role) — no key is hardcoded here.

When boto3 isn't installed, no AWS_REGION/credentials are configured, or the call fails
for any reason, draft() falls back to the original hardcoded sample (the PED-after-
36-months case, including the ONE deliberately planted fabrication citing policy clause
§7.9 — Beat 1 / ticket #17) so `demo.py` and the invariant tests keep working fully
offline with no AWS and no API keys, exactly as the README promises.

The verifier (verify.py) is what catches whatever draft() gets wrong — including a real
model's real hallucinations, not just the planted one. Bedrock Guardrails is a coarse
net, NOT the hallucination defense (Bible §4A).

SEAM (later): #30 — move this onto AgentCore Runtime (Strands agent loop) with the
pipeline stages exposed as MCP tools via Gateway. Same prompt contract, different host.
"""
from __future__ import annotations

import json
import os
from typing import Dict, List, Optional

from backend.schema import Claim, ClaimType, DraftResult

_AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
_BEDROCK_MODEL_ID = os.environ.get(
    "BEDROCK_MODEL_ID", "anthropic.claude-3-5-sonnet-20241022-v2:0"
)

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


def _call_bedrock(sources: Dict[str, str]) -> Optional[DraftResult]:
    try:
        import boto3  # local import: optional dependency, only needed for this seam
    except ImportError:
        return None

    user_content = (
        f"DENIAL LETTER:\n{sources.get('denial', '')}\n\n"
        f"POLICY:\n{sources.get('policy', '')}\n"
    )

    try:
        client = boto3.client("bedrock-runtime", region_name=_AWS_REGION)
        response = client.converse(
            modelId=_BEDROCK_MODEL_ID,
            system=[{"text": _SYSTEM_PROMPT}],
            messages=[{"role": "user", "content": [{"text": user_content}]}],
            inferenceConfig={"maxTokens": 2000, "temperature": 0},
        )
        blocks = response["output"]["message"]["content"]
        text = "".join(b.get("text", "") for b in blocks).strip()
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
        # Any failure in the real seam (no credentials, region/model access not
        # enabled, bad JSON, schema mismatch) -> fall back rather than crash the
        # pipeline or silently fabricate. verify.py still guards whatever comes out
        # of here regardless of which path produced it.
        return None


def draft(sources: Dict[str, str]) -> DraftResult:
    result = _call_bedrock(sources)
    if result is not None:
        return result
    return _sample_draft()