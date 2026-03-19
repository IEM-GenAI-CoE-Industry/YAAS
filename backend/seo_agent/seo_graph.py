from langgraph.graph import StateGraph, END

from seo_agent.seo_state import SeoState
from seo_agent.seo_nodes.generate_metadata import generate_metadata

def create_seo_graph():
    """
    Creates and compiles the LangGraph for the SEO Agent.
    """
    graph = StateGraph(SeoState)

    # Add nodes
    graph.add_node("generate_metadata", generate_metadata)

    # Edges
    graph.set_entry_point("generate_metadata")
    graph.add_edge("generate_metadata", END)

    return graph.compile()
