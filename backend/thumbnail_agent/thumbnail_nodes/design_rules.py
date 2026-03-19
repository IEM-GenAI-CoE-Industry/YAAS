from thumbnail_agent.thumbnail_state import ThumbnailState
from util.constants import COLOR_SCHEMES


def _select_color_palette(emotion_style: str, content_format: str) -> dict:
    emotion_style = (emotion_style or "").lower()

    if emotion_style in {"dramatic", "excited"}:
        return COLOR_SCHEMES["high_contrast"]

    if emotion_style in {"professional", "serious"}:
        return COLOR_SCHEMES["educational"]

    if content_format == "short-form":
        return COLOR_SCHEMES["high_contrast"]

    return COLOR_SCHEMES["tech_blue"]


def _refine_text(content: str, content_format: str) -> str:
    if not content:
        return ""

    words = content.strip().split()
    if len(words) > 6:
        content = " ".join(words[:6])

    if content_format == "short-form":
        content = content.upper()

    return content


def apply_design_rules(state: ThumbnailState) -> ThumbnailState:
    spec = state.get("thumbnail_spec")
    if not isinstance(spec, dict):
        return state

    content_format = state.get("content_format", "short-form")

    # ---- Color fallback ----
    palette = spec.get("color_palette")

    if not isinstance(palette, dict) or "primary" not in palette:
        spec["color_palette"] = _select_color_palette(
            spec.get("emotion_style"), content_format
        )

    # ---- Text refinement ----
    text_block = spec.get("text")
    if not isinstance(text_block, dict):
        text_block = {}
    refined = _refine_text(
        text_block.get("content", ""), content_format
    )
    text_block["content"] = refined
    spec["text"] = text_block

    # ---- Composition safety ----
    composition = spec.get("composition", {})
    composition.setdefault("subject_position", "center")
    composition.setdefault("depth", "shallow")
    spec["composition"] = composition

    # ---- Background safety ----
    background = spec.get("background", {})
    background.setdefault("clutter_level", "low")
    spec["background"] = background

    state["thumbnail_spec"] = spec
    return state