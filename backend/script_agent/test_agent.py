"""
test_agent.py
─────────────
Quick integration test for the Script Agent.

Sends a realistic thumbnail agent JSON and prints the generated timeline.
"""

import json
from script_agent import run_script_agent, validate_thumbnail_input  # type: ignore

# ─── Mock thumbnail agent output ─────────────────────────────────────────────
# This matches the real schema your thumbnail agent produces.

thumbnail_mock = {
    "subject": {
        "type": "human",
        "description": "Young man in a hoodie reacting to a shocking moment",
        "expression": "jaw-dropped, wide eyes",
        "pose": "leaning forward with hands on head",
        "shot_type": "close-up"
    },
    "background": {
        "style": "blurred",
        "clutter_level": "low",
        "lighting": "cinematic"
    },
    "emotion_style": "dramatic",
    "color_palette": {
        "primary": "#FF6B35",
        "secondary": "#1A1A2E",
        "accent": "#FFD700"
    },
    "composition": {
        "subject_position": "center",
        "depth": "shallow"
    },
    "text": {
        "content": "You Won't Believe This!",
        "style": "bold"
    }
}


def test_script_generation():
    print("\n" + "=" * 60)
    print("  SCRIPT AGENT TEST — 10-Second Reel")
    print("=" * 60)

    # ── Show input ──
    print("\n📥 Input from Thumbnail Agent:\n")
    print(json.dumps(thumbnail_mock, indent=2))

    # ── Validate input ──
    try:
        validate_thumbnail_input(thumbnail_mock)
        print("\n✅ Input validation passed.")
    except ValueError as e:
        print(f"\n❌ Validation error: {e}")
        return

    # ── Run agent ──
    print("\n🎬 Calling Mistral API...\n")
    try:
        result = run_script_agent(thumbnail_mock)
    except Exception as e:
        print(f"❌ Agent error: {e}")
        return

    # ── Show output ──
    print("📤 Generated Timeline for Video Agent:\n")
    print(json.dumps(result, indent=2))

    # ── Quick checks ──
    print("\n" + "-" * 40)
    print("Quick Validation:")
    scenes = result.get("timeline", [])
    total = sum(s.get("duration_seconds", 0) for s in scenes)
    print(f"  Scenes     : {len(scenes)}")
    print(f"  Total time : {total}s")
    print(f"  Aspect     : {result.get('render_hints', {}).get('aspect_ratio', '?')}")
    print(f"  Title      : {result.get('video_meta', {}).get('title', '?')}")

    if total == 10:
        print("\n✅ PASS — Timeline is exactly 10 seconds!")
    else:
        print(f"\n⚠️  WARNING — Timeline is {total}s, expected 10s")

    print("=" * 60 + "\n")


if __name__ == "__main__":
    test_script_generation()