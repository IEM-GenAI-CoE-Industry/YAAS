# YAAS Frontend Handoff — Complete Backend Context

## Project Overview

**YAAS (YouTube As A Service)** is a college project that automates the entire YouTube content creation pipeline using AI agents. The backend is a **FastAPI** server with **7 sequential agents** that each do one step of the pipeline:

```
Ideation → Thumbnail → Script → Video Generation → SEO → Publishing
                                                              ↕
                                                         Analytics (standalone)
```

The backend is **fully built and working**. The frontend needs to be a local demo UI that calls the backend endpoints step-by-step and displays results.

---

## Backend Server

- **Framework:** FastAPI
- **Port:** `8001`
- **Start command:** `cd backend && python app.py`
- **API prefix:** `/YAAS/content/v1`
- **Swagger UI:** `http://localhost:8001/docs`
- **CORS:** Already configured for `localhost:3000`, `localhost:5173`, `localhost:8000`

---

## Session-Based Architecture

The backend uses **in-memory sessions**. Each session holds a `global_state` dict that accumulates results as agents run sequentially.

**Flow:**
1. Frontend calls `POST /session` → gets a `session_id`
2. Frontend calls each agent endpoint in order, passing the `session_id`
3. Each agent reads from the session, adds its output, and returns the updated state
4. Frontend can call `GET /session/{id}` at any time to inspect the full state

---

## API Endpoints — Complete Reference

### 1. Create Session
```
POST /YAAS/content/v1/session
```
**Request body:** None  
**Response:**
```json
{
  "session_id": "uuid-string",
  "state": {}
}
```

