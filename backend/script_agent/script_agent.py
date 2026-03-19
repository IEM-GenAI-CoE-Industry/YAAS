"""
script_agent.py
───────────────
YouTube Pipeline · Script Agent (10-second Reels)

Input  : thumbnail_agent output JSON  (file path or stdin)
Output : video_timeline JSON          (file path or stdout)

Usage:
    python script_agent.py --input thumbnail.json --output timeline.json
    python script_agent.py --input thumbnail.json          # prints to stdout
    cat thumbnail.json | python script_agent.py            # stdin → stdout
"""

import argparse
import json
import os
import re
import sys
from dotenv import load_dotenv  # type: ignore
from mistralai.client import Mistral  # type: ignore

load_dotenv()

# ─── Config ──────────────────────────────────────────────────────────────────

API_KEY = os.getenv("MISTRAL_API_KEY")
MODEL = os.getenv("SCRIPT_AGENT_MODEL", "mistral-large-latest")

# ─── System prompt ────────────────────────────────────────────────────────────

SYSTEM_PROMPT = """
You are a professional YouTube Reels script agent inside a multi-agent video production pipeline.

Your job: receive a thumbnail JSON description and output a complete, production-ready
10-SECOND video script as a timeline JSON for the downstream video generation agent.

THE VIDEO IS EXACTLY 10 SECONDS LONG. No more. No less.

OUTPUT RULES (critical):
- Respond with ONLY a valid JSON object — no markdown, no code fences, no commentary.
- Any non-JSON characters in your response will crash the pipeline.

OUTPUT SCHEMA:
{
  "video_meta": {
    "title": "string (max 60 chars)",
    "duration_seconds": 10,
    "tone": "string",
    "target_audience": "string",
    "hook_type": "question | shock | statement | story",
    "music_track_suggestion": "string",
    "b_roll_suggestions": ["string"]
  },
  "render_hints": {
    "aspect_ratio": "9:16",
    "resolution": "1080x1920",
    "fps": 30,
    "color_palette_primary": "#HEX from input",
    "color_palette_secondary": "#HEX from input",
    "color_palette_accent": "#HEX from input",
    "font_style": "bold | clean | dramatic (from input text.style)"
  },
  "timeline": [
    {
      "id": "scene_01",
      "timestamp_start": "00:00",
      "timestamp_end": "00:03",
      "duration_seconds": 3,
      "scene_type": "hook | main_point | cta",
      "shot": {
        "type": "close-up | mid-shot | wide | b-roll | text-overlay",
        "camera_movement": "static | slow_zoom | pan_left | pan_right | dolly_in",
        "framing_notes": "string"
      },
      "voiceover": {
        "text": "Spoken narration for this scene.",
        "tone": "energetic | calm | dramatic | conversational",
        "pace": "fast | medium | slow",
        "pause_after_seconds": 0
      },
      "visual_direction": {
        "on_screen_subject": "string (from input subject)",
        "background": "string (from input background)",
        "lighting": "string (from input background.lighting)",
        "color_grade": "string",
        "overlay_text": "string or null",
        "overlay_style": "bold | clean | dramatic | null"
      },
      "audio": {
        "music_mood": "upbeat | tense | emotional | inspirational | none",
        "music_volume": "bg | mid | off",
        "sfx": "string or null"
      },
      "transition_to_next": "cut | fade | zoom_in | zoom_out | whip_pan"
    }
  ]
}

SCRIPT RULES:
1. Generate exactly 3 scenes totalling EXACTLY 10 seconds:
   - Scene 1: HOOK (0–3s) — match the thumbnail emotion, expression, and text exactly.
   - Scene 2: MAIN POINT (3–7s) — deliver the core content, use the subject description.
   - Scene 3: CTA/ENDING (7–10s) — call to action with energy.
2. Derive tone, color_grade, overlay_style directly from the input thumbnail JSON.
3. Use the input color_palette HEX values in render_hints.
4. Match shot type from input subject.shot_type.
5. Match lighting from input background.lighting.
6. Use the input text.content as the overlay_text in scene 1.
7. Use the input text.style as the overlay_style.
8. Voiceover text must sound natural when read aloud — punchy, viral, short phrases.
9. Timestamps must be continuous: scene N+1 starts exactly where scene N ends.
10. video_meta.duration_seconds must always be 10.
11. aspect_ratio must be 9:16 (vertical for Reels).
12. Respond ONLY with the JSON object — nothing else.
""".strip()

