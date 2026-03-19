from langgraph.graph import StateGraph, END

from script_agent.script_state import ScriptState
from script_agent.script_nodes.generate_timeline import generate_timeline

def create_script_graph():
    """
    Creates and compiles the LangGraph for the Script Agent.
    """
    graph = StateGraph(ScriptState)

    # Add nodes
    graph.add_node("generate_timeline", generate_timeline)

    # Edges
    graph.set_entry_point("generate_timeline")
    graph.add_edge("generate_timeline", END)

    return graph.compile()
