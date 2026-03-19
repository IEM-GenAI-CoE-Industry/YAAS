"""
In-memory session store for YAAS pipeline runs.
Each session holds a global_state dict that accumulates results as agents run.
"""

import uuid
from typing import Dict

_sessions: Dict[str, dict] = {}


def create_session(initial_state: dict | None = None) -> str:
    """Create a new session and return its ID."""
    session_id = str(uuid.uuid4())
    _sessions[session_id] = initial_state or {}
    return session_id


def get_session(session_id: str) -> dict:
    """Return the global_state for a session. Raises KeyError if not found."""
    if session_id not in _sessions:
        raise KeyError(f"Session '{session_id}' not found")
    return _sessions[session_id]


def update_session(session_id: str, state: dict) -> None:
    """Overwrite the global_state for an existing session."""
    if session_id not in _sessions:
        raise KeyError(f"Session '{session_id}' not found")
    _sessions[session_id] = state


def delete_session(session_id: str) -> None:
    """Remove a session."""
    _sessions.pop(session_id, None)


def list_sessions() -> list[str]:
    """Return all active session IDs."""
    return list(_sessions.keys())
