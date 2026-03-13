"""
Temporary test file for Ideation Agent.
Used only to validate ideation + refinement logic.
Safe to remove after review.
"""

from agents.ideation_agent.ideation_graph import create_ideation_graph

if __name__ == "__main__":
    print("\nIdeation Agent – Local Test\n")

    topic = input("Enter topic/niche: ").strip()
    audience = input("Enter target audience: ").strip()
    region = input("Enter target region: ").strip()
    content_format = input("Content format (short-form / long-form): ").strip()

    graph = create_ideation_graph()

    state = {
        "topic": topic or "AI",
        "audience": audience or "Gen Z",
        "region": region or "India",
        "content_format": content_format or "short-form"
    }

    result = graph.invoke(state)

    print("\nFinal Refined YouTube Video Ideas:\n")
    print(result["ideas"])
