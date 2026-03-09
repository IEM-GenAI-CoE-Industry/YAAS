import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

import gradio as gr
import base64
from io import BytesIO
from PIL import Image

from agents.ideation_agent.ideation_service import run_ideation_agent
from agents.thumbnail_agent.thumbnail_service import run_thumbnail_agent


# =================================================
# IDEATION AGENT
# =================================================

def run_ideation(topic, audience, region, content_format):

    if not topic or not topic.strip():
        return "", "❌ Topic is required."

    global_state = {
        "topic": topic.strip(),
        "audience": audience,
        "region": region,
        "content_format": content_format,
    }

    result = run_ideation_agent(global_state)

    ideas = result.get("ideas", "")

    if not ideas:
        return "", "❌ Ideation failed."

    return ideas, "✅ Ideas generated successfully."


# =================================================
# PREFILL THUMBNAIL SPEC (ANALYZE CONTENT)
# =================================================

def prefill_thumbnail_spec(
    ideas_text,
    selected_idea_number,
    audience,
    region,
    content_format,
):

    if not ideas_text or not ideas_text.strip():
        return [""] * 11

    try:
        selected_idea_number = int(selected_idea_number)
    except:
        selected_idea_number = 1

    global_state = {
        "ideas": ideas_text,
        "selected_idea_number": selected_idea_number,
        "audience": audience,
        "region": region,
        "content_format": content_format,
        "enable_image_generation": False,  
    }

    result = run_thumbnail_agent(global_state)

    thumbnail = result.get("thumbnail", {})
    spec = thumbnail.get("thumbnail_spec", {})

    subject = spec.get("subject", {})
    background = spec.get("background", {})
    composition = spec.get("composition", {})
    palette = spec.get("color_palette", {})
    text_block = spec.get("text", {})

    return (
        subject.get("expression", ""),
        subject.get("shot_type", ""),
        background.get("style", ""),
        background.get("lighting", ""),
        composition.get("subject_position", ""),
        composition.get("depth", ""),
        background.get("clutter_level", ""),
        text_block.get("content", ""),
        palette.get("primary", "#ffffff"),
        palette.get("secondary", "#000000"),
        palette.get("accent", "#ff0000"),
    )

# =================================================
# THUMBNAIL GENERATION
# =================================================

def run_thumbnail(
    ideas_text,
    selected_idea_number,
    audience,
    region,
    content_format,
    enable_image_generation,
    image_provider,
    text_render_mode,

    emotion_style,
    shot_type,
    background_style,
    lighting,
    subject_position,
    depth,
    clutter_level,
    text_content,
    primary_color,
    secondary_color,
    accent_color,
):

    if not ideas_text or not ideas_text.strip():
        return None, "", "❌ No ideas provided."

    try:
        selected_idea_number = int(selected_idea_number)
    except:
        selected_idea_number = 1

    if selected_idea_number < 1:
        selected_idea_number = 1

    if not enable_image_generation:
        image_provider = None

    user_overrides = {}

    if emotion_style:
        user_overrides["emotion_style"] = emotion_style

    if shot_type:
        user_overrides["shot_type"] = shot_type

    if background_style:
        user_overrides["background_style"] = background_style

    if lighting:
        user_overrides["lighting"] = lighting

    if subject_position:
        user_overrides["subject_position"] = subject_position

    if depth:
        user_overrides["depth"] = depth

    if clutter_level:
        user_overrides["clutter_level"] = clutter_level

    if text_content:
        user_overrides["text_content"] = text_content

    if primary_color:
        user_overrides["primary_color"] = primary_color

    if secondary_color:
        user_overrides["secondary_color"] = secondary_color

    if accent_color:
        user_overrides["accent_color"] = accent_color

    global_state = {
        "ideas": ideas_text,
        "selected_idea_number": selected_idea_number,
        "audience": audience,
        "region": region,
        "content_format": content_format,
        "enable_image_generation": enable_image_generation,
        "image_provider": image_provider,
        "text_render_mode": text_render_mode,
        "user_overrides": user_overrides,
    }

    result = run_thumbnail_agent(global_state)

    thumbnail = result.get("thumbnail", {})

    if not thumbnail:
        return None, "", "❌ Thumbnail generation failed."

    image_b64 = thumbnail.get("image_base64")
    image_prompt = thumbnail.get("image_prompt", "")

    if enable_image_generation and image_b64:

        try:
            image_bytes = base64.b64decode(image_b64)
            image = Image.open(BytesIO(image_bytes)).convert("RGB")

            return image, image_prompt, "✅ Thumbnail generated."

        except Exception as e:
            return None, image_prompt, f"⚠️ Image decode failed: {e}"

    if image_prompt:
        return None, image_prompt, "🧠 Prompt generated (image disabled)."

    return None, "", "⚠️ No output generated."


