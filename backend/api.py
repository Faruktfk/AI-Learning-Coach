from typing import List, Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

from services.core.api_state_machine import SessionStore


app = FastAPI(
    title="AI Learning Coach API",
    description="REST API wrapper for the Wikipedia-based adaptive learning state machine.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For local development. Restrict this later in production.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

store = SessionStore()


class StepRequest(BaseModel):
    message: Optional[str] = Field(
        default=None,
        description="Text input for states that expect text, e.g. topic, ja/nein, nochmal/skip.",
    )
    answers: Optional[List[int]] = Field(
        default=None,
        description="Selected option numbers for quiz evaluation, e.g. [1, 3, 2, 4].",
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/sessions")
def create_session():
    session = store.create()
    return {
        "session_id": session.session_id,
        "session": session.snapshot(),
        "next": {
            "endpoint": f"/sessions/{session.session_id}/step",
            "method": "POST",
            "body_example": {"message": "Schwarzes Loch"},
        },
    }


@app.get("/sessions")
def list_sessions():
    return {"sessions": store.list()}


@app.get("/sessions/{session_id}")
def get_session(session_id: str):
    try:
        session = store.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    return {"session": session.snapshot()}


@app.post("/sessions/{session_id}/step")
def step_session(session_id: str, request: StepRequest):
    try:
        session = store.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        return session.step(input_message=request.message, answers=request.answers)
    except Exception as exc:
        raise HTTPException(status_code=500, detail=str(exc))


@app.delete("/sessions/{session_id}")
def delete_session(session_id: str):
    try:
        store.get(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail="Session not found")

    store.delete(session_id)
    return {"deleted": True, "session_id": session_id}
