import base64
import logging
from io import BytesIO

from PIL import Image, ImageDraw, ImageFont

from agents.thumbnail_agent.thumbnail_state import ThumbnailState

logger = logging.getLogger(__name__)


def _wrap_text(text: str, max_chars: int = 14):
    words = text.split()
    lines = []
    current = ""

    for w in words:
        if len(current) + len(w) <= max_chars:
            current = f"{current} {w}".strip()
        else:
            lines.append(current)
            current = w

    if current:
        lines.append(current)

    return lines[:3]


def post_render_text(state: ThumbnailState) -> ThumbnailState:

    if state.get("text_render_mode") != "overlay":
        return state

    image_b64 = state.get("image_base64")

    spec = state.get("thumbnail_spec", {})
    text = (spec.get("text", {}).get("content") or "").strip()

    if not image_b64 or not text:
        return state

    logger.info("Overlaying thumbnail text: %s", text)

    try:
        image_bytes = base64.b64decode(image_b64)

        image = Image.open(BytesIO(image_bytes)).convert("RGB")
        draw = ImageDraw.Draw(image)

        W, H = image.size

        font_size = max(52, W // 12)

        font = None
        for f in ["arialbd.ttf", "DejaVuSans-Bold.ttf"]:
            try:
                font = ImageFont.truetype(f, font_size)
                break
            except Exception:
                continue

        if font is None:
            font = ImageFont.load_default()

        lines = _wrap_text(text)

        line_height = font_size + 8
        block_height = line_height * len(lines)

        x = int(W * 0.05)
        y = int(H * 0.06)

        if y + block_height > H * 0.4:
            y = int(H * 0.65)

        for i, line in enumerate(lines):
            draw.text(
                (x, y + i * line_height),
                line.upper(),
                font=font,
                fill=(255, 255, 255),
                stroke_width=6,
                stroke_fill=(0, 0, 0),
            )

        buffer = BytesIO()
        image.save(buffer, format="PNG")

        state["image_base64"] = base64.b64encode(buffer.getvalue()).decode()

        logger.info("Text overlay applied successfully")

    except Exception:
        logger.exception("Thumbnail text overlay failed")

    return state