from script_agent.script_graph import create_script_graph
from script_agent.script_state import ScriptState

_script_graph = create_script_graph()

def validate_thumbnail_input(data: dict) -> None:
    """Validate that the incoming thumbnail JSON has the required fields."""
    required_top = ["subject", "text"]
    missing = [k for k in required_top if k not in data]
    if missing:
        raise ValueError(
            f"Input JSON missing required fields: {', '.join(missing)}. "
            f"Expected keys: subject, background, emotion_style, color_palette, "
            f"composition, text"
        )

def run_script_agent(global_state: dict) -> dict:
    """
    Entry point for the Script Agent.
    Reads 'thumbnail' from global state and writes 'script_timeline'.
    """
    thumbnail_data = global_state.get("thumbnail", {})
    
    if not thumbnail_data:
        raise ValueError("Script Agent requires 'thumbnail' data in global state.")
    
    # Optional Validation step (kept from original code to be safe)
    if "thumbnail_spec" in thumbnail_data:
        validate_thumbnail_input(thumbnail_data["thumbnail_spec"])
        
    agent_state: ScriptState = {
        "thumbnail_data": thumbnail_data
    }
    
    result: ScriptState = _script_graph.invoke(agent_state)
    
    global_state["script_timeline"] = {
        "video_meta": result.get("video_meta", {}),
        "render_hints": result.get("render_hints", {}),
        "timeline": result.get("timeline", [])
    }
    
    return global_state
