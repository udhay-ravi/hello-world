"""FastAPI server — connects the Parent Agent, Worker Agent, and Web UI."""

from __future__ import annotations

import uuid

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles

from app.agents.parent_agent import get_current_question, process_answer
from app.agents.worker_agent import generate_diagram, generate_summary
from app.models import AgentMessage, QuestionStep, SessionState, UserResponse

app = FastAPI(title="System Design Architect Agent")

# In-memory session store (swap for Redis in production)
sessions: dict[str, SessionState] = {}


@app.post("/api/session", response_model=AgentMessage)
async def create_session() -> AgentMessage:
    """Create a new design session and return the first question."""
    sid = uuid.uuid4().hex[:12]
    state = SessionState(session_id=sid)
    sessions[sid] = state
    msg = get_current_question(state)
    msg.text = f"[Session `{sid}` created]\n\n{msg.text}"
    return AgentMessage(
        text=msg.text,
        options=msg.options,
        is_free_text=msg.is_free_text,
        diagram=None,
        is_complete=False,
    )


@app.post("/api/respond", response_model=AgentMessage)
async def respond(payload: UserResponse) -> AgentMessage:
    """Accept a user answer, advance state, return next question or diagram."""
    state = sessions.get(payload.session_id)
    if state is None:
        return AgentMessage(text="Session not found. Please start a new session.")

    # Parent agent processes the answer
    state = process_answer(state, payload.answer)
    sessions[payload.session_id] = state

    # Check if all questions are answered
    if state.current_step == QuestionStep.COMPLETE:
        # Hand off to Worker Agent
        diagram = generate_diagram(state)
        summary = generate_summary(state)
        state.diagram_mermaid = diagram
        sessions[payload.session_id] = state

        return AgentMessage(
            text=summary,
            diagram=diagram,
            is_complete=True,
        )

    # Otherwise, return the next question
    return get_current_question(state)


@app.get("/api/session/{session_id}")
async def get_session(session_id: str):
    """Return current session state (for debugging)."""
    state = sessions.get(session_id)
    if state is None:
        return {"error": "not found"}
    return state.model_dump()


@app.get("/", response_class=HTMLResponse)
async def index():
    """Serve the single-page web UI."""
    with open("app/templates/index.html") as f:
        return HTMLResponse(content=f.read())
