import re
from typing import Any, Dict

from agents.thumbnail_agent.thumbnail_state import ThumbnailState

from agents.thumbnail_agent.constants import (
    ALLOWED_EMOTIONS,
    ALLOWED_SHOT_TYPES,
    ALLOWED_SUBJECT_POSITIONS,
    ALLOWED_DEPTH,
    ALLOWED_BACKGROUND_STYLES,
    ALLOWED_LIGHTING,
    ALLOWED_CLUTTER,
)


def _is_valid_hex(value: str) -> bool:
    return isinstance(value, str) and bool(re.fullmatch(r"#([A-Fa-f0-9]{6})", value))


def apply_user_overrides(state: ThumbnailState) -> ThumbnailState:
    spec = state.get("thumbnail_spec")
    overrides: Dict[str, Any] = state.get("user_overrides") or {}

    if not isinstance(spec, dict):
        return state

    subject = spec.setdefault("subject", {})
    background = spec.setdefault("background", {})
    composition = spec.setdefault("composition", {})
    palette = spec.setdefault("color_palette", {})
    text = spec.setdefault("text", {})

    # ---- Emotion override ----
    emotion = overrides.get("emotion_style")
    if emotion in ALLOWED_EMOTIONS:
        spec["emotion_style"] = emotion

    # ---- Shot type override ----
    shot_type = overrides.get("shot_type")
    if shot_type in ALLOWED_SHOT_TYPES:
        subject["shot_type"] = shot_type

    # ---- Background style override ----
    bg_style = overrides.get("background_style")
    if bg_style in ALLOWED_BACKGROUND_STYLES:
        background["style"] = bg_style

    # ---- Lighting override ----
    lighting = overrides.get("lighting")
    if lighting in ALLOWED_LIGHTING:
        background["lighting"] = lighting

    # ---- Subject position override ----
    position = overrides.get("subject_position")
    if position in ALLOWED_SUBJECT_POSITIONS:
        composition["subject_position"] = position

    # ---- Depth override ----
    depth = overrides.get("depth")
    if depth in ALLOWED_DEPTH:
        composition["depth"] = depth

    # ---- Clutter override ----
    clutter = overrides.get("clutter_level")
    if clutter in ALLOWED_CLUTTER:
        background["clutter_level"] = clutter

    # ---- Color overrides ----
    primary = overrides.get("primary_color")
    secondary = overrides.get("secondary_color")
    accent = overrides.get("accent_color")

    if _is_valid_hex(primary):
        palette["primary"] = primary
    if _is_valid_hex(secondary):
        palette["secondary"] = secondary
    if _is_valid_hex(accent):
        palette["accent"] = accent

    # ---- Text override ----
    text_content = overrides.get("text_content")
    if isinstance(text_content, str):
        words = text_content.strip().split()
        if 0 < len(words) <= 6:
            text["content"] = " ".join(words)

    state["thumbnail_spec"] = spec
    return state