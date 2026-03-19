# YAAS Thumbnail Agent --- Technical Documentation

## Overview

The **Thumbnail Agent** in YAAS converts a **YouTube video idea** into a
**high-CTR thumbnail design specification and optionally a generated
thumbnail image**.

The system uses:

-   Structured JSON prompting
-   LangGraph orchestration
-   Deterministic design rules
-   Optional user overrides
-   Multi-provider image generation

The agent outputs:

-   A structured thumbnail design specification
-   A deterministic image generation prompt
-   An optional generated thumbnail image
-   Optional overlay text rendering

------------------------------------------------------------------------

# Architecture

The Thumbnail Agent is implemented as a **LangGraph workflow**.

Ideation Agent → Thumbnail Agent

Nodes:

1.  analyze_content
2.  apply_user_overrides
3.  apply_design_rules
4.  generate_prompt
5.  generate_image (conditional)
6.  post_render_text (conditional)

------------------------------------------------------------------------

# Input State

The Thumbnail Agent receives the following fields.

  Field                     Type                     Description
  ------------------------- ------------------------ ---------------------------
  idea_title                str                      Selected video idea title
  idea_description          str                      Idea description
  audience                  str                      Target audience
  region                    str                      Target region
  content_format            short-form / long-form   Video format
  script                    str                      Optional script
  enable_image_generation   bool                     Enable image generation
  image_provider            stability / gemini       Image provider
  text_render_mode          overlay / baked / none   Text rendering strategy

------------------------------------------------------------------------

# Thumbnail Specification Schema

``` json
{
  "subject": {
    "type": "human | object",
    "description": "visual description",
    "expression": "facial expression",
    "pose": "body pose",
    "shot_type": "close-up | mid-shot | wide"
  },
  "background": {
    "style": "clean | blurred | realistic | studio",
    "clutter_level": "low | medium",
    "lighting": "soft studio | cinematic | natural"
  },
  "emotion_style": "excited | dramatic | professional | friendly | serious",
  "color_palette": {
    "primary": "#HEX",
    "secondary": "#HEX",
    "accent": "#HEX"
  },
  "composition": {
    "subject_position": "center | left | right",
    "depth": "shallow | medium"
  },
  "text": {
    "content": "max 6 words",
    "style": "bold | clean | dramatic"
  }
}
```

------------------------------------------------------------------------

# Node Responsibilities

## analyze_content

Uses an LLM to generate the structured thumbnail specification.

Inputs:

-   idea_title
-   idea_description
-   audience
-   region
-   content_format
-   script

Output:

-   thumbnail_spec

------------------------------------------------------------------------

## apply_user_overrides

Allows UI or user input to modify parts of the thumbnail specification.

Supported overrides include:

-   emotion_style
-   shot_type
-   background_style
-   lighting
-   subject_position
-   depth
-   clutter_level
-   text_content
-   primary_color
-   secondary_color
-   accent_color

------------------------------------------------------------------------

## apply_design_rules

Applies deterministic safety rules to ensure design quality.

Rules applied:

-   Color palette fallback
-   Text length enforcement
-   Uppercase text for short-form
-   Composition defaults
-   Background clutter defaults

------------------------------------------------------------------------

## generate_prompt

Converts the structured specification into a deterministic image
generation prompt.

Prompt components include:

-   Subject description
-   Pose and expression
-   Shot framing
-   Composition layout
-   Background style
-   Lighting style
-   Emotional tone
-   Color palette
-   Text rendering rules
-   Image quality constraints

------------------------------------------------------------------------

## generate_image

Generates the thumbnail image using external models.

Supported providers:

-   Stability AI
-   Gemini

Execution strategy:

1.  Attempt selected provider
2.  Fallback to alternative provider
3.  Return prompt-only mode if generation fails

Outputs:

-   image_base64
-   image_provider

------------------------------------------------------------------------

## post_render_text

Adds text overlay to the generated image when:

text_render_mode = overlay

Rendering features:

-   Smart text wrapping
-   Automatic font scaling
-   Stroke outline
-   Smart positioning

------------------------------------------------------------------------

# Output State

The Thumbnail Agent writes results into:

global_state\["thumbnail"\]

Output structure:

``` python
{
  "idea_title": str,
  "idea_description": str,
  "audience": str,
  "region": str,
  "content_format": str,
  "thumbnail_spec": dict,
  "thumbnail_text": str,
  "image_prompt": str,
  "image_provider": str,
  "image_base64": str,
  "text_render_mode": str
}
```

------------------------------------------------------------------------

# Summary

The Thumbnail Agent transforms **video ideas into production-ready
thumbnail designs** using:

-   Structured JSON reasoning
-   Deterministic prompt construction
-   Conditional image generation
-   Modular LangGraph orchestration

This design keeps the system **scalable, debuggable, and extensible** as
new agents are added.
