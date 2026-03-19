import datetime
from seo_agent.seo_graph import create_seo_graph
from seo_agent.seo_state import SeoState

_seo_graph = create_seo_graph()

def run_seo_agent(global_state: dict) -> dict:
    """
    Entry point for the SEO Agent.
    Reads 'script_timeline' from global state and writes 'seo_metadata'.
    """
    
    script_timeline = global_state.get("script_timeline", {})
    
    if not script_timeline:
        raise ValueError("SEO Agent requires 'script_timeline' data in global state.")
        
    agent_state: SeoState = {
        "script_timeline": script_timeline
    }
    
    result: SeoState = _seo_graph.invoke(agent_state)
    
    metadata = result.get("seo_metadata", {})
    
    if metadata:
        # Generate scheduled time
        scheduled_time = (
            datetime.datetime.utcnow()
            + datetime.timedelta(minutes=2)
        ).isoformat(timespec="seconds") + "Z"
        
        metadata["privacy"] = "private"
        metadata["scheduled_time"] = scheduled_time
        
        global_state["seo_metadata"] = metadata
    
    return global_state
