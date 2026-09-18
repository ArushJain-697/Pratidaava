"""Pipeline stages, in dependency order:

    ingest -> draft -> decompose -> verify (grounding + cedar + precedent -> tier) -> assemble

Every stage is a pure-Python module with a clean seam where the real AWS/model
implementation plugs in. The verifier contains NO generative model call, by design.
"""
