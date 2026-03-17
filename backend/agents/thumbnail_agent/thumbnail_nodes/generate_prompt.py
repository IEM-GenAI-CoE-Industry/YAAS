from agents.thumbnail_agent.thumbnail_state import ThumbnailState


def generate_prompt(state: ThumbnailState) -> ThumbnailState:
    spec = state.get("thumbnail_spec")
    if not isinstance(spec, dict):
        return state

    text_mode = state.get("text_render_mode")
    content_format = state.get("content_format", "short-form")

    subject = spec.get("subject", {})
    background = spec.get("background", {})
    composition = spec.get("composition", {})
    palette = spec.get("color_palette", {})
    text_block = spec.get("text")
    if not isinstance(text_block, dict):
        text_block = {}

    prompt_parts: list[str] = []

    
    # Base thumbnail intent
    prompt_parts.append(
        "YouTube thumbnail image, high click-through rate, professional thumbnail composition"
    )


    # Subject
    description = subject.get("description", "")
    expression = subject.get("expression", "")
    pose = subject.get("pose", "")
    shot_type = subject.get("shot_type", "close-up")

    subject_phrase = ", ".join(
        x for x in [description, expression, pose] if x
    )

    if subject_phrase:
        prompt_parts.append(subject_phrase)

    shot_mapping = {
        "close-up": "tight close-up framing",
        "mid-shot": "medium framing showing upper body",
        "wide": "wide framing with environmental context",
    }

    prompt_parts.append(
        shot_mapping.get(shot_type, "tight close-up framing")
    )

    
    # Composition
    position = composition.get("subject_position", "center")
    depth = composition.get("depth", "shallow")

    prompt_parts.append(f"subject positioned {position}")
    prompt_parts.append(f"{depth} depth of field")

    
    # Background
    bg_style = background.get("style", "clean")
    lighting = background.get("lighting", "natural")
    clutter = background.get("clutter_level", "low")

    prompt_parts.append(f"{bg_style} realistic background")
    prompt_parts.append(f"{lighting} lighting")

    if clutter == "low":
        prompt_parts.append(
            "minimal distractions, clean simple environment"
        )
    else:
        prompt_parts.append(
            "light contextual environment detail"
        )

    
    # Emotion / Mood
    emotion = spec.get("emotion_style", "professional")

    emotion_styles = {
        "excited": "energetic positive emotion, engaging expression",
        "dramatic": "cinematic mood with strong visual contrast",
        "professional": "clean polished professional appearance",
        "friendly": "warm approachable emotional tone",
        "serious": "focused minimal emotional expression",
    }

    prompt_parts.append(
        emotion_styles.get(emotion, "professional visual tone")
    )

    
    # Color palette
    if isinstance(palette, dict):
        colors = ", ".join(
            palette.get(k)
            for k in ["primary", "secondary", "accent"]
            if isinstance(palette.get(k), str)
        )
        if colors:
            prompt_parts.append(f"color palette: {colors}")

    
    # Mobile-first rule
    if content_format == "short-form":
        prompt_parts.append(
            "mobile-first composition, instantly readable subject"
        )

    
    # Text handling
    text_content = text_block.get("content", "").strip()

    if text_mode == "baked" and text_content:
        prompt_parts.append(
            f'text overlay: "{text_content}", bold sans-serif typography'
        )
    else:
        prompt_parts.append(
            "no text, no letters, no typography"
        )

    
    # Quality constraints
    prompt_parts.append(
        "16:9 aspect ratio, ultra high resolution, sharp focus, natural skin tones"
    )

    prompt_parts.append(
        "no logos, no watermarks, no UI elements, no platform branding, "
        "no excessive glow, no neon haze"
    )

    state["image_prompt"] = ", ".join(prompt_parts)
    return state