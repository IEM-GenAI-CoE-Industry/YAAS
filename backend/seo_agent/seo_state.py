from typing import Any, Dict, List, TypedDict

class SeoState(TypedDict, total=False):
    """
    Internal state schema for the SEO Agent.
    """
    
    # Input
    script_timeline: Dict[str, Any]
    
    # Output
    seo_metadata: Dict[str, Any]
