"""
Ticket #11 — the API that fronts the pipeline, plus serving the UI shell (#10).

    GET  /            -> the frontend
    GET  /health      -> {"status": "ok"}
    POST /appeal      -> run the pipeline, return AppealResult as JSON

SEAM (later): this handler is what moves onto AgentCore Runtime behind API Gateway,
with the pipeline stages exposed to a Strands agent as MCP tools via Gateway (#30).
"""
from __future__ import annotations

import os
from typing import Optional

from fastapi import FastAPI
from fastapi.responses import FileResponse
from pydantic import BaseModel

from backend.pipeline.run import run_appeal

app = FastAPI(title="Claim-Appeal Agent (scaffold)")

FRONTEND = os.path.join(os.path.dirname(__file__), "..", "frontend", "index.html")


class AppealRequest(BaseModel):
    # Optional overrides; when omitted, the sample PED-after-36-months case is used.
    denial_text: Optional[str] = None
    policy_text: Optional[str] = None


@app.get("/health")
def health() -> dict:
    return {"status": "ok"}


@app.post("/appeal")
def appeal(req: AppealRequest) -> dict:
    result = run_appeal(denial_text=req.denial_text, policy_text=req.policy_text)
    return result.model_dump()


@app.get("/")
def index() -> FileResponse:
    return FileResponse(FRONTEND)
