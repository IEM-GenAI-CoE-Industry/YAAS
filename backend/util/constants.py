mistral_llm = "mistral-large-latest"
gemini_llm = "gemini-2.5-flash"
openai_llm = "gpt-4.1-nano-2025-04-14"
groq_llm = "llama-3.3-70b-versatile"
local_llm = "gemma3"

# ── Thumbnail Agent ──────────────────────────────────────────────────────────
ALLOWED_EMOTIONS = {"excited", "dramatic", "professional", "friendly", "serious"}
ALLOWED_SHOT_TYPES = {"close-up", "mid-shot", "wide"}
ALLOWED_SUBJECT_POSITIONS = {"center", "left", "right"}
ALLOWED_DEPTH = {"shallow", "medium"}
ALLOWED_BACKGROUND_STYLES = {"clean", "blurred", "realistic", "studio"}
ALLOWED_LIGHTING = {"soft studio", "cinematic", "natural"}
ALLOWED_CLUTTER = {"low", "medium"}

COLOR_SCHEMES = {
    "high_contrast": {
        "primary": "#FF6B35",
        "secondary": "#004E89",
        "accent": "#FFFF00",
    },
    "educational": {
        "primary": "#4834D4",
        "secondary": "#686DE0",
        "accent": "#30336B",
    },
    "tech_blue": {
        "primary": "#0066CC",
        "secondary": "#00CCFF",
        "accent": "#FFFFFF",
    },
}

# ── Image Generation ─────────────────────────────────────────────────────────
STABILITY_API_URL = "https://api.stability.ai/v2beta/stable-image/generate/core"
STABILITY_MODEL = "sdxl-1.0"
GEMINI_IMAGE_MODEL = "gemini-2.5-flash-preview-image"

# ── Script Agent ─────────────────────────────────────────────────────────────
SCRIPT_AGENT_MAX_TOKENS = 4096

# ── Publishing Agent ─────────────────────────────────────────────────────────
YOUTUBE_UPLOAD_SCOPE = "https://www.googleapis.com/auth/youtube.upload"

# ── Analytics Agent ─────────────────────────────────────────────────────────
ANALYTICS_SCOPES = [
    "https://www.googleapis.com/auth/youtube.readonly",
    "https://www.googleapis.com/auth/yt-analytics.readonly"
]
