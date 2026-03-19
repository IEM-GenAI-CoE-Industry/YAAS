from typing import Any, Dict, List, Optional
from pydantic import BaseModel, Field


# ── Session ──────────────────────────────────────────────────────────────────

class SessionResponse(BaseModel):
    session_id: str
    state: Dict[str, Any] = {}


# ── Ideation Agent ───────────────────────────────────────────────────────────

class IdeationRequest(BaseModel):
    topic: str = Field(..., description="Video topic / niche")
    audience: str = Field(..., description="Target audience (e.g. college students)")
    region: str = Field("Global", description="Target region")
    content_format: str = Field("short-form", description="short-form or long-form")


# ── Thumbnail Agent ──────────────────────────────────────────────────────────

class ThumbnailRequest(BaseModel):
    selected_idea_number: int = Field(1, description="1-based index of the idea to use")
    enable_image_generation: bool = Field(False, description="Generate actual image via API")
    image_provider: Optional[str] = Field(None, description="gemini or stability")
    text_render_mode: str = Field("overlay", description="overlay or embedded")
    user_overrides: Optional[Dict[str, Any]] = Field(None, description="Optional manual overrides")


# ── Script Agent ─────────────────────────────────────────────────────────────
# No request body needed — reads from session state.


# ── Video Generator Agent ───────────────────────────────────────────────────

class VideoRequest(BaseModel):
    output_filename: str = Field("generated_reel.mp4", description="Name for the output .mp4 file")


# ── SEO Agent ────────────────────────────────────────────────────────────────
# No request body needed — reads from session state.


# ── Publishing Agent ────────────────────────────────────────────────────────
# No request body needed — reads from session state.


# ── Analytics Agent ──────────────────────────────────────────────────────────

class AnalyticsRequest(BaseModel):
    video_id: str = Field(..., description="YouTube video ID to analyze")
