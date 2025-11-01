from util.llm_factory import LLMFactory
from util.system_prompt import prompt_generate_summary


from typing import Optional

def generate_summary(text: str, local_llm = False) -> Optional[str]:
    """
    Generates a summary of the given text using the LLM.

    Args:
        text: The input text to summarize

    Returns:
        The generated summary or None if generation fails
    """
    if not text or not text.strip():
        return None

    try:
        response = LLMFactory.invoke(
            system_prompt=prompt_generate_summary,
            human_message=text,
            temperature=0.7,
            local_llm=local_llm,
        )
        summary = response.content.strip()
        return summary
    except Exception as e:
        # Log the error appropriately
        print(f"Error generating summary: {e}")
        return None