# ─── Helpers ──────────────────────────────────────────────────────────────────


def seconds_to_timestamp(total_seconds: int) -> str:
    """Convert integer seconds to MM:SS format."""
    m = total_seconds // 60
    s = total_seconds % 60
    return f"{m:02d}:{s:02d}"


def fix_timestamps(timeline: list) -> tuple[list, int]:
    """Recalculate all timestamps from duration_seconds to ensure accuracy."""
    cursor = 0
    for scene in timeline:
        dur = int(scene.get("duration_seconds", 0))
        scene["timestamp_start"] = seconds_to_timestamp(cursor)
        scene["timestamp_end"] = seconds_to_timestamp(cursor + dur)
        cursor += dur
    return timeline, cursor


def extract_json(raw: str) -> dict:
    """Strip any accidental markdown fences and parse JSON."""
    clean = re.sub(r"```(?:json)?|```", "", raw).strip()
    return json.loads(clean)


def validate_thumbnail_input(data: dict) -> None:
    """Validate that the incoming thumbnail JSON has the required fields."""
    required_top = ["subject", "text"]
    missing = [k for k in required_top if k not in data]
    if missing:
        raise ValueError(
            f"Input JSON missing required fields: {', '.join(missing)}. "
            f"Expected keys: subject, background, emotion_style, color_palette, "
            f"composition, text"
        )


def build_user_prompt(thumbnail_data: dict) -> str:
    """Build the user message from thumbnail data."""
    return (
        "Generate a 10-second YouTube Reels script timeline from this "
        "thumbnail agent output:\n\n"
        + json.dumps(thumbnail_data, indent=2)
    )


# ─── Core agent function ──────────────────────────────────────────────────────


def run_script_agent(thumbnail_data: dict) -> dict:
    """
    Takes thumbnail agent JSON dict.
    Returns video timeline JSON dict for the video generation agent.
    Raises on API or parse errors.
    """
    if not API_KEY:
        raise RuntimeError(
            "MISTRAL_API_KEY not found. Set it in your .env file."
        )

    client = Mistral(api_key=API_KEY)

    response = client.chat.complete(
        model=MODEL,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": build_user_prompt(thumbnail_data)},
        ],
    )

    raw = response.choices[0].message.content

    result = extract_json(raw)

    # Fix timestamps to be mathematically accurate
    fixed_timeline, total_seconds = fix_timestamps(result.get("timeline", []))
    result["timeline"] = fixed_timeline
    result["video_meta"]["duration_seconds"] = total_seconds

    return result


# ─── CLI entry point ──────────────────────────────────────────────────────────


def main():
    parser = argparse.ArgumentParser(
        description="Script Agent: thumbnail JSON → 10s Reel timeline JSON"
    )
    parser.add_argument(
        "--input", "-i",
        help="Path to thumbnail agent JSON file (omit to read from stdin)",
    )
    parser.add_argument(
        "--output", "-o",
        help="Path to write timeline JSON (omit to print to stdout)",
    )
    parser.add_argument(
        "--pretty", action="store_true", default=True,
        help="Pretty-print output JSON (default: true)",
    )
    args = parser.parse_args()

    # ── Read input ──
    if args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            thumbnail_data = json.load(f)
    else:
        thumbnail_data = json.load(sys.stdin)

    # ── Validate ──
    validate_thumbnail_input(thumbnail_data)

    # ── Run agent ──
    print("🎬 Running script agent (10s Reel)...", file=sys.stderr)
    timeline = run_script_agent(thumbnail_data)
    scene_count = len(timeline.get("timeline", []))
    total_dur = timeline.get("video_meta", {}).get("duration_seconds", "?")
    print(
        f"✅ Done. {scene_count} scenes, {total_dur}s total.",
        file=sys.stderr,
    )

    # ── Write output ──
    indent = 2 if args.pretty else None
    output_str = json.dumps(timeline, indent=indent, ensure_ascii=False)

    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_str)
        print(f"📁 Timeline saved → {args.output}", file=sys.stderr)
    else:
        print(output_str)


if __name__ == "__main__":
    main()