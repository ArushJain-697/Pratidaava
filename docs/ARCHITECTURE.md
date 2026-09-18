# Architecture — scaffold ↔ bible ↔ build map

The scaffold implements the Bible's draft → verify → confirm pipeline as pure-Python
stages, each a seam for the real AWS/model implementation.

```
upload ─▶ ingest(#9) ─▶ draft(#8) ─▶ decompose(#14) ─┬─▶ W1 grounding(#13)  ┐
                                                     ├─▶ W2 cedar(#12)      ├─▶ verify(#15) ─▶ assemble(#16/#20) ─▶ human(#21) ─▶ letter+audit(#22/#23)
                                                     └─▶ W3 precedent(#19)  ┘
```

The two invariants that are the whole thesis, enforced in code:

1. `verify.py` makes **no generative model call** — `tests/test_invariants.py` greps it.
2. **No probability** is ever emitted — the schema has no score field; a test asserts it.

## Where each AWS service lands (Bible §4A)

- **Bedrock** → `draft.py` (generative brain)
- **SageMaker** → `grounding.py` NLI endpoint (#29), `precedent.py` InLegalBERT
- **Strands** → the agent loop wrapping `run.py`
- **AgentCore** → Runtime hosts it, Gateway exposes the witnesses as MCP tools, **Policy**
  runs `coverage.cedar` natively, Memory holds case state, Observability traces it
- **Cedar / AVP** → `coverage.cedar` (source of truth) via `cedar.py`
- **S3 / DynamoDB / OpenSearch / API Gateway / Amplify** → ingest, audit, retrieval, API, UI

Weekend build runs the agent locally with the Lambda-shaped verifier and a Cedar file;
the AgentCore/SageMaker versions are the north-star shown on the architecture slide.
