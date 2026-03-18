"""
Veo 3.1 Reel Generator
--------------------------------
Generate cinematic short videos using Google's Veo API.

Inputs:
- transcript (main story / script)
- tone/style
- aspect ratio
- sound toggle
- output filename
"""

import os
import time
from google import genai
from google.genai import types

# -------------------------
# USER CONFIGURATION
# -------------------------

# Securely fetches API Key from environment variable
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "YOUR_GEMINI_API_KEY")

TRANSCRIPT = """
PLACE_TRANSCRIPT_HERE
"""

TONE = "cinematic inspirational storytelling"

ASPECT_RATIO = "9:16"   # reels
RESOLUTION = "720p"     # cheaper for first run

DURATION = 8            # Veo limit
SOUND_ENABLED = False   # enable later if needed

OUTPUT_FILENAME = "my_reel_video.mp4"


# -------------------------
# PROMPT BUILDER
# -------------------------

def build_prompt(transcript, tone, sound_enabled):

    if sound_enabled:
        audio_section = """
        Include synchronized audio, ambient sound effects, and dialogue matching the transcript.
        """
    else:
        audio_section = """
        Silent cinematic video with only environmental ambiance.
        No spoken dialogue.
        """

    prompt = f"""
Create a high quality cinematic social media reel.

Story:
{transcript}

Tone:
{tone}

Video Style:
professional filmmaking quality
smooth cinematic camera movement
high detail textures
natural lighting
shallow depth of field

{audio_section}

Camera:
dynamic cinematic framing
smooth motion tracking
"""

    return prompt.strip()


# -------------------------
# VIDEO GENERATION
# -------------------------

def generate_video(prompt, output_file, sound_enabled):

    client = genai.Client(api_key=GEMINI_API_KEY)

    print("\nStarting video generation...\n")

    operation = client.models.generate_videos(
        model="veo-3.1-generate-preview",
        prompt=prompt,
        config=types.GenerateVideosConfig(
            aspect_ratio=ASPECT_RATIO,
            resolution=RESOLUTION,
            person_generation="allow_adult"  # Optimized for API compatibility
        )
    )

    while not operation.done:
        print("Rendering video... please wait")
        time.sleep(10)
        operation = client.operations.get(operation)

        if operation.error:
            print(f"\nERROR: Video generation failed - {operation.error}")
            return

    print("Video generation finished")

    video = operation.response.generated_videos[0]

    client.files.download(file=video.video)
    video.video.save(output_file)

    print(f"\nSaved video as: {output_file}")


# -------------------------
# MAIN
# -------------------------

def main():

    prompt = build_prompt(
        TRANSCRIPT,
        TONE,
        SOUND_ENABLED
    )

    generate_video(prompt, OUTPUT_FILENAME, SOUND_ENABLED)


if __name__ == "__main__":
    main()
