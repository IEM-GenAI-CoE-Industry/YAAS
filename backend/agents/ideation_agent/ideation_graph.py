from langgraph.graph import StateGraph, END
from util.llm_factory import LLMFactory
from util.system_prompt import (
    PROMPT_IDEATION_GENERATE,
    PROMPT_IDEATION_REFINE,
)

# Node 1: Generate ideas 
def generate_ideas(state: dict) -> dict:
    response = LLMFactory.invoke(
        system_prompt=PROMPT_IDEATION_GENERATE,
        human_message=f"""
Topic: {state.get('topic', 'AI')}
Audience: {state.get('audience', 'teens')}
Region: {state.get('region', 'India')}
Content Format: {state.get('content_format', 'short-form')}
""",
        temperature=0.7,
    )

    state["ideas"] = response.content.strip()
    return state


# Node 2: Refine ideas 
def refine_ideas(state: dict) -> dict:
    response = LLMFactory.invoke(
        system_prompt=PROMPT_IDEATION_REFINE,
        human_message=state["ideas"],
        temperature=0.6,
    )

    state["ideas"] = response.content.strip()
    return state

# Graph
def create_ideation_graph():
    graph = StateGraph(dict)

    graph.add_node("generate_ideas", generate_ideas)
    graph.add_node("refine_ideas", refine_ideas)

    graph.set_entry_point("generate_ideas")
    graph.add_edge("generate_ideas", "refine_ideas")
    graph.add_edge("refine_ideas", END)

    return graph.compile()