### 2. Get Session State
```
GET /YAAS/content/v1/session/{session_id}
```
**Response:** Full [SessionResponse](file:///c:/Users/sujaa/Documents/College%20Projects/YAAS/backend/base_requests.py#7-10) with all accumulated state from agents that have run.

---

### 3. Ideation Agent
```
POST /YAAS/content/v1/session/{session_id}/ideation
```
**Request body:**
```json
{
  "topic": "AI in education",
  "audience": "college students",
  "region": "India",
  "content_format": "short-form"
}
```
- `topic` (required): Video topic/niche
- [audience](file:///c:/Users/sujaa/Documents/College%20Projects/YAAS/backend/analytics_agent/analytics_agent_service.py#168-235) (required): Target audience
- `region` (optional, default `"Global"`): Target region
- `content_format` (optional, default `"short-form"`): `"short-form"` or `"long-form"`

**Adds to state:**
```json
{
  "topic": "...",
  "audience": "...",
  "region": "...",
  "content_format": "...",
  "ideas": "1. Idea Title\n   Description: ...\n\n2. Idea Title\n   Description: ..."
}
```
The [ideas](file:///c:/Users/sujaa/Documents/College%20Projects/YAAS/backend/thumbnail_agent/thumbnail_service.py#11-32) field is a **formatted text string** with numbered ideas. The Thumbnail Agent parses this internally.

---

### 4. Thumbnail Agent
```
POST /YAAS/content/v1/session/{session_id}/thumbnail
```
**Request body:**
```json
{
  "selected_idea_number": 1,
  "enable_image_generation": false,
  "image_provider": null,
  "text_render_mode": "overlay",
  "user_overrides": null
}
```
- `selected_idea_number` (default `1`): 1-based index of which idea from ideation to use
- `enable_image_generation` (default `false`): Set `true` to actually generate an image via Stability/Gemini API
- `image_provider` (optional): `"gemini"` or `"stability"`
- `text_render_mode` (default `"overlay"`): `"overlay"` or `"embedded"`
- [user_overrides](file:///c:/Users/sujaa/Documents/College%20Projects/YAAS/backend/thumbnail_agent/thumbnail_nodes/apply_user_overrides.py#21-90) (optional): Dict of manual overrides for thumbnail spec fields

**Adds to state:**
```json
{
  "final_idea": {
    "title": "Selected Idea Title",
    "description": "Selected idea description"
  },
  "thumbnail": {
    "idea_title": "...",
    "idea_description": "...",
    "audience": "...",
    "region": "...",
    "content_format": "...",
    "thumbnail_spec": {
      "subject": { "type": "person", "emotion": "excited", "shot_type": "close-up", "position": "center" },
      "background": { "style": "blurred", "depth": "shallow", "lighting": "cinematic", "clutter": "low" },
      "emotion_style": { "mood": "...", "energy": "high" },
      "color_palette": { "scheme": "high_contrast", "primary": "#FF6B35", "secondary": "#004E89", "accent": "#FFFF00" },
      "composition": { "layout": "...", "contrast_level": "high" },
      "text": { "content": "Main Text", "font_style": "bold", "placement": "top-center", "size": "large" }
    },
    "thumbnail_text": "Main Text",
    "image_prompt": "A detailed prompt for image generation...",
    "image_provider": "stability",
    "image_base64": "base64-encoded-png-string-or-null",
    "text_render_mode": "overlay"
  }
}
```

> **Note:** `image_base64` is only populated when `enable_image_generation` is `true`. The frontend can display this as: `<img src="data:image/png;base64,{image_base64}" />`

---

### 5. Script Agent
```
POST /YAAS/content/v1/session/{session_id}/script
```
**Request body:** None (reads from session state)

**Adds to state:**
```json
{
  "script_timeline": {
    "video_meta": {
      "title": "Video Title",
      "tone": "cinematic dramatic",
      "duration_seconds": 10
    },
    "render_hints": {
      "aspect_ratio": "9:16",
      "color_palette": { "primary": "#...", "accent": "#..." },
      "font": "bold sans-serif"
    },
    "timeline": [
      {
        "scene_number": 1,
        "shot_type": "close-up",
        "visual_description": "A person looking at camera...",
        "voiceover": { "text": "Scene narration text...", "tone": "dramatic" },
        "text_overlay": { "content": "HOOK TEXT", "position": "center", "animation": "fade-in" },
        "audio": { "music_mood": "epic", "sfx": ["whoosh"] }
      }
    ]
  }
}
```

---

### 6. Video Generator Agent
```
POST /YAAS/content/v1/session/{session_id}/video
```
**Request body:**
```json
{
  "output_filename": "generated_reel.mp4"
}
```
- [output_filename](file:///c:/Users/sujaa/Documents/College%20Projects/YAAS/backend/video_generator_agent/test_video_generator_service.py#498-503) (default `"generated_reel.mp4"`): Name for the saved video file

**Adds to state:**
```json
{
  "video_path": "c:/Users/.../backend/output/generated_reel.mp4"
}
```

> **Note:** This calls Google's Veo 3.1 API and takes 1-3 minutes. Requires `GEMINI_API_KEY` env var.

---

### 7. SEO Agent
```
POST /YAAS/content/v1/session/{session_id}/seo
```
**Request body:** None

**Adds to state:**
```json
{
  "seo_metadata": {
    "title": "Optimized YouTube Title (max 60 chars)",
    "description": "Engaging video description with keywords...",
    "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"],
    "privacy": "private",
    "scheduled_time": "2026-03-19T21:00:00Z"
  }
}
```

---

### 8. Publishing Agent
```
POST /YAAS/content/v1/session/{session_id}/publish
```
**Request body:** None

**Adds to state:**
```json
{
  "publish_response": {
    "id": "youtube-video-id",
    "snippet": { "title": "...", "description": "..." },
    "status": { "privacyStatus": "private" }
  }
}
```

> **Note:** Requires YouTube OAuth `token.json` in `backend/`. Will return an error if not configured.

---

### 9. Analytics Agent (Standalone)
```
POST /YAAS/content/v1/analytics
```
**Request body:**
```json
{
  "video_id": "dQw4w9WgXcQ"
}
```

**Response state:**
```json
{
  "video_id": "dQw4w9WgXcQ",
  "analytics": {
    "metrics": {
      "video_id": "...",
      "title": "Video Title",
      "views": 10000,
      "likes": 400,
      "comments": 60,
      "watch_time": 5000.0,
      "average_view_duration": 180.0,
      "engagement_rate": 0.046,
      "click_through_rate": null,
      "demographics": {
        "age": { "18-24": 0.4, "25-34": 0.3 },
        "gender": { "male": 0.6, "female": 0.4 },
        "location": { "US": 0.5, "IN": 0.3 }
      },
      "traffic_sources": {
        "youtube search": 0.5,
        "suggested videos": 0.3
      }
    },
    "insights": [
      {
        "insight_type": "High Engagement",
        "message": "Strong engagement rate of 0.046.",
        "recommendation": "Continue with similar content style.",
        "priority": "low"
      }
    ]
  }
}
```

> **Note:** Requires `client_secrets.json` in `backend/analytics_agent/` and triggers an OAuth browser popup.

---

## Error Handling

All agent endpoints return `HTTP 500` with a JSON body on failure:
```json
{
  "detail": "Ideation Agent error: <error message>"
}
```

Session-not-found returns `HTTP 404`:
```json
{
  "detail": "Session 'bad-uuid' not found"
}
```

---

## Typical Frontend Flow (Sample API Call Sequence)

```
1. POST /session                           → get session_id
2. POST /session/{id}/ideation             → user enters topic, audience, region
3. Display ideas to user, let them pick one
4. POST /session/{id}/thumbnail            → pass selected_idea_number
5. Display thumbnail spec + image (if generated)
6. POST /session/{id}/script               → auto, no user input needed
7. Display script timeline scenes
8. POST /session/{id}/video                → long-running (show spinner)
9. Display video player with generated .mp4
10. POST /session/{id}/seo                 → auto
11. Display generated title/description/tags
12. POST /session/{id}/publish             → requires OAuth setup
13. Show success or "OAuth not configured" message

Separately:
14. POST /analytics                        → user enters a YouTube video ID
15. Display metrics dashboard
```

---

## Project Directory Structure

```
YAAS/
├── backend/
│   ├── app.py                          # FastAPI entry point (port 8001)
│   ├── api_services.py                 # All 9 API endpoints
│   ├── session_store.py                # In-memory session management
│   ├── base_requests.py                # Pydantic request/response models
│   ├── config.py                       # CORS, API prefix settings
│   ├── .env                            # API keys (not committed to git)
│   ├── requirements.txt                # All Python dependencies
│   ├── output/                         # Generated .mp4 video files
│   ├── util/
│   │   ├── constants.py                # All constants
│   │   ├── system_prompt.py            # All LLM prompts
│   │   ├── llm_factory.py             # LLM provider abstraction
│   │   └── utility.py                  # Helper functions
│   ├── ideation_agent/                 # Agent 1
│   ├── thumbnail_agent/                # Agent 2
│   ├── script_agent/                   # Agent 3
│   ├── video_generator_agent/          # Agent 4
│   ├── seo_agent/                      # Agent 5
│   ├── publishing_agent/               # Agent 6
│   ├── analytics_agent/                # Agent 7
│   ├── tests/                          # Test files
│   └── venv/                           # Python virtual environment
├── frontend/                           # Frontend code goes here
├── .gitignore
└── README.md
```

---

## Key Constraints for the Frontend

1. **This is a local demo, not a production app.** Keep it simple but visually polished.
2. **The pipeline is sequential** — each agent depends on the previous one's output. The UI should enforce this order (disable steps that haven't been reached yet).
3. **Video generation takes 1-3 minutes** — the UI needs a loading/progress state for this step.
4. **Publishing and Analytics require OAuth** — these may not be configured. The UI should handle errors gracefully (show a friendly message, not crash).
5. **The `image_base64` field** can be rendered directly as `<img src="data:image/png;base64,..." />`.
6. **CORS is already configured** for `localhost:3000` and `localhost:5173`.
