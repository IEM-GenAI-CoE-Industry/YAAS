"""
Global-state wrapper for VideoGeneratorService.
Matches the run_X_agent(global_state) → global_state interface used by all other agents.
"""

import os
import logging

from video_generator_agent.video_generator_service import VideoGeneratorService

logger = logging.getLogger(__name__)

OUTPUT_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "output")


def run_video_generator_agent(global_state: dict) -> dict:
    """
    Entry point for the Video Generator Agent.
    Reads 'script_timeline' from global_state and writes 'video_path'.
    """
    script_timeline = global_state.get("script_timeline")

    if not script_timeline:
        raise ValueError("Video Generator Agent requires 'script_timeline' in global state.")

    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)

    output_filename = global_state.get("output_filename", "generated_reel.mp4")
    output_path = os.path.join(OUTPUT_DIR, output_filename)

    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set.")

    service = VideoGeneratorService(api_key=api_key)

    logger.info("Starting video generation from script timeline...")
    result = service.generate_from_script_timeline(script_timeline, output_filename=output_path)

    if result:
        global_state["video_path"] = result
        logger.info(f"Video saved to {result}")
    else:
        logger.warning("Video generation returned None (possible API error).")

    return global_state
