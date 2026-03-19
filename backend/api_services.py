import logging
import traceback

from fastapi import APIRouter, HTTPException

import session_store
from base_requests import (
    AnalyticsRequest,
    IdeationRequest,
    SessionResponse,
    ThumbnailRequest,
    VideoRequest,
)

from ideation_agent.ideation_service import run_ideation_agent
from thumbnail_agent.thumbnail_service import run_thumbnail_agent
from script_agent.script_service import run_script_agent
from video_generator_agent.run_video_generator import run_video_generator_agent
from seo_agent.seo_service import run_seo_agent

# Publishing and Analytics agents are imported lazily inside their endpoints
# because they depend on google-api-python-client / google-auth-oauthlib
# which may not be installed yet.

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_router = APIRouter(tags=["YAAS API Services"])


# ── Helper ───────────────────────────────────────────────────────────────────

def _get_state_or_404(session_id: str) -> dict:
    """Fetch session state or raise HTTP 404."""
    try:
        return session_store.get_session(session_id)
    except KeyError:
        raise HTTPException(status_code=404, detail=f"Session '{session_id}' not found")


# ── Session Management ───────────────────────────────────────────────────────

@api_router.post("/session", response_model=SessionResponse)
async def create_session():
    """Create a new pipeline session."""
    session_id = session_store.create_session()
    return SessionResponse(session_id=session_id, state={})


@api_router.get("/session/{session_id}", response_model=SessionResponse)
async def get_session(session_id: str):
    """Get the full state of a session (inspect intermediate results)."""
    state = _get_state_or_404(session_id)
    return SessionResponse(session_id=session_id, state=state)


# ── 1. Ideation Agent ───────────────────────────────────────────────────────

@api_router.post("/session/{session_id}/ideation", response_model=SessionResponse)
async def ideation(session_id: str, req: IdeationRequest):
    """Generate video ideas based on topic, audience, and region."""
    state = _get_state_or_404(session_id)

    state["topic"] = req.topic
    state["audience"] = req.audience
    state["region"] = req.region
    state["content_format"] = req.content_format

    try:
        state = run_ideation_agent(state)
    except Exception as e:
        logger.error(f"Ideation Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Ideation Agent error: {str(e)}")

    session_store.update_session(session_id, state)
    return SessionResponse(session_id=session_id, state=state)


# ── 2. Thumbnail Agent ──────────────────────────────────────────────────────

@api_router.post("/session/{session_id}/thumbnail", response_model=SessionResponse)
async def thumbnail(session_id: str, req: ThumbnailRequest):
    """Generate a thumbnail spec (and optionally an image) from the selected idea."""
    state = _get_state_or_404(session_id)

    state["selected_idea_number"] = req.selected_idea_number
    state["enable_image_generation"] = req.enable_image_generation
    state["image_provider"] = req.image_provider
    state["text_render_mode"] = req.text_render_mode
    state["user_overrides"] = req.user_overrides

    try:
        state = run_thumbnail_agent(state)
    except Exception as e:
        logger.error(f"Thumbnail Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Thumbnail Agent error: {str(e)}")

    session_store.update_session(session_id, state)
    return SessionResponse(session_id=session_id, state=state)


# ── 3. Script Agent ─────────────────────────────────────────────────────────

@api_router.post("/session/{session_id}/script", response_model=SessionResponse)
async def script(session_id: str):
    """Generate a script timeline from the thumbnail data."""
    state = _get_state_or_404(session_id)

    try:
        state = run_script_agent(state)
    except Exception as e:
        logger.error(f"Script Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Script Agent error: {str(e)}")

    session_store.update_session(session_id, state)
    return SessionResponse(session_id=session_id, state=state)


# ── 4. Video Generator Agent ────────────────────────────────────────────────

@api_router.post("/session/{session_id}/video", response_model=SessionResponse)
async def video(session_id: str, req: VideoRequest = VideoRequest()):
    """Generate a video reel using Veo 3 from the script timeline."""
    state = _get_state_or_404(session_id)

    state["output_filename"] = req.output_filename

    try:
        state = run_video_generator_agent(state)
    except Exception as e:
        logger.error(f"Video Generator Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Video Generator error: {str(e)}")

    session_store.update_session(session_id, state)
    return SessionResponse(session_id=session_id, state=state)


# ── 5. SEO Agent ────────────────────────────────────────────────────────────

