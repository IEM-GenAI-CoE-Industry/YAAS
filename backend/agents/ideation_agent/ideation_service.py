from agents.ideation.ideation_graph import create_ideation_graph

_ideation_graph = create_ideation_graph()

def run_ideation_agent(global_state: dict) -> dict:
    """
    Entry point for the Ideation Agent.
    To be called later by the main YAAS graph.
    """

    agent_state = {
        "topic": global_state.get("topic"),
        "audience": global_state.get("audience"),
        "region": global_state.get("region"),
        "content_format": global_state.get("content_format", "short-form"),
    }

    result = _ideation_graph.invoke(agent_state)

    global_state["ideas"] = result["ideas"]
    return global_state
