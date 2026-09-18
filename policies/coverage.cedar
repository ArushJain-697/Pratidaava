// Ticket #12 — Cedar policy. SOURCE OF TRUTH for the rules (Bible §6).
// backend/pipeline/cedar.py is a Python stand-in that must stay behavior-identical to this.
// Coverage is modeled as an authorization decision; `forbid` overrides `permit`, so an
// impermissible repudiation is a FORBID (a win for the claimant).
//
// SEAM: evaluate this with the open-source Cedar engine (Build It) or AgentCore Policy /
// Amazon Verified Permissions (Ship It, #30).

// ---------- Group A: coverage oracle — is the claim payable under the contract? ----------
permit (
    principal,
    action == Action::"ReimburseClaim",
    resource
)
when {
    resource.procedure_code in principal.plan.covered_procedures &&
    context.service_date >= principal.plan.effective_date &&
    context.service_date >= principal.plan.waiting_period_end &&
    principal.plan.annual_used + context.claim_amount <= principal.plan.annual_limit
};

// ---------- Group B: denial-validity oracle — IRDAI protections that void a repudiation ----------

// 36-month PED cap: a PED denial after 36 months of continuous cover is impermissible.
forbid (
    principal,
    action == Action::"RepudiateClaim",
    resource
)
when {
    resource.denial_reason == "pre_existing_disease" &&
    principal.plan.continuous_coverage_months >= 36
};

// 60-month moratorium: no repudiation for non-disclosure after 5 years, absent proven fraud.
forbid (
    principal,
    action == Action::"RepudiateClaim",
    resource
)
when {
    resource.denial_reason == "non_disclosure" &&
    principal.plan.continuous_coverage_months >= 60 &&
    resource.proven_intentional_fraud == false
};

// Missing-document prohibition on cashless claims.
forbid (
    principal,
    action == Action::"RepudiateClaim",
    resource
)
when {
    resource.denial_reason == "missing_documents" &&
    resource.channel == "cashless"
};
