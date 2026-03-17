import os
import base64
import logging
import requests
from typing import Optional

from google import genai

from agents.thumbnail_agent.thumbnail_state import ThumbnailState
from util.image_config import (
    STABILITY_API_URL,
    STABILITY_MODEL,
    GEMINI_MODEL,
    STABILITY_API_KEY_ENV,
    GEMINI_API_KEY_ENV,
)

logger = logging.getLogger(__name__)


def _generate_with_gemini(prompt: str) -> Optional[str]:
    api_key = os.getenv(GEMINI_API_KEY_ENV)

    if not api_key:
        logger.warning("Gemini API key not found")
        return None

    try:
        client = genai.Client(api_key=api_key)

        response = client.models.generate_content(
            model=GEMINI_MODEL,
            contents=[prompt],
            config={"response_modalities": ["IMAGE"]},
        )

        if not response.candidates:
            logger.warning("Gemini response contains no candidates")
            return None

        candidate = response.candidates[0]
        parts = getattr(candidate.content, "parts", [])

        for part in parts:
            if hasattr(part, "inline_data") and part.inline_data:
                return base64.b64encode(part.inline_data.data).decode()

        logger.warning("Gemini response contained no image data")
        return None

    except Exception:
        logger.exception("Gemini image generation failed")
        return None


def _generate_with_stability(prompt: str) -> Optional[str]:
    api_key = os.getenv(STABILITY_API_KEY_ENV)

    if not api_key:
        logger.warning("Stability API key not found")
        return None

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "image/*",
    }

    files = {
        "prompt": (None, prompt),
        "model": (None, STABILITY_MODEL),
        "output_format": (None, "png"),
    }

    try:
        response = requests.post(
            STABILITY_API_URL,
            headers=headers,
            files=files,
            timeout=60,
        )

        if response.status_code != 200:
            logger.error("Stability API error: %s", response.text)
            return None

        if not response.content:
            logger.warning("Stability returned empty image response")
            return None

        return base64.b64encode(response.content).decode()

    except Exception:
        logger.exception("Stability image generation failed")
        return None


def generate_image(state: ThumbnailState) -> ThumbnailState:
    if not state.get("enable_image_generation", False):
        logger.info("Image generation disabled — skipping")
        return state

    prompt = state.get("image_prompt")
    if not prompt:
        logger.warning("No image prompt found — skipping image generation")
        return state

    provider = state.get("image_provider") or "stability"
    image_base64: Optional[str] = None

    if provider == "gemini":
        logger.info("Attempting Gemini image generation")

        image_base64 = _generate_with_gemini(prompt)

        if image_base64:
            logger.info("Gemini image generation successful")
            state["image_base64"] = image_base64
            state["image_provider"] = "gemini"
            return state

        logger.warning("Gemini generation failed — falling back to Stability")

    logger.info("Attempting Stability image generation")

    image_base64 = _generate_with_stability(prompt)

    if image_base64:
        logger.info("Stability image generation successful")
        state["image_base64"] = image_base64
        state["image_provider"] = "stability"
    else:
        logger.warning("Stability generation failed — returning prompt-only mode")

    return state