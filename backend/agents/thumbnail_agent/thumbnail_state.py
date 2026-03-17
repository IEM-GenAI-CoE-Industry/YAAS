from typing import Any, Dict, Optional, Literal, TypedDict


class ThumbnailState(TypedDict, total=False):
    """
    Internal state schema for the Thumbnail Agent.
    """

    #Inputs
    idea_title: str
    idea_description: str
    audience: Optional[str]
    region: Optional[str]
    content_format: Optional[Literal["short-form", "long-form"]]
    script: Optional[str]

    #Execution control 
    enable_image_generation: Optional[bool]
    image_provider: Optional[Literal["stability", "gemini"]]
    text_render_mode: Optional[Literal["overlay", "baked", "none"]]

    # User customization
    user_overrides: Optional[Dict[str, Any]]

    # Structured design specification (JSON prompting system)
    thumbnail_spec: Optional[Dict[str, Any]]

    # Generation outputs
    image_prompt: Optional[str]
    image_base64: Optional[str]
