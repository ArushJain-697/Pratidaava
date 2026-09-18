# Claim-Appeal Agent — Detailed Build Map & Step-by-Step Implementation Guide (v1)

**For anyone building the Claim-Appeal Agent who has NOT read the full Bible.** This file is self-contained and ordered so each ticket can be built and tested on its own before moving to the next. The companion `bible-final.md` has the deep "why" — read it if a ticket's rationale is unclear. Where a ticket cites a Bible section (e.g. §6), that's where the reasoning lives.

**Build model:** team of 1–4, **First Commit hackathon — Bharat Builds Tour (AWS), Sept 17–20 2026 (Thu–Sun)**, hybrid, free entry. This is a real sprint, and it is **checkpoint-gated by the demo, not by the clock** — because the whole thing is judged on a **3-minute recorded video with no live demo**, the video's three beats *are* the schedule. Build order targets **"the guard catches a hallucination on camera" by the first checkpoint**, then layers the precedent payoff and the governance gate on top — not "build toward one ending at hour N."

This map is granular on purpose: bigger pieces are split so each ticket is buildable and independently testable in a single sitting, and every ticket has an explicit **Test** step, not just a "done when" description. For a system whose entire pitch is *"our AI won't lie in a legal document,"* the Test step is load-bearing — a persuasive letter that reads well but cites a clause that isn't in the policy is worse than one that crashes.

---

## How to Read This Map

Tickets are numbered in strict dependency order — `Blocked by` only ever points to a lower ticket number, so the logical build sequence never leaves you stuck on something undone.

### Priority tag

| Tag | Meaning |
|---|---|
| 🟥 **CORE** | The spine, or a headline differentiator. If you build nothing else, build these. Without them there is no thesis. |
| 🟨 **SUPPORTING** | Real capability that strengthens the demo, but the spine tells its story without it. Build after the loop works end-to-end. |
| ⬜ **SEED / PITCH-ONLY** | A north-star piece where the weekend can't reach the real version. Build a *token* version to prove the idea, or narrate it on stage over the architecture slide — production is future work, not a hackathon target. |

### Track tag (which workstream a ticket primarily lives on — this is how a team of up to 4 parallelizes)

| Tag | Meaning |
|---|---|
| 🟩 **VERIFY** | The deterministic spine: Cedar rules, the no-LLM verifier, corroboration grading. This track *is* the thesis — protect it. |
| 🟦 **AGENT** | The generative side: Bedrock/Strands draft, claim decomposition, assembly, final-letter generation. |
| 🟪 **DATA** | Corpus, extraction, retrieval/index, grounding source, precedent seeding. |
| 🟧 **FRONT** | Amplify UI, citation chips, the human-confirm gate, audit view, and the demo/video itself. |

### Type tag

| Tag | Meaning |
|---|---|
| **Discuss** | A decision or rehearsal, not code. Outcome is an agreed answer in writing or a line the team can say cold. |
| **Prototype** | Known-achievable; the work is doing it correctly and testing it. |
| **Research** | Outcome uncertain; the ticket may return "the weekend version is the fallback." Budget for that. |
| **Infra** | Plumbing, harnesses, schemas — no intelligence, but everything above depends on it. |

### Per-ticket fields

Each ticket has: **Build** (what to actually make), **Watch out** (the specific mistake the Bible already flagged for this piece), **Test** (how to verify it works, standalone), **Done when** (the pass condition). Plus a **Checkpoint** line: the demo beat this ticket must be green for.

**Golden rule:** don't start a ticket until its blockers show green on their own Test step. A ticket that "mostly works" is not done — the next ticket silently inherits its bugs, and in a verification stack a broken lower ticket means the guard passes a hallucination it should have caught.

**Ground rule (project-specific):** every factual sentence in a generated appeal must trace to a **rule** (Cedar), a **case** (precedent), or a **source span** (grounding) — or it is stripped before a human ever sees it, and **no output is ever a probability** (Bible §2, §5, the Data-Gap finding in §0/§10). "It produced a persuasive letter" is never a passing Test. "Every surviving sentence carries a citation chip, and the planted fabrication was stripped" is.

---

## Checkpoint Gates (the spine of the schedule)

