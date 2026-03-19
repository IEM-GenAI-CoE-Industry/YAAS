from typing import Any, Dict, List, Optional, TypedDict


class ScriptState(TypedDict, total=False):
    """
    Internal state schema for the Script Agent.
    """
    
    # Input schema
    thumbnail_data: Dict[str, Any]
    
    # Output schema
    timeline: List[Dict[str, Any]]
    video_meta: Dict[str, Any]
    render_hints: Dict[str, Any]