# =================================================
# GRADIO UI
# =================================================

with gr.Blocks(title="YAAS – Ideation to Thumbnail Demo") as demo:

    gr.Markdown("# 🎯 YAAS Demo")
    gr.Markdown("## Ideation → Thumbnail Agent")

    # =================================================
    # IDEATION
    # =================================================

    gr.Markdown("### 1️⃣ Ideation Agent")

    topic = gr.Textbox(label="Topic")
    audience = gr.Textbox(label="Audience")
    region = gr.Textbox(label="Region")

    content_format = gr.Radio(
        ["short-form", "long-form"],
        value="short-form",
        label="Content Format",
    )

    generate_ideas_btn = gr.Button("Generate Ideas")

    ideation_output = gr.Textbox(
        label="Generated Ideas (Editable)",
        lines=10,
        interactive=True,
    )

    ideation_status = gr.Markdown()

    generate_ideas_btn.click(
        run_ideation,
        inputs=[topic, audience, region, content_format],
        outputs=[ideation_output, ideation_status],
    )

    # =================================================
    # THUMBNAIL
    # =================================================

    gr.Markdown("### 2️⃣ Thumbnail Agent")

    selected_idea_number = gr.Number(value=1, precision=0)

    enable_image_generation = gr.Checkbox(label="Enable Image Generation")

    image_provider = gr.Dropdown(
        ["stability", "gemini"],
        value="stability",
        label="Image Provider",
    )

    text_render_mode = gr.Radio(
        [
            ("Overlay Text", "overlay"),
            ("Bake Text", "baked"),
            ("No Text", "none"),
        ],
        value="overlay",
        label="Text Rendering Mode",
    )

    analyze_thumbnail_btn = gr.Button("Analyze Content (Auto Fill Spec)")

    # =================================================
    # OVERRIDES
    # =================================================

    gr.Markdown("### 🎨 Optional Thumbnail Overrides")

    emotion_style = gr.Dropdown(
        ["", "excited", "dramatic", "professional", "friendly", "serious"],
        label="Emotion Style",
    )

    shot_type = gr.Dropdown(
        ["", "close-up", "mid-shot", "wide"],
        label="Shot Type",
    )

    background_style = gr.Dropdown(
        ["", "clean", "blurred", "realistic", "studio"],
        label="Background Style",
    )

    lighting = gr.Dropdown(
        ["", "soft studio", "cinematic", "natural"],
        label="Lighting",
    )

    subject_position = gr.Dropdown(
        ["", "center", "left", "right"],
        label="Subject Position",
    )

    depth = gr.Dropdown(
        ["", "shallow", "medium"],
        label="Depth",
    )

    clutter_level = gr.Dropdown(
        ["", "low", "medium"],
        label="Clutter Level",
    )

    text_content = gr.Textbox(
        label="Override Thumbnail Text",
        placeholder="Optional",
    )

    primary_color = gr.ColorPicker(label="Primary Color")
    secondary_color = gr.ColorPicker(label="Secondary Color")
    accent_color = gr.ColorPicker(label="Accent Color")

    analyze_thumbnail_btn.click(
        prefill_thumbnail_spec,
        inputs=[
            ideation_output,
            selected_idea_number,
            audience,
            region,
            content_format,
        ],
        outputs=[
            emotion_style,
            shot_type,
            background_style,
            lighting,
            subject_position,
            depth,
            clutter_level,
            text_content,
            primary_color,
            secondary_color,
            accent_color,
        ],
    )

    generate_thumbnail_btn = gr.Button("Generate Thumbnail")

    thumbnail_image = gr.Image(type="pil", label="Generated Thumbnail")

    thumbnail_prompt = gr.Textbox(
        label="Generated Prompt",
        lines=6,
    )

    thumbnail_status = gr.Markdown()

    generate_thumbnail_btn.click(
        run_thumbnail,
        inputs=[
            ideation_output,
            selected_idea_number,
            audience,
            region,
            content_format,
            enable_image_generation,
            image_provider,
            text_render_mode,
            emotion_style,
            shot_type,
            background_style,
            lighting,
            subject_position,
            depth,
            clutter_level,
            text_content,
            primary_color,
            secondary_color,
            accent_color,
        ],
        outputs=[
            thumbnail_image,
            thumbnail_prompt,
            thumbnail_status,
        ],
    )

    gr.Markdown(
        """
---

### Notes

• Ideation output can be edited manually  
• Analyze Content auto-fills thumbnail design suggestions  
• Overrides allow creators to fine-tune thumbnails  
• Prompt-only mode works when image generation is disabled  
• Overlay text gives the best readability
"""
    )

demo.launch()