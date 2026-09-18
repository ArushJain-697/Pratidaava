"""
Ticket #19 — Precedent match + citation (Witness 3). NO model call.

SCAFFOLD: the honest weekend version — a hardcoded map from denial reason to the right
seeded precedent. Do NOT fake a retriever you didn't build (Bible §4 W3, §9).

SEAM (#future): real legal-ISSUE retrieval (InLegalBERT + rhetorical-role labelling +
AQgR-style question generation) over the Indian Kanoon SC/NCDRC corpus. Ombudsman awards
are NOT mineable (OTP wall) — precedents are curated SC/NCDRC text (Bible §9).
"""
from __future__ import annotations

from typing import Optional

from backend.schema import PrecedentHit

_MAP = {
    "pre_existing_disease": PrecedentHit(
        case="Manmohan Nanda v. United India Insurance Co. (2022)",
        holding=("An insurer that issued the policy despite a disclosed condition cannot later "
                 "weaponise that condition or its complications to repudiate the claim."),
    ),
    "non_disclosure": PrecedentHit(
        case="Manmohan Nanda v. United India Insurance Co. (2022)",
        holding=("Disclosure made and accepted at proposal cannot be re-characterised as "
                 "non-disclosure to defeat the claim."),
    ),
    "missing_documents": PrecedentHit(
        case="Gurmel Singh v. National Insurance Co. Ltd. (2022)",
        holding=("Repudiation on flimsy, hyper-technical grounds beyond the insured's control "
                 "is a deficiency in service."),
    ),
    "hyper_technical": PrecedentHit(
        case="Gurmel Singh v. National Insurance Co. Ltd. (2022)",
        holding=("Refusing a claim on hyper-technical documentation grounds is a deficiency "
                 "in service."),
    ),
}


def match(denial_reason: Optional[str]) -> Optional[PrecedentHit]:
    if not denial_reason:
        return None
    return _MAP.get(denial_reason)