| Gate | Name | Pass condition (demo, not vibes) |
|---|---|---|
| **C0** | Walking skeleton | Upload a file → a (stubbed) draft renders in the UI end-to-end. The pipe is connected. |
| **C1** | Beat 1 — the guard | A deliberately fabricated policy clause in the draft is flagged and **stripped on camera**; surviving claims show grounding chips. |
| **C2** | Beat 2 — cite the court | Cedar flags the PED denial impermissible after 36 months; the precedent engine attaches *Manmohan Nanda*, promoted to the lead argument. |
| **C3** | Beat 3 — no number, gate, audit | Every chip cites a rule/case (never a %); the human reviews and confirms; a final GRO letter + tamper-evident audit entry is produced. |
| **C4** | Shipped | 3-min video recorded, blog published on AWS Builder Center, submission in before the deadline. |

**Scheduling rule (project-specific):** the four Tracks can run in parallel across people **once C0 (the skeleton) is green** — one person pushes the VERIFY spine (Phases 2–3) while another builds the AGENT draft/decompose and a third preps DATA. But get **#3 (Bedrock access)** and **#4 (the corpus)** done *first*, before anything else: nearly every ticket is blocked on one or both, and discovering a model-access wall or a broken sample doc mid-sprint is a catastrophic time sink. The VERIFY track is the spine — if you are down a person, take them off FRONT polish, never off VERIFY.

---

## Phase 0 — Pre-Event Decisions & Foundations

### #1: Scope & Denial-Type Lock
Priority: 🟥 CORE
Type: Discuss
Track: 🟩 VERIFY
Checkpoint: Before build starts
Blocked by: —

**Build:** Pick and write down the **one** denial type the whole demo runs on: PED denial after 36 months of continuous cover (primary), or missing-document hyper-technical denial (fallback). Everything downstream — the Cedar rule, the precedent, the sample letter — is chosen to serve this one path (Bible §3b, §12).
**Watch out:** the failure mode here is the two-sided platform — a facility dashboard, multiple denial types, a chatbot. One denial type that verifies end-to-end beats four that half-work (Bible §12 scope discipline). Decide once and stop revisiting.
**Test:** the chosen denial type is written at the top of the repo README, and every Phase-0 data ticket references it by name.
**Done when:** one denial type is chosen in writing and the team stops debating it.

### #2: Registration & AWS Builder Center
Priority: 🟥 CORE
Type: Discuss
Track: 🟧 FRONT
Checkpoint: Before build starts
Blocked by: —

**Build:** Settle four things and stop: the project name (Bible leaves it TBD — decide it now, across form/repo/UI); the track intent (one submission is auto-considered for all, but decide whether you're targeting Ship It's deployed URL or a Build It local build); the 1–4 person role split across the four Tracks; and every member's AWS Builder Center profile (required to compete).
**Watch out:** the AWS Builder Center profile is the mandatory home base — no profile, no eligibility. Do it before doors, not on the clock.
**Done when:** name, track, roles, and all Builder Center profiles are settled in writing before build starts.

### #3: Bedrock Model Access Confirmed
Priority: 🟥 CORE
Type: Infra
Track: 🟦 AGENT
Checkpoint: Before build starts (ideally)
Blocked by: —

**Build:** Enable model access for the chosen Bedrock model in the target region and prove a round-trip: a script sends a prompt, gets a completion back. This is the analog of "confirm the toolchain works before the sprint" — nearly all of the AGENT track is blocked on it.
**Watch out:** discovering a model-access wall or a region mismatch *during* the sprint is a catastrophic time sink (Bible §12 risk register). Enable access first, before any other build ticket.
**Test:** run one prompt → completion round-trip end-to-end from a script.
**Done when:** you have a proven, repeatable call that returns a Bedrock completion.

### #4: Sample Corpus Sourced
Priority: 🟥 CORE
Type: Prototype
Track: 🟪 DATA
Checkpoint: Before build starts
Blocked by: —

