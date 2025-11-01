from pydantic import BaseModel, Field, field_validator

# Request Classes


class GenerateContentRequest(BaseModel):
    """Request model for generating content."""

    question: str = Field(..., description="question for content generation")
    local_llm: bool = Field(False, description="Whether to use a local LLM (default: False)")

    @field_validator("question")
    def validate_question(cls, value: str) -> str:
        """Ensure question is not empty."""
        if not value.strip():
            raise ValueError("question cannot be empty")
        return value.strip()


# Response Classes


class GenerateContentResponse(BaseModel):
    """Response model for content generation."""

    status: str = Field(..., description="Status of the content generation")
    message: str = Field(..., description="Message about the content generation")
    data: str = Field(..., description="Generated content")

    @field_validator("data")
    def validate_data(cls, value: str) -> str:
        """Ensure data is not empty."""
        if not value.strip():
            raise ValueError("Generated content cannot be empty")
        return value.strip()