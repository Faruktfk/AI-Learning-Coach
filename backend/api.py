from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.tools.handout_pdf import HANDOUT_DIR
from services.core.api_state_machine import LearningSession, StepResult


app = FastAPI(title="MyWikiGPT API", version="1.0.0", root_path="/api/v1")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

SESSIONS: Dict[str, LearningSession] = {}


class StepRequest(BaseModel):
    message: Optional[str] = None
    answers: Optional[List[int]] = None


class SessionResponse(BaseModel):
    session_id: str
    state_before: str
    state_after: str
    message: str
    requires_input: bool
    input_kind: Optional[str] = None
    data: Dict[str, Any]
    download_url: Optional[str] = None
    session: Dict[str, Any]


def to_response(result: StepResult) -> SessionResponse:
    return SessionResponse(
        session_id=result.session_id,
        state_before=result.state_before,
        state_after=result.state_after,
        message=result.message,
        requires_input=result.requires_input,
        input_kind=result.input_kind,
        data=result.data,
        download_url=result.download_url,
        session=result.session,
    )


@app.get("/health")
def health() -> Dict[str, str]:
    return {"status": "ok"}


@app.post("/sessions", response_model=SessionResponse)
def create_session() -> SessionResponse:
    session = LearningSession()
    SESSIONS[session.session_id] = session
    return to_response(session.initial_response())


@app.get("/sessions/{session_id}")
def get_session(session_id: str) -> Dict[str, Any]:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")
    return session.snapshot()


@app.post("/sessions/{session_id}/step", response_model=SessionResponse)
def step_session(session_id: str, request: StepRequest) -> SessionResponse:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session.step(message=request.message, answers=request.answers)
    return to_response(result)


@app.post("/sessions/{session_id}/handout", response_model=SessionResponse)
def generate_handout_for_session(session_id: str) -> SessionResponse:
    session = SESSIONS.get(session_id)

    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    result = session.generate_handout_now()
    return to_response(result)


@app.get("/handouts/{filename}")
def download_handout_file(filename: str):
    """
    Downloads a generated handout PDF by filename.

    Important:
    This endpoint does NOT depend on the in-memory session store.
    If the PDF exists on disk, it can be downloaded.
    """

    # Prevent path traversal like ../../secret.txt
    safe_name = Path(filename).name

    if safe_name != filename:
        raise HTTPException(status_code=400, detail="Invalid filename")

    file_path = HANDOUT_DIR / safe_name

    if not file_path.exists() or not file_path.is_file():
        raise HTTPException(status_code=404, detail="Handout file not found")

    if file_path.suffix.lower() != ".pdf":
        raise HTTPException(status_code=400, detail="Only PDF files can be downloaded")

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=safe_name,
    )