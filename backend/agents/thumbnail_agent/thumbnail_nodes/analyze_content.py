import json
import re
from typing import Any, Dict

from util.llm_factory import LLMFactory
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


def _build_prompt(
    idea_title: str,
    idea_description: str,
    audience: str,
    region: str,
    content_format: str,
    script: str,
) -> str:

    script_section = f"\nScript:\n{script}\n" if script else ""

    return f"""
You are an expert YouTube thumbnail strategist specialized in high-CTR, mobile-first thumbnails.

Analyze the content and return a STRICT JSON thumbnail design specification.

Content Title:
{idea_title}

Content Description:
{idea_description}

Audience:
{audience}

Region:
{region}

Content Format:
{content_format}
{script_section}

Return ONLY valid JSON in this exact structure:

{{
  "subject": {{
    "type": "human or object",
    "description": "clear visual description",
    "expression": "natural emotional expression",
    "pose": "short descriptive phrase",
    "shot_type": "close-up | mid-shot | wide"
  }},
  "background": {{
    "style": "clean | blurred | realistic | studio",
    "clutter_level": "low | medium",
    "lighting": "soft studio | cinematic | natural"
  }},
  "emotion_style": "excited | dramatic | professional | friendly | serious",
  "color_palette": {{
    "primary": "#HEX",
    "secondary": "#HEX",
    "accent": "#HEX"
  }},
  "composition": {{
    "subject_position": "center | left | right",
    "depth": "shallow | medium"
  }},
  "text": {{
    "content": "max 6 words",
    "style": "bold | clean | dramatic"
  }}
}}

Rules:
- Optimize for high click-through rate
- Ensure subject is clearly visible at small mobile sizes
- Strong subject emphasis
- Clean realistic background
- No logos, no UI, no platform branding
- No explanations, no markdown
""".strip()


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

    prompt = _build_prompt(
        state.get("idea_title", ""),
        state.get("idea_description", ""),
        state.get("audience", ""),
        state.get("region", ""),
        state.get("content_format", ""),
        script,
    )

    for _ in range(2):
        response = LLMFactory.invoke(
            system_prompt=prompt,
            human_message="Generate thumbnail JSON.",
            temperature=0.4,
        )

        data = _extract_json(response.content.strip())

        if data and _validate_schema(data):
            state["thumbnail_spec"] = data
            return state

        prompt += "\n\nIMPORTANT: Return ONLY valid JSON matching the schema."

    return state

