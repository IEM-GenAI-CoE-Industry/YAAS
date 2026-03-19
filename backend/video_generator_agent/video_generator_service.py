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

Requirements:
    pip install google-genai
"""

import os
import time
import json
from google import genai                 # ✅ Correct SDK (google-genai)
from google.genai import types           # ✅ Correct import path
from util.system_prompt import PROMPT_VIDEO_GENERATOR



class VideoGeneratorService:
    def __init__(self, api_key=None):
        self.GEMINI_API_KEY = api_key or os.environ.get("GEMINI_API_KEY")

    def build_prompt(self, transcript, tone, sound_enabled):
        if sound_enabled:
            audio_section = "\nInclude synchronized audio, ambient sound effects, and dialogue matching the transcript.\n"
        else:
            audio_section = "\nSilent cinematic video with only environmental ambiance.\nNo spoken dialogue.\n"

        prompt = PROMPT_VIDEO_GENERATOR.format(
            transcript=transcript,
            tone=tone,
            audio_section=audio_section,
        )

        return prompt.strip()

    def generate_video(self, prompt, output_file, aspect_ratio="9:16", resolution="720p", sound_enabled=False):
        client = genai.Client(api_key=self.GEMINI_API_KEY)

        print("\nStarting video generation...\n")

        operation = client.models.generate_videos(
            model="veo-3.0-generate-001",
            prompt=prompt,
            config=types.GenerateVideosConfig(
                aspect_ratio=aspect_ratio,
                resolution=resolution,
            )
        )

        # ✅ Poll until done, then check error once outside the loop
        while not operation.done:
            print("Rendering video... please wait")
            time.sleep(10)
            operation = client.operations.get(operation)

        if operation.error:
            print(f"\nERROR: Video generation failed - {operation.error}")
            return None

        print("Video generation finished")

        video = operation.response.generated_videos[0]

        client.files.download(file=video.video)
        video.video.save(output_file)

        print(f"\nSaved video as: {output_file}")
        return output_file

    def generate_reel(
        self,
        transcript,
        tone="cinematic inspirational storytelling",
        aspect_ratio="9:16",
        resolution="720p",
        sound_enabled=False,
        output_filename="my_reel_video.mp4"
    ):
        prompt = self.build_prompt(transcript, tone, sound_enabled)
        return self.generate_video(prompt, output_filename, aspect_ratio, resolution, sound_enabled)

    def generate_from_script_timeline(self, timeline_json, output_filename="generated_reel.mp4"):
        """
        Generate video from script agent timeline JSON output.
        Extracts transcript from voiceover texts, tone, aspect_ratio, etc.
        """
        data = json.loads(timeline_json) if isinstance(timeline_json, str) else timeline_json

        # ✅ Guard against missing or empty timeline
        if not data.get("timeline"):
            raise ValueError("No timeline found in input data")

        # Extract transcript: concatenate all voiceover texts
        transcript_parts = []
        for scene in data["timeline"]:
            vo_text = scene.get("voiceover", {}).get("text", "")
            if vo_text:
                transcript_parts.append(vo_text)
        transcript = " ".join(transcript_parts)

        if not transcript:
            raise ValueError("No voiceover text found in timeline to use as transcript")

        tone = data.get("video_meta", {}).get("tone", "cinematic inspirational storytelling")
        aspect_ratio = data.get("render_hints", {}).get("aspect_ratio", "9:16")
        resolution = "720p"  # Default, or parse from render_hints if available

        # Sound enabled if any scene has music or sfx
        sound_enabled = any(
            scene.get("audio", {}).get("music_mood") not in [None, "none"] or
            scene.get("audio", {}).get("sfx")
            for scene in data["timeline"]
        )

        return self.generate_reel(transcript, tone, aspect_ratio, resolution, sound_enabled, output_filename)