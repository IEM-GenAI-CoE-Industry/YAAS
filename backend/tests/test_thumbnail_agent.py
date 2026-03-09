import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import base64
from agents.thumbnail_agent.thumbnail_service import run_thumbnail_agent


def main():
    print("\n=== YAAS Thumbnail Agent – CLI Test ===\n")

    print("Paste ideation output (numbered ideas).")
    print("End input with an empty line:\n")

    ideas_lines = []
    while True:
        line = input()
        if not line.strip():
            break
        ideas_lines.append(line)

    ideas_text = "\n".join(ideas_lines)

    if not ideas_text.strip():
        print("\nNo ideas provided. Exiting.")
        return

    selected_idea_number = input(
        "\nSelect idea number (default = 1): "
    ).strip()

    try:
        selected_idea_number = int(selected_idea_number) if selected_idea_number else 1
    except ValueError:
        selected_idea_number = 1

    audience = input("Audience (optional): ").strip() or None
    region = input("Region (optional): ").strip() or None

    content_format = (
        input("Content format (short-form / long-form) [short-form]: ").strip()
        or "short-form"
    )

    enable_image_generation = (
        input("Enable image generation? (y/n) [n]: ").strip().lower() == "y"
    )

    image_provider = None
    if enable_image_generation:
        image_provider = (
            input("Image provider (stability / gemini) [stability]: ").strip()
            or "stability"
        )

    print("\nText rendering mode:")
    print("1 → Overlay text after generation (recommended)")
    print("2 → Bake text into image (experimental)")
    print("3 → No text in thumbnail")

    text_mode_input = input("Select option [1]: ").strip() or "1"

    text_render_mode_map = {
        "1": "overlay",
        "2": "baked",
        "3": "none",
    }

    text_render_mode = text_render_mode_map.get(text_mode_input, "overlay")

    print("\n=== Running Thumbnail Agent ===\n")

    global_state = {
        "ideas": ideas_text,
        "selected_idea_number": selected_idea_number,
        "audience": audience,
        "region": region,
        "content_format": content_format,
        "enable_image_generation": enable_image_generation,
        "image_provider": image_provider,
        "text_render_mode": text_render_mode,
    }

    result = run_thumbnail_agent(global_state)

    thumbnail = result.get("thumbnail", {})
    spec = thumbnail.get("thumbnail_spec", {})

    subject = spec.get("subject", {})
    background = spec.get("background", {})
    palette = spec.get("color_palette", {})
    composition = spec.get("composition", {})
    text_block = spec.get("text", {})

    print("\n=== Thumbnail Agent Output ===\n")

    print(f"Idea Title        : {thumbnail.get('idea_title')}")
    print(f"Idea Description  : {thumbnail.get('idea_description')}")
    print(f"Audience          : {thumbnail.get('audience')}")
    print(f"Region            : {thumbnail.get('region')}")
    print(f"Content Format    : {thumbnail.get('content_format')}")

    print("\n--- Subject ---")
    print(f"Type              : {subject.get('type')}")
    print(f"Description       : {subject.get('description')}")
    print(f"Expression        : {subject.get('expression')}")
    print(f"Pose              : {subject.get('pose')}")
    print(f"Shot Type         : {subject.get('shot_type')}")

    print("\n--- Background ---")
    print(f"Style             : {background.get('style')}")
    print(f"Lighting          : {background.get('lighting')}")
    print(f"Clutter Level     : {background.get('clutter_level')}")

    print("\n--- Composition ---")
    print(f"Subject Position  : {composition.get('subject_position')}")
    print(f"Depth             : {composition.get('depth')}")

    print("\n--- Color Palette ---")
    print(f"Primary           : {palette.get('primary')}")
    print(f"Secondary         : {palette.get('secondary')}")
    print(f"Accent            : {palette.get('accent')}")

    print("\n--- Text ---")
    print(f"Content           : {text_block.get('content')}")
    print(f"Style             : {text_block.get('style')}")

    print("\n--- Generation ---")
    print(f"Image Provider    : {thumbnail.get('image_provider')}")
    print(f"Text Render Mode  : {text_render_mode}")

    image_b64 = thumbnail.get("image_base64")

    if image_b64:
        print("\nImage generated successfully.")

        save_image = (
            input("Save image to file? (y/n) [n]: ").strip().lower() == "y"
        )

        if save_image:
            with open("thumbnail.png", "wb") as f:
                f.write(base64.b64decode(image_b64))

            print("Image saved as thumbnail.png")

    else:
        print("\nImage not generated (prompt-only mode).")

    print("\n=== Test Complete ===\n")


if __name__ == "__main__":
    main()

# 1. AI Homework Hacks You Can't Ignore 
# Description: Learn how students can use AI tools ethically to simplify studying and improve grades. 
# 2. Create Viral AI Art for Instagram 
# Description: Discover free AI tools to design stunning profile pictures and eye-catching posts. 
# 3. Boost Productivity with AI Writing Assistants 
# Description: Explore top AI writing tools that help students draft essays and reports faster.