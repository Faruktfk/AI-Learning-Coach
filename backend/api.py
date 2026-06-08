from __future__ import annotations

from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel

from services.core.api_state_machine import LearningSession, StepResult


app = FastAPI(title="AI Learning Coach API", version="1.0.0")

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


@app.get("/sessions/{session_id}/handout.pdf")
def download_handout(session_id: str) -> FileResponse:
    session = SESSIONS.get(session_id)
    if session is None:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.handout_pdf_path is None:
        # If the session is already in HANDOUT, generate it now.
        if session.get_current_state() == "HANDOUT":
            session.step()
        else:
            raise HTTPException(status_code=404, detail="Handout is not ready yet")

    path = Path(session.handout_pdf_path)
    if not path.exists():
        raise HTTPException(status_code=404, detail="Handout file not found")

    return FileResponse(
        path=str(path),
        media_type="application/pdf",
        filename=path.name,
    )
