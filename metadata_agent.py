import os
import json
import datetime
import google.generativeai as genai

# -------------------- GEMINI SETUP --------------------

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

if not GEMINI_API_KEY:
    raise RuntimeError(
        "❌ GEMINI_API_KEY not found. Set it as an environment variable."
    )

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-1.5-flash")

# -------------------- METADATA AGENT --------------------

def get_video_metadata(context: str) -> dict:
    """
    Generate SEO-optimized YouTube metadata using Gemini.
    Context can be:
    - video summary
    - script
    - filename
    - description
    """

    prompt = f"""
    You are a YouTube SEO expert.

    Video context:
    {context}

    Generate STRICT JSON in this format:
    {{
        "title": "string",
        "description": "string",
        "tags": ["tag1", "tag2", "tag3", "tag4", "tag5"]
    }}
    """

    response = model.generate_content(prompt)
    text = response.text.strip()

    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(
            f"❌ Gemini returned invalid JSON.\nRaw output:\n{text}"
        )

    scheduled_time = (
        datetime.datetime.utcnow()
        + datetime.timedelta(minutes=2)
    ).isoformat(timespec="seconds") + "Z"

    return {
        "title": data["title"],
        "description": data["description"],
        "tags": data["tags"],
        "privacy": "private",
        "scheduled_time": scheduled_time,
    }