@api_router.post("/session/{session_id}/seo", response_model=SessionResponse)
async def seo(session_id: str):
    """Generate SEO metadata (title, description, tags) from the script timeline."""
    state = _get_state_or_404(session_id)

    try:
        state = run_seo_agent(state)
    except Exception as e:
        logger.error(f"SEO Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"SEO Agent error: {str(e)}")

    session_store.update_session(session_id, state)
    return SessionResponse(session_id=session_id, state=state)


# ── 6. Publishing Agent ─────────────────────────────────────────────────────

@api_router.post("/session/{session_id}/publish", response_model=SessionResponse)
async def publish(session_id: str):
    """Upload the generated video to YouTube with SEO metadata."""
    state = _get_state_or_404(session_id)

    try:
        from publishing_agent.publishing_service import run_publishing_agent
        state = run_publishing_agent(state)
    except Exception as e:
        logger.error(f"Publishing Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Publishing Agent error: {str(e)}")

    session_store.update_session(session_id, state)
    return SessionResponse(session_id=session_id, state=state)


# ── 7. Analytics Agent (standalone) ─────────────────────────────────────────

@api_router.post("/analytics", response_model=SessionResponse)
async def analytics(req: AnalyticsRequest):
    """Analyze an existing YouTube video's performance (standalone, no session needed)."""
    state = {"video_id": req.video_id}

    try:
        from analytics_agent.analytics_agent_service import run_analytics_agent
        state = run_analytics_agent(state)
    except Exception as e:
        logger.error(f"Analytics Agent failed: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Analytics Agent error: {str(e)}")

    return SessionResponse(session_id="standalone", state=state)


# ── 8. OAuth Web Flow ───────────────────────────────────────────────────────

import json
import os
from fastapi import Request
from fastapi.responses import RedirectResponse, HTMLResponse

# Required for localhost testing without HTTPS
os.environ['OAUTHLIB_INSECURE_TRANSPORT'] = '1'

@api_router.get("/auth/youtube/login")
async def youtube_login(request: Request):
    """Generate the Google OAuth URL and redirect the user."""
    from google_auth_oauthlib.flow import Flow
    
    redirect_uri = str(request.base_url).rstrip("/") + "/YAAS/content/v1/auth/youtube/callback"
    
    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly"
        ],
        redirect_uri=redirect_uri
    )
    auth_url, _ = flow.authorization_url(
        access_type='offline',
        include_granted_scopes='true',
        login_hint='',
    )
    # Force account picker by appending prompt parameter directly
    auth_url += '&prompt=select_account+consent'
    return RedirectResponse(auth_url)


@api_router.get("/auth/youtube/callback")
async def youtube_callback(request: Request):
    """Handle the Google OAuth redirect and save token.json."""
    from google_auth_oauthlib.flow import Flow

    redirect_uri = str(request.base_url).rstrip("/") + "/YAAS/content/v1/auth/youtube/callback"
    state = request.query_params.get("state")

    flow = Flow.from_client_secrets_file(
        'client_secrets.json',
        scopes=[
            "https://www.googleapis.com/auth/youtube.upload",
            "https://www.googleapis.com/auth/youtube.readonly"
        ],
        redirect_uri=redirect_uri,
        state=state,
    )
    
    # fetch_token requires the full URL
    flow.fetch_token(authorization_response=str(request.url))
    
    creds = flow.credentials
    
    token_data = {
        "token": creds.token,
        "refresh_token": creds.refresh_token,
        "token_uri": creds.token_uri,
        "client_id": creds.client_id,
        "client_secret": creds.client_secret,
        "scopes": list(creds.scopes) if creds.scopes else [],
        "universe_domain": "googleapis.com",
        "account": "",
        "expiry": creds.expiry.isoformat() if hasattr(creds, 'expiry') and creds.expiry else None,
    }
    
    with open("token.json", "w") as f:
        json.dump(token_data, f, indent=4)
        
    html = """
    <html>
    <head><style>body { font-family: sans-serif; text-align: center; padding: 50px; background: #0f172a; color: white; }</style></head>
    <body>
    <h2>✅ Authentication Successful!</h2>
    <p>You can now close this window and click <b>Publish to YouTube</b> again in the pipeline.</p>
    <script>
        setTimeout(() => window.close(), 3000);
    </script>
    </body>
    </html>
    """
    return HTMLResponse(html)