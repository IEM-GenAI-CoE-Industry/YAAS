from langgraph.graph import StateGraph, END

from agents.thumbnail_agent.thumbnail_state import ThumbnailState

from agents.thumbnail_agent.thumbnail_nodes.analyze_content import analyze_content
from agents.thumbnail_agent.thumbnail_nodes.apply_user_overrides import apply_user_overrides
from agents.thumbnail_agent.thumbnail_nodes.design_rules import apply_design_rules
from agents.thumbnail_agent.thumbnail_nodes.generate_prompt import generate_prompt
from agents.thumbnail_agent.thumbnail_nodes.generate_image import generate_image
from agents.thumbnail_agent.thumbnail_nodes.post_render_text import post_render_text


# CONDITIONS
def should_generate_image(state: ThumbnailState):
    return "generate_image" if state.get("enable_image_generation") else END


def should_render_text(state: ThumbnailState):
    mode = state.get("text_render_mode")
    return "post_render_text" if mode == "overlay" else END


# GRAPH
def create_thumbnail_graph():

    graph = StateGraph(ThumbnailState)

    graph.add_node("analyze_content", analyze_content)
    graph.add_node("apply_user_overrides", apply_user_overrides)
    graph.add_node("apply_design_rules", apply_design_rules)
    graph.add_node("generate_prompt", generate_prompt)
    graph.add_node("generate_image", generate_image)
    graph.add_node("post_render_text", post_render_text)

    graph.set_entry_point("analyze_content")

    graph.add_edge("analyze_content", "apply_user_overrides")
    graph.add_edge("apply_user_overrides", "apply_design_rules")
    graph.add_edge("apply_design_rules", "generate_prompt")

    graph.add_conditional_edges(
        "generate_prompt",
        should_generate_image,
        {
            "generate_image": "generate_image",
            END: END,
        },
    )

    graph.add_conditional_edges(
        "generate_image",
        should_render_text,
        {
            "post_render_text": "post_render_text",
            END: END,
        },
    )

    graph.add_edge("post_render_text", END)

    return graph.compile()