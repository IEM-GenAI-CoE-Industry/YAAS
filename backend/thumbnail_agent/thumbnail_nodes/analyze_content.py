import json
import re
from typing import Any, Dict

from util.llm_factory import LLMFactory
from util.system_prompt import PROMPT_THUMBNAIL_ANALYZE_SYSTEM, PROMPT_THUMBNAIL_ANALYZE_HUMAN
from thumbnail_agent.thumbnail_state import ThumbnailState

from util.constants import (
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


def _validate_schema(data: Dict[str, Any]) -> bool:
    if not isinstance(data, dict):
        return False

    # Emotion validation
    if data.get("emotion_style") not in ALLOWED_EMOTIONS:
        return False


    # Subject validation
    subject = data.get("subject")
    if not isinstance(subject, dict):
        return False

    if not isinstance(subject.get("type"), str):
        return False

    if not isinstance(subject.get("description"), str):
        return False

    if not isinstance(subject.get("expression"), str):
        return False

    if not isinstance(subject.get("pose"), str):
        return False

    if subject.get("shot_type") not in ALLOWED_SHOT_TYPES:
        return False

    
    # Background validation
    background = data.get("background")
    if not isinstance(background, dict):
        return False

    if background.get("style") not in ALLOWED_BACKGROUND_STYLES:
        return False

    if background.get("lighting") not in ALLOWED_LIGHTING:
        return False

    if background.get("clutter_level") not in ALLOWED_CLUTTER:
        return False

    
    # Composition validation
    composition = data.get("composition")
    if not isinstance(composition, dict):
        return False

    if composition.get("subject_position") not in ALLOWED_SUBJECT_POSITIONS:
        return False

    if composition.get("depth") not in ALLOWED_DEPTH:
        return False

    
    # Text validation
    text = data.get("text")
    if not isinstance(text, dict):
        return False

    content = text.get("content")
    if not isinstance(content, str) or len(content.split()) > 6:
        return False

    
    # Color palette validation
    palette = data.get("color_palette")
    if not isinstance(palette, dict):
        return False

    if not _is_valid_hex(palette.get("primary")):
        return False

    if not _is_valid_hex(palette.get("secondary")):
        return False

    accent = palette.get("accent")
    if accent is not None and not _is_valid_hex(accent):
        return False

    return True


def _extract_json(text: str) -> Dict[str, Any] | None:
    match = re.search(r"\{[\s\S]*\}", text)
    if not match:
        return None

    try:
        return json.loads(match.group())
    except json.JSONDecodeError:
        return None


def analyze_content(state: ThumbnailState) -> ThumbnailState:
    """
    LLM reasoning node that generates a structured thumbnail design specification.

    Output:
    state["thumbnail_spec"]
    """

    script = state.get("script") or ""
    script_section = f"\nScript:\n{script}\n" if script else ""

    prompt = PROMPT_THUMBNAIL_ANALYZE_SYSTEM.format(
        idea_title=state.get("idea_title", ""),
        idea_description=state.get("idea_description", ""),
        audience=state.get("audience", ""),
        region=state.get("region", ""),
        content_format=state.get("content_format", ""),
        script_section=script_section,
    )

    for _ in range(2):
        response = LLMFactory.invoke(
            system_prompt=prompt,
            human_message=PROMPT_THUMBNAIL_ANALYZE_HUMAN,
            temperature=0.4,
        )

        data = _extract_json(response.content.strip())

        if data and _validate_schema(data):
            state["thumbnail_spec"] = data
            return state

        prompt += "\n\nIMPORTANT: Return ONLY valid JSON matching the schema."

    return state

