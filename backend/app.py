import sys
from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api_services import api_router

from config import settings

app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_tags=[
        {"name": "YAAS Platform Services", "description": "YAAS Platform APIs"}
    ],
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
)

# Set all CORS enabled origins - MUST be before adding routers
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

root_router = APIRouter()


@root_router.get("/")
def index(request: Request) -> Any:
    """Basic HTML response."""
    body = (
        "<html>"
        "<body style='padding: 10px;'>"
        "<h1>YAAS Platform APIs</h1>"
        "<div>"
        "Check the API spec: <a href='/docs'>here</a>"
        "</div>"
        "</body>"
        "</html>"
    )

    return HTMLResponse(content=body)


app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8001,
        timeout_keep_alive=300,  # Keep-alive timeout in seconds (default is 5)
        timeout_graceful_shutdown=300,  # Graceful shutdown timeout
        log_level="info",
    )
