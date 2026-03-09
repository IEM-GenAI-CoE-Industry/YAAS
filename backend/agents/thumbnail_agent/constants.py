"""
Centralized enum definitions for Thumbnail Agent.
"""

# Emotion / mood
ALLOWED_EMOTIONS = {
    "excited",
    "dramatic",
    "professional",
    "friendly",
    "serious",
}

# Subject framing
ALLOWED_SHOT_TYPES = {"close-up", "mid-shot", "wide"}

# Composition
ALLOWED_SUBJECT_POSITIONS = {"center", "left", "right"}
ALLOWED_DEPTH = {"shallow", "medium"}

# Background
ALLOWED_BACKGROUND_STYLES = {"clean", "blurred", "realistic", "studio"}
ALLOWED_LIGHTING = {"soft studio", "cinematic", "natural"}
ALLOWED_CLUTTER = {"low", "medium"}