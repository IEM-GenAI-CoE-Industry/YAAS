import json
import re

from seo_agent.seo_state import SeoState
from util.llm_factory import LLMFactory
from util.system_prompt import PROMPT_SEO_SYSTEM, PROMPT_SEO_HUMAN


def _extract_json(raw: str) -> dict:
    match = re.search(r"\{[\s\S]*\}", raw)
    if not match:
        raise ValueError("No JSON object found in response")
    clean = match.group(0).strip()
    return json.loads(clean)


def generate_metadata(state: SeoState) -> SeoState:
    """
    LLM reasoning node that generates SEO optimized YouTube metadata.
    """
    
    script_timeline = state.get("script_timeline", {})
    context_data = json.dumps(script_timeline, indent=2)
    
    prompt = PROMPT_SEO_SYSTEM.format(context=context_data)
    
    for _ in range(2):
        response = LLMFactory.invoke(
            system_prompt=prompt,
            human_message=PROMPT_SEO_HUMAN,
            temperature=0.7,
        )
        
        try:
            data = _extract_json(response.content.strip())
            
            # Simple validation
            if "title" in data and "description" in data:
                state["seo_metadata"] = data
                return state
        except (json.JSONDecodeError, ValueError):
            pass
            
        prompt += "\n\nIMPORTANT: Return ONLY valid JSON matching the schema."
        
    return state
