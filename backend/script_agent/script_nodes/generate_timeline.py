import json
import re
from typing import Any, Dict, Tuple

from script_agent.script_state import ScriptState
from util.llm_factory import LLMFactory
from util.system_prompt import PROMPT_SCRIPT_SYSTEM, PROMPT_SCRIPT_HUMAN


def _seconds_to_timestamp(total_seconds: int) -> str:
    """Convert integer seconds to MM:SS format."""
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m:02d}:{s:02d}"


def _fix_timestamps(timeline: list) -> Tuple[list, int]:
    """Recalculate all timestamps from duration_seconds to ensure accuracy."""
    cursor = 0
    for scene in timeline:
        dur = int(scene.get("duration_seconds", 0))
        scene["timestamp_start"] = _seconds_to_timestamp(cursor)
        scene["timestamp_end"] = _seconds_to_timestamp(cursor + dur)
        cursor += dur
    return timeline, cursor


def _extract_json(raw: str) -> dict:
    """Strip any accidental markdown fences and parse JSON."""
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(clean)


def generate_timeline(state: ScriptState) -> ScriptState:
    """
    LLM reasoning node that generates a 10s video timeline from thumbnail data.
    """
    thumbnail_data = state.get("thumbnail_data", {})
    
    user_prompt = PROMPT_SCRIPT_HUMAN.format(
        thumbnail_json=json.dumps(thumbnail_data, indent=2)
    )

    for _ in range(2):
        response = LLMFactory.invoke(
            system_prompt=PROMPT_SCRIPT_SYSTEM,
            human_message=user_prompt,
            temperature=0.4,
        )

        try:
            data = _extract_json(response.content.strip())
            
            # Fix timestamps to be mathematically accurate
            timeline_list = data.get("timeline", [])
            fixed_timeline, total_seconds = _fix_timestamps(timeline_list)
            
            data["timeline"] = fixed_timeline
            if "video_meta" not in data:
                data["video_meta"] = {}
            data["video_meta"]["duration_seconds"] = total_seconds
            
            state["timeline"] = fixed_timeline
            state["video_meta"] = data["video_meta"]
            state["render_hints"] = data.get("render_hints", {})
            return state
        except (json.JSONDecodeError, ValueError):
            user_prompt += "\n\nIMPORTANT: Return ONLY valid JSON matching the schema."

    return state