**Build:** Assemble the demo corpus as clean text: one real public Indian health-policy PDF, one realistic **synthetic** denial letter matching the chosen type (#1), and two precedents as plain text — *Manmohan Nanda* and *Gurmel Singh* (Bible §3c).
**Watch out:** do NOT fight scanned/heavily-formatted PDFs — OCR is the documented rabbit hole that sinks these projects (Bible §8 post-mortem, §9). Use clean text samples; the parsing problem is explicitly out of scope for the slice.
**Test:** load each file, confirm text extracts cleanly and the denial letter states a reason that matches the chosen denial type.
**Done when:** policy, denial letter, and two precedents are in S3 as clean, extracted text.

### #5: Repo + Infra Skeleton
Priority: 🟥 CORE
Type: Infra
Track: 🟧 FRONT
Checkpoint: C0
Blocked by: —

**Build:** The deployable shell: an S3 bucket, DynamoDB tables (claim state + audit), an empty Lambda, API Gateway, and an Amplify app shell — wired enough that a request reaches a stub endpoint and returns.
**Watch out:** the checkbox-architecture trap — don't stand up twelve services now. Five load-bearing services that run beat a sprawling diagram that half-runs (Bible §4A, §12).
**Test:** `curl` the API Gateway endpoint through to the Lambda and back; confirm a stub response reaches the Amplify shell.
**Done when:** the skeleton is deployed and a request flows shell → API → Lambda → shell.

### #6: Kiro Specs + Steering from the Bible
Priority: 🟨 SUPPORTING
Type: Infra
Track: 🟦 AGENT
Checkpoint: Before build starts
Blocked by: —

**Build:** Feed `bible-final.md` into Kiro Specs (requirements → design → tasks) and pin the five §1 principles as Steering files so the coding agent can't drift (Bible §4A). If running a team of 4, stand up Kiro Crew with one agent per Track.
**Watch out:** Kiro/Crew are build-time tooling, not runtime — do not put them in the architecture or claim them for the "built on AWS" score (Bible §4A).
**Test:** run Kiro's requirements analysis over the bible; confirm it surfaces at least the "no probability" and "verifier makes no model call" constraints as steering rules.
**Done when:** specs are generated and the non-negotiables are pinned as steering.

---

## Phase 1 — Walking Skeleton (C0)

> This phase exists so every ticket above the pipe has something honest to attach to. Nothing here is intelligent — the point is one request flowing end-to-end through stubs before any brains go in.

### #7: Structured-Claim Schema
Priority: 🟥 CORE
Type: Infra
Track: 🟦 AGENT
Checkpoint: C0
Blocked by: #5

**Build:** Fix the JSON contract the draft emits and the verifier consumes: per claim — `claim_id`, `text`, `claim_type` (FACTUAL / NUMERIC / COVERAGE / PROCEDURAL / PRECEDENTIAL), `cited_source_ref`, `asserted_value` (Bible §5). Everything downstream keys off this shape.
**Watch out:** if the draft returns free prose instead of prose + structured claims, the verifier has nothing to check and the whole thesis collapses. The schema is the seam between AGENT and VERIFY — lock it before either side builds against it.
**Test:** validate a hand-written sample claim object against the schema; confirm the verifier stub can parse it.
**Done when:** a single claim schema is agreed and both the draft and the verifier stub read/write it.

### #8: Bedrock Draft → Letter + Claims
Priority: 🟥 CORE
Type: Prototype
Track: 🟦 AGENT
Checkpoint: C0
Blocked by: #3, #7

**Build:** The `Draft` step: Bedrock reads the denial reason + policy + bill and returns an appeal letter **plus** the structured claims list (#7), each claim carrying a pointer to what it's based on (Bible §4, §5).
**Watch out:** Bedrock Guardrails (PII, denied topics) is a coarse net and is NOT your hallucination defense — the deterministic verifier is (Bible §4A). Don't lean on Guardrails to do the verifier's job.
**Test:** feed the sample denial + policy; confirm the output contains both a readable letter and a well-formed claims array that validates against #7.
**Done when:** one Bedrock call returns a letter and a schema-valid claims list for the sample case.

### #9: Doc Ingest + Text Extraction
Priority: 🟥 CORE
Type: Prototype
Track: 🟪 DATA
Checkpoint: C0
Blocked by: #4, #5

**Build:** Ingest the corpus to S3 and extract to clean, chunked text with stable references (doc + span) the grounding check can later resolve.
**Watch out:** references must be stable and resolvable — a chunk ref that can't be resolved later reads as a fabricated citation and gets everything stripped (Bible §5, check 2). Keep the ref scheme simple and deterministic.
**Test:** extract the policy PDF; resolve a known clause by its ref and confirm you get the exact expected span back.
**Done when:** every corpus doc is chunked with resolvable refs.

### #10: UI Shell — Upload → Letter → Placeholder Chips
Priority: 🟥 CORE
Type: Prototype
Track: 🟧 FRONT
Checkpoint: C0
Blocked by: #5

**Build:** The Amplify screen: an upload control, a rendered letter pane, and placeholder citation chips beside each claim (real grading comes at #16).
**Watch out:** an accessibility tool that is itself an accessible, clean UI is the Best-UI story — but that's polish; at C0 the chips are placeholders. Don't gold-plate the UI before the verifier exists.
**Test:** upload a file, confirm the letter renders and placeholder chips appear per claim.
**Done when:** the shell shows an uploaded doc's draft with one placeholder chip per claim.

### #11: End-to-End Stub Wire
Priority: 🟥 CORE
Type: Prototype
Track: 🟧 FRONT
Checkpoint: C0
Blocked by: #8, #9, #10

**Build:** Connect the pipe: upload → ingest (#9) → Bedrock draft (#8) → UI render (#10), with the verifier still a stub returning fake tiers.
**Watch out:** this is a *connection* milestone, not an intelligence one — resist adding the real verifier here. Prove the pipe first (Bible §12 Day 1).
**Test:** from the UI, upload the sample denial and confirm a real Bedrock draft renders with (stub-tiered) chips.
**Done when:** upload → draft renders in the UI end-to-end — **C0 gate.**

---

## Phase 2 — The Verifier: The Thesis (C1)

> The most important phase. If you protect one thing, protect this. The `Verify` step makes no generative model call — that constraint is the entire pitch.

### #12: Cedar Policy — Core Rules
Priority: 🟥 CORE
Type: Prototype
Track: 🟩 VERIFY
Checkpoint: C1
Blocked by: #1

**Build:** A Cedar policy file encoding the IRDAI + policy-term rules for the chosen denial: the 36-month PED cap and the missing-document prohibition as `forbid`-on-repudiation rules, plus the coverage `permit` conditions (Bible §6). Start as a local Cedar file, not AVP.
**Watch out:** model coverage as an authorization decision (`ReimburseClaim` / `RepudiateClaim`), and let `forbid` override `permit` — that's how denials-as-exceptions work (Bible §6). Local Cedar first; AVP is a stretch (#30).
**Test:** evaluate the sample case (PED, 40 months' continuous cover) and confirm Cedar returns the `forbid`-on-repudiation decision — i.e. the denial is impermissible.
**Done when:** the Cedar engine returns a correct permit/forbid decision for the sample case from a local policy file.

### #13: Grounding Check v1 (substring / Semantic-F1)
Priority: 🟥 CORE
Type: Prototype
Track: 🟩 VERIFY
Checkpoint: C1
Blocked by: #7, #9

**Build:** Witness 1: resolve each claim's `cited_source_ref` to its chunk and test support — start with normalized substring / simple similarity, returning DOCUMENTED / ABSENT / CONTRADICTED (Bible §4 Witness 1, §5).
**Watch out:** substring matching fails on paraphrase ("elevated core temperature" → "fever") and arithmetic ("3 days at ₹1,000" → "₹3,000") — this is a known weakness, and the NLI upgrade (#29) is the north-star fix (Bible §4 Witness 1). Ship substring for the slice, but *say* on stage that NLI is the upgrade path — don't pretend substring is the final answer.
**Test:** on a claim whose source clearly supports it → DOCUMENTED; on a fabricated claim with an unresolvable ref → ABSENT.
**Done when:** the grounding check returns a correct three-way verdict for a supported claim and a fabricated one.

### #14: Claim Decomposition (entity-pair)
Priority: 🟥 CORE
Type: Prototype
Track: 🟦 AGENT
Checkpoint: C1
Blocked by: #7, #8

**Build:** Decompose the draft's claims into verifiable units that preserve relationships (date ↔ policy limit, procedure ↔ waiting period) rather than naive atomic splits (Bible §4 decomposition).
**Watch out:** over-decomposition severs causal/regulatory links — splitting "denied because the annual limit was exceeded" into two atoms destroys the nuance the appeal turns on. And do NOT build an LLM repair loop to fix bad splits — the Bible notes they're non-monotone and may never terminate (Bible §4).
**Test:** decompose a two-clause causal claim; confirm the causal relationship survives as one verifiable unit, not two orphaned atoms.
**Done when:** decomposition preserves at least one date↔limit relationship as a single checkable unit.

### #15: The No-LLM Verifier + Corroboration Grading
Priority: 🟥 CORE
Type: Prototype
Track: 🟩 VERIFY
Checkpoint: C1
Blocked by: #12, #13, #14

**Build:** The core function: for each decomposed claim, combine the grounding verdict (#13) and the Cedar decision (#12) into a tier — Tier A (rule-backed + grounded), Tier B (grounded only), Tier C (weak), STRIP (contradicted/absent). No generative model call; no probability anywhere (Bible §5).
**Watch out:** the two hard constraints are the whole thesis — a single model call in here, or a single "% likely" in the output, and you've lost it (Bible §2, §5, §11). Also: don't reach for an LLM-as-judge to grade grounding — the Bible documents its numeric/prior bias as exactly why this stays deterministic (Bible §5, §11).
**Test:** run the full claim set; confirm each claim gets a tier, a fabricated claim gets STRIP, and nowhere in the output is there a probability or score.
**Done when:** every claim is tiered by concurrence with no model call and no probability emitted.

### #16: Assembly — Strip + Render Chips
Priority: 🟥 CORE
Type: Prototype
Track: 🟧 FRONT
Checkpoint: C1
Blocked by: #15, #10

**Build:** Remove STRIP claims from the letter before render, and show each surviving claim's real tier chip (rule § / case / source span) in the UI (Bible §5 assembly).
**Watch out:** the chip must cite the witness, never a percentage (Bible §4 corroboration). A stripped claim must visibly *disappear* from the letter, not merely grey out — that visible removal is the demo.
**Test:** feed a claim set containing one fabricated claim; confirm it's gone from the rendered letter and the rest show correct tier chips.
**Done when:** the rendered letter contains only kept claims, each with an accurate citation chip.

### #17: Plant-and-Catch Harness (Beat 1)
Priority: 🟥 CORE
Type: Prototype
Track: 🟩 VERIFY
Checkpoint: C1
Blocked by: #16

**Build:** A repeatable demo setup where the draft is made to cite a clause that isn't in the policy, and the verifier strips it — this *is* Beat 1 of the video (Bible demo shot list, §12).
**Watch out:** the fabrication must be one a judge can see is fabricated in a glance (a named clause that isn't in the shown policy), and the strip must be visible and instant. A subtle catch doesn't read on camera.
**Test:** run the harness twice; confirm the fabricated clause is caught and stripped both times, visibly, in the UI.
**Done when:** "watch the guard catch its own hallucination" runs reliably on camera — **C1 gate.**

---

## Phase 3 — Rules Payoff + Precedent (C2)

> This is where the appeal grows teeth: the verifier stops being only a filter and becomes the thing that finds the winning argument.

### #18: Cedar Group-B Denial-Validity Firing
Priority: 🟥 CORE
Type: Prototype
Track: 🟩 VERIFY
Checkpoint: C2
Blocked by: #12, #15

**Build:** Wire the Group-B `forbid`-on-repudiation result into grading so a PED-after-36-months denial is surfaced as *impermissible under the IRDAI Master Circular*, and the agent is forbidden from hedging it (Bible §6).
**Watch out:** when neither coverage nor a denial-validity rule supports the claim, the agent must NOT manufacture a coverage argument — that's the honesty guardrail (Bible §6).
**Test:** on the sample PED case, confirm the impermissible-denial finding is produced and marked as a lead-strength argument.
**Done when:** the PED-36 denial is flagged impermissible and promoted, not hedged.

### #19: Precedent Match + Citation
Priority: 🟥 CORE
Type: Prototype
Track: 🟪 DATA
Checkpoint: C2
Blocked by: #4, #15

**Build:** Witness 3 (weekend version): map the denial reason to the right seeded precedent (*Manmohan Nanda* for disclosed-condition PED, *Gurmel Singh* for hyper-technical) and render the case name in the letter (Bible §3c, §4 Witness 3).
**Watch out:** real legal-issue retrieval (InLegalBERT + rhetorical-role + AQgR) is north-star and an open problem — for the slice a hardcoded reason→case map is the *honest* move; do NOT fake a retriever you didn't build (Bible §4 Witness 3, §9). Ombudsman awards aren't mineable — precedents come from curated SC/NCDRC text (Bible §9).
**Test:** on the sample PED denial, confirm *Manmohan Nanda* is attached and its holding is stated correctly in the letter.
**Done when:** the correct precedent is cited by name with an accurate one-line holding.

### #20: Contradiction → Lead-Argument Promotion
Priority: 🟥 CORE
Type: Prototype
Track: 🟦 AGENT
Checkpoint: C2
Blocked by: #18, #19

**Build:** The inversion: a claim that *contradicts the insurer's* reasoning (Cedar says the denial is impermissible; precedent contradicts the denial ground) is promoted to the lead argument of the letter, not dropped (Bible §4 "the inversion", §5 assembly).
**Watch out:** distinguish a contradiction against the *insurer* (promote) from a contradiction against the *user's own papers* (strip) — they take opposite paths (Bible §5).
**Test:** confirm the impermissible-PED finding + *Manmohan Nanda* appear as the opening argument of the generated letter.
**Done when:** the letter opens with the rule/precedent-backed contradiction as its lead — **C2 gate.**

---

## Phase 4 — Human Gate, Audit, Final Letter (C3)

> The governance layer. The agent drafts and grounds; it never promises a win and never submits on its own.

### #21: Human-Confirm Gate
Priority: 🟥 CORE
Type: Prototype
Track: 🟧 FRONT
Checkpoint: C3
Blocked by: #16

**Build:** A review screen where the human sees every chip and must explicitly approve before anything is final — never auto-submit (Bible §2, §11).
**Watch out:** the gate must be real, not a rubber-stamp — the whole liability posture (tool/scrivener, not legal advice) depends on a human confirming (Bible §11). Make approval a deliberate action.
**Test:** confirm nothing final is produced until the human clicks approve, and that declining a claim removes it.
**Done when:** no final letter exists until a human explicitly confirms.

### #22: Final GRO Letter Generation
Priority: 🟥 CORE
Type: Prototype
Track: 🟦 AGENT
Checkpoint: C3
Blocked by: #20, #21

**Build:** On approval, generate the rung-1 internal Grievance Redressal Officer letter — the first, highest-leverage escalation artifact (Bible §3d).
**Watch out:** the GRO letter is the "call the insurer's bluff" artifact — keep it to the grounded, rule/precedent-backed arguments only; no unverified filler (Bible §1 impact, §3d).
**Test:** approve the sample case; confirm a clean GRO letter is produced containing only kept, cited claims.
**Done when:** an approved case yields a submittable GRO grievance letter.

### #23: Hash-Chained Audit Entry + View
Priority: 🟨 SUPPORTING
Type: Prototype
Track: 🟩 VERIFY
Checkpoint: C3
Blocked by: #22

**Build:** Append a tamper-evident record to DynamoDB (each entry hashed with the previous) capturing what was claimed, what backed it, and who confirmed — plus a simple view of it (Bible §11 stretch).
**Watch out:** this is a nice-to-have — build it only once the core loop (through #22) is solid; it must not eat time the VERIFY spine needs (Bible §11).
**Test:** produce two audit entries; confirm the second's hash depends on the first and that altering entry one breaks the chain.
**Done when:** an approved case writes a verifiable hash-chained audit entry — **C3 gate.**

---

## Phase 5 — Proof & Demo (do not skip these)

### #24: Feature Freeze + Demo Data Seed
Priority: 🟥 CORE
Type: Discuss
Track: 🟧 FRONT
Checkpoint: C4
Blocked by: #23

**Build:** Call a hard feature freeze — bug-fix only. Seed clean demo data and dry-run the full loop 2–3× until it's reflexive.
**Watch out:** the instinct to add "one more feature" on the last day is how demos break. After freeze, the only work is making the existing loop bulletproof (Bible §12 Day 4).
**Test:** run the full loop cold, start to finish, twice with no manual fixes.
**Done when:** two consecutive clean end-to-end runs on seeded data.

### #25: 3-Minute Video Recorded
Priority: 🟥 CORE
Type: Prototype
Track: 🟧 FRONT
Checkpoint: C4
Blocked by: #24

**Build:** Record the video to the shot list: 0:00 problem (rationing by inconvenience) → 0:40 Beat 1 (guard strips a hallucination) → 1:10 Beat 2 (Cedar + *Manmohan Nanda* against the insurer) → 1:50 Beat 3 (no number, human confirms, letter + audit) → 2:20 architecture slide + the Learning line → 2:50 vision (Bible demo shot list, §10).
**Watch out:** there is no live demo — the video *is* the judging surface, so every beat must land inside 3 minutes. The "no number, ever" beat is the one most likely to be dropped for time; keep it — it's the honesty differentiator (Bible §2, §10).
**Test:** play it end to end; confirm all three beats are visible and every spoken claim matches what's on screen.
**Done when:** a clean sub-3-minute video shows all three beats plus the architecture and vision.

### #26: Blog on AWS Builder Center
Priority: 🟥 CORE
Type: Discuss
Track: 🟦 AGENT
Checkpoint: C4
Blocked by: #24

**Build:** Publish the blog (top-5-blogs prize) telling the Learning story: the neuro-symbolic dual-verifier is an open research problem, and the Data Gap forces binary verification over probability (Bible §0, §10).
**Watch out:** this is the "Learning" judging criterion made concrete — lead with the open-problem framing, not a feature list; it's your strongest intellectual claim (Bible §10).
**Test:** a teammate who didn't write it reads it and can restate the dual-verifier open-problem in one sentence.
**Done when:** the blog is published on AWS Builder Center with the Learning story front and center.

### #27: Challenge-Response Answers Rehearsed
Priority: 🟥 CORE
Type: Discuss
Track: 🟩 VERIFY
Checkpoint: C4
Blocked by: #24

**Build:** Rehearse cold answers to the questions judges will ask: "isn't this just an LLM wrapper?", "how do you know it won't hallucinate in a legal document?", "why don't you show a success percentage?", "is this giving legal advice / UPL?", "what about scanned/messy documents?" (Bible §8, §10, §11).
**Watch out:** name your own limits before a judge does — the "no probability because the Data Gap forbids it" answer turns an apparent weakness into the integrity story (Bible §10, §11).
**Done when:** every member can answer each challenge in one clean sentence.

### #28: Submission
Priority: 🟥 CORE
Type: Discuss
Track: 🟧 FRONT
Checkpoint: C4
Blocked by: #25, #26

**Build:** Submit: repo (README states the locked scope + AWS services used), the 3-min video, the blog link, Builder Center profiles, and the deployed URL (Ship It) or runnable build with instructions (Build It).
**Watch out:** verify the *exact* submission time and submit ~1 hour early — prior hackathon experience showed website-vs-guide deadline conflicts (Bible §12 risk register).
**Test:** open the submission from a fresh browser/account; confirm the repo, video, and blog links all resolve.
**Done when:** everything is submitted and every link resolves — **C4 gate.**

---

## Phase 6 — North-Star / Stretch (build a token version, or narrate on the slide)

### #29: NLI Grounding Upgrade on SageMaker
Priority: ⬜ SEED / PITCH-ONLY
Type: Research
Track: 🟩 VERIFY
Checkpoint: Stretch
Blocked by: #13

**Build:** Replace substring grounding with an NLI/entailment endpoint (Luna / DeBERTa-large) on SageMaker, with Semantic-F1 for paraphrase equivalence (Bible §4 Witness 1, §4A).
**Watch out:** heavier than a weekend needs — if it's not fully working, show it on the architecture slide as the upgrade path rather than half-wiring it (Bible §12).
**Done when:** either an NLI endpoint measurably beats substring on a paraphrase case, or it's carried as a stated upgrade on the slide.

### #30: AgentCore Runtime + Gateway + Policy
Priority: ⬜ SEED / PITCH-ONLY
Type: Research
Track: 🟦 AGENT
Checkpoint: Stretch
Blocked by: #15, #22

**Build:** Host the Strands agent on AgentCore Runtime, expose the verifier/Cedar/precedent as MCP tools via Gateway, and move the Cedar rules into AgentCore Policy as a managed native-Cedar governance layer (Bible §4A).
**Watch out:** production ops layer — powerful for the vision, but the weekend runs the agent locally with a Lambda verifier. Show it on the slide; build only if the core loop is already shipped (Bible §4A, §12).
**Done when:** either the agent runs on AgentCore with Policy enforcing Cedar, or it's narrated on the architecture slide.

### #31: OpenSearch Hybrid Retrieval
Priority: ⬜ SEED / PITCH-ONLY
Type: Research
Track: 🟪 DATA
Checkpoint: Stretch
Blocked by: #9

**Build:** Upgrade grounding-source and precedent retrieval to OpenSearch hybrid (BM25 + dense) so a claim resolves to the exact clause (Bible §4 Witness 1/3).
**Watch out:** the weekend fallback is plain keyword/substring — don't let index tuning eat spine time (Bible §12 cut list).
**Done when:** either hybrid retrieval returns the exact clause for a paraphrased query, or plain lookup carries the demo.

---

## Cut List (de-scope ladder — drop in this order if behind)

Drop from the top; **never** drop anything below the line.

1. #31 OpenSearch hybrid → plain keyword/substring
2. #29 NLI grounding → substring only (#13)
3. #23 audit hash-chain → plain append log
4. #14 entity-graph decomposition → sentence-level claims
5. #19 precedent retrieval → the hardcoded reason→case map (already the slice)
6. #30 AgentCore / SageMaker → local Strands + Lambda (already the plan)

— never cut below this line —

- #15 the no-LLM verifier
- #12/#18 the Cedar rule check
- #21 the human-confirm gate
- the "no probability" rule (Bible §2)

Those four *are* the project — losing any one loses the thesis.

---

## Future Work (out of scope for this build)

These aren't rejected ideas — they're real extensions carried in the Bible as north-star, not given a weekend slot. Worth naming if asked; worth returning to after the event.

1. **Escalation navigator** — the full GRO → Bima Bharosa → Ombudsman → e-Jagriti journey with per-rung deadlines and document kits, backed by AgentCore Memory for multi-week case state (Bible §3d, §7, §4A).
2. **Statutory-timeline weapon** — parse discharge/TPA timestamps and auto-draft the 3-hour-clock delay-penalty grievance against the insurer's shareholder fund (Bible §3a, §7).
3. **Multi-document contradiction hunting** — cross-check bill vs policy vs medical record; a billing/coding inconsistency is itself an appeal ground (Bible §7).
4. **Preventive denial-risk coach** — flip reactive → preventive: warn a user their proposal-form omission invites a future PED denial *before* they submit (Bible §7).
5. **Real legal-issue precedent retrieval** — InLegalBERT + rhetorical-role labelling + AQgR-style question generation over the Indian Kanoon SC/NCDRC corpus, replacing the hardcoded map (Bible §4 Witness 3, §9).
6. **Generalization to other bureaucracies** — the same draft→verify→confirm engine for EPFO/PF claims, visa RFEs, and RTI appeals (Bible §12 vision).

---

*This build map is a companion to `bible-final.md`. The Bible explains WHY; this map tells you WHAT to build, in WHAT order, how to test each piece, which Track (VERIFY/AGENT/DATA/FRONT) and demo checkpoint each belongs to, and what's genuinely future work. When a step and the Bible disagree, the Bible is the source of truth on intent — but follow this map's ticket order, Track tags, checkpoint assignments, and Test steps for execution. The Golden rule and the Ground rule are the two that keep this project honest: build nothing on an unvalidated layer, and never accept a persuasive letter as a passing test — every surviving sentence cites a rule, a case, or a source span, or it was stripped.*
