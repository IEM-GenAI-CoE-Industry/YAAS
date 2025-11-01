from fastapi import APIRouter, HTTPException, status
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

api_router = APIRouter(tags=["YAAS API Services"])

from base_requests import GenerateContentRequest, GenerateContentResponse
from test_run import generate_summary


@api_router.post(
    "/generate",
    response_model=GenerateContentResponse,
    status_code=status.HTTP_200_OK,
    responses={
        400: {"description": "Invalid Question"},
        422: {"description": "Unprocessable Question"},
    },
)
async def generate_content(request: GenerateContentRequest) -> GenerateContentResponse:
    try:
        logger.info("Generating content with Question")
        summary = generate_summary(text=request.question, local_llm=request.local_llm)

        return GenerateContentResponse(
            status="success", message="Content generated successfully", data=summary
        )
    except HTTPException as he:
        raise he
    except Exception as e:
        logger.error(f"Error generating content: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error generating content: {str(e)}",
        )