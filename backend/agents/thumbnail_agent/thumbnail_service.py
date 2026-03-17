import re
from typing import List, Tuple

from agents.thumbnail_agent.thumbnail_graph import create_thumbnail_graph
from agents.thumbnail_agent.thumbnail_state import ThumbnailState


_thumbnail_graph = create_thumbnail_graph()


def _parse_ideas(ideas_text: str) -> List[Tuple[str, str]]:
    blocks = re.split(r"\n\s*\d+\.\s+", ideas_text.strip())
    parsed = []

    for block in blocks:
        if not block.strip():
            continue

        lines = block.strip().split("\n")
        title = lines[0].strip()

        description = ""
        for line in lines[1:]:
            if "description:" in line.lower():
                description = line.split(":", 1)[1].strip()
            else:
                description += " " + line.strip()

        parsed.append((title, description.strip()))

    return parsed


def run_thumbnail_agent(global_state: dict) -> dict:
    ideas_text = global_state.get("ideas")
    selected_idea_number = global_state.get("selected_idea_number")

    if not ideas_text or not isinstance(ideas_text, str):
        raise ValueError("Thumbnail Agent requires 'ideas' as a non-empty string.")

    parsed_ideas = _parse_ideas(ideas_text)

    if not parsed_ideas:
        raise ValueError("Failed to parse ideas from ideation output.")

    if isinstance(selected_idea_number, int):
        idx = selected_idea_number - 1
        if 0 <= idx < len(parsed_ideas):
            idea_title, idea_description = parsed_ideas[idx]
        else:
            idea_title, idea_description = parsed_ideas[0]
    else:
        idea_title, idea_description = parsed_ideas[0]

    text_mode = global_state.get("text_render_mode")
    if not isinstance(text_mode, str):
        text_mode = "overlay"

    agent_state: ThumbnailState = {
        "idea_title": idea_title,
        "idea_description": idea_description,
        "audience": global_state.get("audience"),
        "region": global_state.get("region"),
        "content_format": global_state.get("content_format"),
        "script": global_state.get("script"),
        "enable_image_generation": global_state.get("enable_image_generation", False),
        "image_provider": global_state.get("image_provider"),
        "text_render_mode": text_mode.lower(),
        "user_overrides": global_state.get("user_overrides"),
    }

    result: ThumbnailState = _thumbnail_graph.invoke(agent_state)

    global_state["final_idea"] = {
        "title": idea_title,
        "description": idea_description,
    }

    thumbnail_spec = result.get("thumbnail_spec") or {}
    
    global_state["thumbnail"] = {
        "idea_title": idea_title,
        "idea_description": idea_description,
        "audience": agent_state.get("audience"),
        "region": agent_state.get("region"),
        "content_format": agent_state.get("content_format"),
        "thumbnail_spec": thumbnail_spec,
        "thumbnail_text": thumbnail_spec.get("text", {}).get("content"),
        "image_prompt": result.get("image_prompt"),
        "image_provider": result.get("image_provider"),
        "image_base64": result.get("image_base64"),
        "text_render_mode": result.get("text_render_mode"),
    }

    return global_state