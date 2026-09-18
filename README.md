# Claim-Appeal Agent — Scaffold (walking skeleton)

Locked scope (Bible §12): **one denial type — PED denial after 36 months of continuous
cover.** One policy, one synthetic denial letter, two seeded precedents. Do not widen
this without a decision.

This is the walking skeleton from the build map (tickets #5, #7, and Phase 1), runnable
**offline, end-to-end, with no AWS and no API keys.** The generative and cloud pieces are
clean stubs with a `SEAM` comment marking exactly where the real thing plugs in.

## Run it

Zero-setup pipeline demo (needs only `pydantic`):

```bash
pip install pydantic
python demo.py
```

API + UI shell:

```bash
./run.sh              # or: pip install -r requirements.txt && uvicorn backend.app:app --port 8000
# open http://localhost:8000  and click "Run sample appeal"
```

Invariant tests (the Ground rule, enforced):

```bash
python tests/test_invariants.py       # or: python -m pytest -q
```

## What already works (not just stubs)

- **The no-LLM verifier** (`verify.py`) is real and pure — it combines grounding + Cedar +
  precedent into a corroboration tier with **no model call and no probability**. A test
  greps the module to prove no model call ever leaks in.
- **Beat 1** — the draft contains a planted fabrication (a cite to policy clause §7.9, which
  doesn't exist); the grounding check strips it before it reaches the letter.
- **Beat 2** — the PED-after-36-months denial is flagged impermissible under the IRDAI rule
  and promoted to the lead argument, with *Manmohan Nanda* attached.
- The final GRO letter contains only kept, cited claims. No percentage anywhere.

## What is a stub (with a `SEAM` marker)

| File | Ticket | Replace with |
|---|---|---|
| `backend/pipeline/draft.py` | #8 | Bedrock draft (Strands agent loop) |
| `backend/pipeline/decompose.py` | #14 | entity-pair decomposition |
| `backend/pipeline/cedar.py` | #12 | real Cedar (open-source engine / AgentCore Policy / AVP) |
| `backend/pipeline/grounding.py` | #13 → #29 | NLI entailment endpoint on SageMaker |
| `backend/pipeline/precedent.py` | #19 | InLegalBERT legal-issue retrieval over Indian Kanoon |
| `backend/pipeline/ingest.py` | #9 → #31 | S3 + OpenSearch hybrid retrieval |
| `backend/app.py` | #11 → #30 | AgentCore Runtime + Gateway |

`policies/coverage.cedar` is the **source of truth** for the rules; `cedar.py` is a Python
stand-in that must stay behavior-identical to it.

## Layout

```
backend/
  schema.py            # #7 — the claim schema (no probability field, by design)
  app.py               # #11 — FastAPI: /appeal, /health, serves the UI
  pipeline/
    ingest.py          # #9   load corpus, resolve refs
    draft.py           # #8   draft -> letter + claims (plants the fabrication)
    decompose.py       # #14  entity-pair decomposition
    grounding.py       # #13  Witness 1 (substring; NLI is the upgrade)
    cedar.py           # #12  Witness 2 (rules)
    precedent.py       # #19  Witness 3 (precedent)
    verify.py          # #15  THE no-LLM verifier + corroboration grading
    assemble.py        # #16/#20  strip + promote lead argument
    run.py             # #11  end-to-end orchestration
  data/                # #4   sample policy, denial letter, precedents (clean text)
policies/coverage.cedar# #12  Cedar rules (source of truth)
frontend/index.html    # #10  minimal UI shell
tests/test_invariants.py  # enforces the Ground rule
demo.py                # offline end-to-end demo
```

See `bible-final.md` for the WHY and `Claim_Appeal_Build_Map.md` for ticket order.
