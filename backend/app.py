import sys
import warnings

# Suppress pydantic v1 compatibility warning from LangChain on Python 3.14+
warnings.filterwarnings(
    "ignore",
    message="Core Pydantic V1 functionality",
    category=UserWarning,
)

from pathlib import Path

file = Path(__file__).resolve()
parent, root = file.parent, file.parents[1]
sys.path.append(str(root))

from typing import Any

from fastapi import APIRouter, FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from api_services import api_router

import os
from fastapi.staticfiles import StaticFiles

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


output_dir = os.path.join(parent, "output")
os.makedirs(output_dir, exist_ok=True)
app.mount("/outputs", StaticFiles(directory=output_dir), name="outputs")

app.include_router(api_router, prefix=settings.API_V1_STR)
app.include_router(root_router)


if __name__ == "__main__":
    import subprocess
    import uvicorn

    # Free port 8002 if already in use (Windows)
    try:
        result = subprocess.run(
            ["netstat", "-ano"],
            capture_output=True, text=True
        )
        for line in result.stdout.splitlines():
            if ":8002 " in line and "LISTENING" in line:
                pid = line.strip().split()[-1]
                subprocess.run(["taskkill", "/F", "/PID", pid], capture_output=True)
                print(f"Killed existing process on port 8002 (PID {pid})")
                break
    except Exception:
        pass

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        timeout_keep_alive=300,  # Keep-alive timeout in seconds (default is 5)
        timeout_graceful_shutdown=300,  # Graceful shutdown timeout
        log_level="info",
    )
