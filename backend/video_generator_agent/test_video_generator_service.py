"""
test_video_generator_service.py
--------------------------------
Comprehensive test suite for VideoGeneratorService.

Run with:
    pip install pytest pytest-mock
    pytest test_video_generator_service.py -v

Or from any directory:
    pytest /Users/satabarto/Project/YAAS/YAAS/backend/video_generator_agent/test_video_generator_service.py -v
"""

import sys
sys.path.insert(0, "/Users/satabarto/Project/YAAS/YAAS/backend/video_generator_agent")

import json
import os
import pytest
from unittest.mock import MagicMock, patch, call, PropertyMock

from video_generator_service import VideoGeneratorService


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def service():
    return VideoGeneratorService(api_key="test-api-key")


@pytest.fixture
def minimal_timeline():
    return {
        "timeline": [
            {"voiceover": {"text": "A hero rises from the ashes."}, "audio": {}},
        ]
    }


@pytest.fixture
def full_timeline():
    return {
        "video_meta": {"tone": "dark dramatic"},
        "render_hints": {"aspect_ratio": "16:9"},
        "timeline": [
            {
                "voiceover": {"text": "Scene one opens at dawn."},
                "audio": {"music_mood": "epic", "sfx": ["wind", "drums"]},
            },
            {
                "voiceover": {"text": "The journey begins now."},
                "audio": {"music_mood": "none", "sfx": []},
            },
        ],
    }


def _make_mock_operation(done=True, error=None, video_uri="gs://bucket/video.mp4"):
    """Helper: build a mock operation object returned by generate_videos."""
    mock_video_file = MagicMock()
    mock_video_file.uri = video_uri

    mock_generated_video = MagicMock()
    mock_generated_video.video = mock_video_file

    mock_response = MagicMock()
    mock_response.generated_videos = [mock_generated_video]

    op = MagicMock()
    op.done = done
    op.error = error
    op.response = mock_response
    return op


# ──────────────────────────────────────────────
# 1. Initialisation
# ──────────────────────────────────────────────

class TestInit:
    def test_explicit_api_key(self):
        svc = VideoGeneratorService(api_key="my-key")
        assert svc.GEMINI_API_KEY == "my-key"

    def test_env_var_fallback(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        svc = VideoGeneratorService()
        assert svc.GEMINI_API_KEY == "env-key"

    def test_default_placeholder_when_no_key(self, monkeypatch):
        monkeypatch.delenv("GEMINI_API_KEY", raising=False)
        svc = VideoGeneratorService()
        assert svc.GEMINI_API_KEY == "YOUR_GEMINI_API_KEY"

    def test_explicit_key_overrides_env(self, monkeypatch):
        monkeypatch.setenv("GEMINI_API_KEY", "env-key")
        svc = VideoGeneratorService(api_key="explicit-key")
        assert svc.GEMINI_API_KEY == "explicit-key"


# ──────────────────────────────────────────────
# 2. build_prompt
# ──────────────────────────────────────────────

class TestBuildPrompt:
    def test_contains_transcript(self, service):
        prompt = service.build_prompt("My story here", "epic", False)
        assert "My story here" in prompt

    def test_contains_tone(self, service):
        prompt = service.build_prompt("story", "dark thriller", False)
        assert "dark thriller" in prompt

    def test_sound_disabled_contains_silent_instruction(self, service):
        prompt = service.build_prompt("story", "tone", sound_enabled=False)
        assert "No spoken dialogue" in prompt
        assert "synchronized audio" not in prompt

    def test_sound_enabled_contains_audio_instruction(self, service):
        prompt = service.build_prompt("story", "tone", sound_enabled=True)
        assert "synchronized audio" in prompt
        assert "No spoken dialogue" not in prompt

    def test_prompt_is_stripped(self, service):
        prompt = service.build_prompt("story", "tone", False)
        assert not prompt.startswith("\n")
        assert not prompt.endswith("\n")

    def test_prompt_contains_style_keywords(self, service):
        prompt = service.build_prompt("story", "tone", False)
        for keyword in ["cinematic", "natural lighting", "shallow depth of field", "smooth motion tracking"]:
            assert keyword in prompt

    def test_empty_transcript_still_builds(self, service):
        prompt = service.build_prompt("", "tone", False)
        assert isinstance(prompt, str)
        assert len(prompt) > 0

    def test_multiline_transcript_preserved(self, service):
        transcript = "Line one.\nLine two.\nLine three."
        prompt = service.build_prompt(transcript, "tone", False)
        assert "Line one." in prompt
        assert "Line three." in prompt

    def test_special_characters_in_transcript(self, service):
        transcript = 'She said: "It\'s alive!" & ran away — fast.'
        prompt = service.build_prompt(transcript, "tone", False)
        assert transcript in prompt


# ──────────────────────────────────────────────
# 3. generate_video — happy path
# ──────────────────────────────────────────────

class TestGenerateVideoSuccess:
    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_returns_output_filename(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        result = service.generate_video("prompt", "out.mp4")

        assert result == "out.mp4"

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_calls_generate_videos_with_correct_model(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4")

        call_kwargs = mock_client.models.generate_videos.call_args
        assert call_kwargs.kwargs["model"] == "veo-3.1-generate-preview"

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_passes_prompt(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("my cinematic prompt", "out.mp4")

        call_kwargs = mock_client.models.generate_videos.call_args
        assert call_kwargs.kwargs["prompt"] == "my cinematic prompt"

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_config_aspect_ratio(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4", aspect_ratio="16:9")

        config = mock_client.models.generate_videos.call_args.kwargs["config"]
        assert config.aspect_ratio == "16:9"

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_config_resolution(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4", resolution="1080p")

        config = mock_client.models.generate_videos.call_args.kwargs["config"]
        assert config.resolution == "1080p"

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_config_person_generation_is_allow_adult(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4")

        config = mock_client.models.generate_videos.call_args.kwargs["config"]
        assert config.person_generation == "allow_adult"

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_downloads_and_saves_video(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "reel.mp4")

        video_file = op.response.generated_videos[0].video
        mock_client.files.download.assert_called_once_with(file=video_file)
        video_file.save.assert_called_once_with("reel.mp4")

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_client_initialised_with_api_key(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4")

        mock_client_cls.assert_called_once_with(api_key="test-api-key")


# ──────────────────────────────────────────────
# 4. generate_video — polling behaviour
# ──────────────────────────────────────────────

class TestGenerateVideoPolling:
    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_polls_until_done(self, mock_sleep, mock_client_cls, service):
        """Operation starts not-done, becomes done after two polls."""
        op_pending = _make_mock_operation(done=False)
        op_done = _make_mock_operation(done=True)

        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op_pending
        mock_client.operations.get.side_effect = [op_pending, op_done]

        service.generate_video("prompt", "out.mp4")

        assert mock_client.operations.get.call_count == 2

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_sleeps_between_polls(self, mock_sleep, mock_client_cls, service):
        op_pending = _make_mock_operation(done=False)
        op_done = _make_mock_operation(done=True)

        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op_pending
        mock_client.operations.get.side_effect = [op_pending, op_done]

        service.generate_video("prompt", "out.mp4")

        # sleep called once per pending iteration
        assert mock_sleep.call_count == 2
        mock_sleep.assert_called_with(10)

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_no_poll_when_immediately_done(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4")

        mock_client.operations.get.assert_not_called()
        mock_sleep.assert_not_called()


# ──────────────────────────────────────────────
# 5. generate_video — error handling
# ──────────────────────────────────────────────

class TestGenerateVideoErrors:
    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_returns_none_on_operation_error(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True, error="Safety filter triggered")
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        result = service.generate_video("prompt", "out.mp4")

        assert result is None

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_does_not_save_on_error(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True, error="API error")
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4")

        mock_client.files.download.assert_not_called()

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_prints_error_message(self, mock_sleep, mock_client_cls, service, capsys):
        op = _make_mock_operation(done=True, error="Quota exceeded")
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        service.generate_video("prompt", "out.mp4")

        captured = capsys.readouterr()
        assert "ERROR" in captured.out
        assert "Quota exceeded" in captured.out


# ──────────────────────────────────────────────
# 6. generate_reel
# ──────────────────────────────────────────────

class TestGenerateReel:
    def test_delegates_to_generate_video(self, service):
        with patch.object(service, "generate_video", return_value="reel.mp4") as mock_gv:
            result = service.generate_reel("transcript")
            mock_gv.assert_called_once()
            assert result == "reel.mp4"

    def test_uses_default_tone(self, service):
        with patch.object(service, "generate_video", return_value="reel.mp4"):
            with patch.object(service, "build_prompt", wraps=service.build_prompt) as mock_bp:
                service.generate_reel("transcript")
                _, tone_arg, _ = mock_bp.call_args.args
                assert tone_arg == "cinematic inspirational storytelling"

    def test_default_aspect_ratio_is_9_16(self, service):
        with patch.object(service, "generate_video", return_value="out.mp4") as mock_gv:
            service.generate_reel("transcript")
            assert mock_gv.call_args.args[2] == "9:16"

    def test_default_resolution_is_720p(self, service):
        with patch.object(service, "generate_video", return_value="out.mp4") as mock_gv:
            service.generate_reel("transcript")
            assert mock_gv.call_args.args[3] == "720p"

    def test_custom_output_filename_passed_through(self, service):
        with patch.object(service, "generate_video", return_value="custom.mp4") as mock_gv:
            service.generate_reel("transcript", output_filename="custom.mp4")
            assert mock_gv.call_args.args[1] == "custom.mp4"

    def test_sound_flag_passed_through(self, service):
        with patch.object(service, "generate_video", return_value="out.mp4") as mock_gv:
            service.generate_reel("transcript", sound_enabled=True)
            assert mock_gv.call_args.args[4] is True


# ──────────────────────────────────────────────
# 7. generate_from_script_timeline — parsing
# ──────────────────────────────────────────────

class TestGenerateFromScriptTimeline:

    # ── transcript extraction ──

    def test_concatenates_voiceover_texts(self, service, full_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(full_timeline)
            transcript_arg = mock_gr.call_args.args[0]
            assert "Scene one opens at dawn." in transcript_arg
            assert "The journey begins now." in transcript_arg

    def test_skips_scenes_without_voiceover(self, service):
        timeline = {
            "timeline": [
                {"voiceover": {"text": "Only this one."}, "audio": {}},
                {"audio": {}},  # no voiceover key at all
                {"voiceover": {}, "audio": {}},  # voiceover key but no text
            ]
        }
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(timeline)
            transcript_arg = mock_gr.call_args.args[0]
            assert transcript_arg == "Only this one."

    def test_accepts_json_string_input(self, service, full_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4"):
            # Should not raise
            service.generate_from_script_timeline(json.dumps(full_timeline))

    def test_accepts_dict_input(self, service, full_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4"):
            service.generate_from_script_timeline(full_timeline)

    # ── metadata extraction ──

    def test_extracts_tone_from_video_meta(self, service, full_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(full_timeline)
            tone_arg = mock_gr.call_args.args[1]
            assert tone_arg == "dark dramatic"

    def test_default_tone_when_video_meta_missing(self, service, minimal_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(minimal_timeline)
            tone_arg = mock_gr.call_args.args[1]
            assert tone_arg == "cinematic inspirational storytelling"

    def test_extracts_aspect_ratio_from_render_hints(self, service, full_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(full_timeline)
            aspect_ratio_arg = mock_gr.call_args.args[2]
            assert aspect_ratio_arg == "16:9"

    def test_default_aspect_ratio_when_render_hints_missing(self, service, minimal_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(minimal_timeline)
            aspect_ratio_arg = mock_gr.call_args.args[2]
            assert aspect_ratio_arg == "9:16"

    def test_resolution_is_always_720p(self, service, full_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(full_timeline)
            resolution_arg = mock_gr.call_args.args[3]
            assert resolution_arg == "720p"

    # ── sound detection ──

    def test_sound_enabled_when_music_mood_present(self, service):
        timeline = {
            "timeline": [
                {"voiceover": {"text": "story"}, "audio": {"music_mood": "epic"}},
            ]
        }
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(timeline)
            sound_arg = mock_gr.call_args.args[4]
            assert sound_arg is True

    def test_sound_enabled_when_sfx_present(self, service):
        timeline = {
            "timeline": [
                {"voiceover": {"text": "story"}, "audio": {"sfx": ["explosion"]}},
            ]
        }
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(timeline)
            sound_arg = mock_gr.call_args.args[4]
            assert sound_arg is True

    def test_sound_disabled_when_music_mood_is_none_string(self, service):
        timeline = {
            "timeline": [
                {"voiceover": {"text": "story"}, "audio": {"music_mood": "none", "sfx": []}},
            ]
        }
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(timeline)
            sound_arg = mock_gr.call_args.args[4]
            assert sound_arg is False

    def test_sound_disabled_when_audio_section_empty(self, service, minimal_timeline):
        with patch.object(service, "generate_reel", return_value="out.mp4") as mock_gr:
            service.generate_from_script_timeline(minimal_timeline)
            sound_arg = mock_gr.call_args.args[4]
            assert sound_arg is False

    # ── output filename ──

    def test_default_output_filename(self, service, minimal_timeline):
        with patch.object(service, "generate_reel", return_value="generated_reel.mp4") as mock_gr:
            service.generate_from_script_timeline(minimal_timeline)
            filename_arg = mock_gr.call_args.args[5]
            assert filename_arg == "generated_reel.mp4"

    def test_custom_output_filename(self, service, minimal_timeline):
        with patch.object(service, "generate_reel", return_value="custom.mp4") as mock_gr:
            service.generate_from_script_timeline(minimal_timeline, output_filename="custom.mp4")
            filename_arg = mock_gr.call_args.args[5]
            assert filename_arg == "custom.mp4"

    # ── error cases ──

    def test_raises_on_missing_timeline_key(self, service):
        with pytest.raises(ValueError, match="No timeline found"):
            service.generate_from_script_timeline({"video_meta": {}})

    def test_raises_on_empty_timeline_list(self, service):
        with pytest.raises(ValueError, match="No timeline found"):
            service.generate_from_script_timeline({"timeline": []})

    def test_raises_on_empty_voiceover_texts(self, service):
        timeline = {
            "timeline": [
                {"voiceover": {"text": ""}, "audio": {}},
                {"voiceover": {}, "audio": {}},
            ]
        }
        with pytest.raises(ValueError, match="No voiceover text found"):
            service.generate_from_script_timeline(timeline)

    def test_raises_on_invalid_json_string(self, service):
        with pytest.raises((json.JSONDecodeError, ValueError)):
            service.generate_from_script_timeline("this is not json")

    def test_returns_result_of_generate_reel(self, service, minimal_timeline):
        with patch.object(service, "generate_reel", return_value="final.mp4"):
            result = service.generate_from_script_timeline(minimal_timeline)
            assert result == "final.mp4"


# ──────────────────────────────────────────────
# 8. Integration: generate_reel → generate_video
# ──────────────────────────────────────────────

class TestIntegration:
    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_generate_reel_full_flow(self, mock_sleep, mock_client_cls, service):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        result = service.generate_reel(
            transcript="A lone astronaut drifts through an infinite cosmos.",
            tone="sci-fi epic",
            aspect_ratio="9:16",
            resolution="720p",
            sound_enabled=False,
            output_filename="space_reel.mp4"
        )

        assert result == "space_reel.mp4"

        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert call_kwargs["model"] == "veo-3.1-generate-preview"
        assert "astronaut" in call_kwargs["prompt"]
        assert "sci-fi epic" in call_kwargs["prompt"]
        assert "No spoken dialogue" in call_kwargs["prompt"]

        video_file = op.response.generated_videos[0].video
        video_file.save.assert_called_once_with("space_reel.mp4")

    @patch("video_generator_service.genai.Client")
    @patch("video_generator_service.time.sleep", return_value=None)
    def test_generate_from_timeline_full_flow(self, mock_sleep, mock_client_cls, service, full_timeline):
        op = _make_mock_operation(done=True)
        mock_client = mock_client_cls.return_value
        mock_client.models.generate_videos.return_value = op

        result = service.generate_from_script_timeline(full_timeline, output_filename="timeline_reel.mp4")

        assert result == "timeline_reel.mp4"
        call_kwargs = mock_client.models.generate_videos.call_args.kwargs
        assert "Scene one opens at dawn." in call_kwargs["prompt"]
        assert "The journey begins now." in call_kwargs["prompt"]

        config = call_kwargs["config"]
        assert config.aspect_ratio == "16:9"
        assert config.resolution == "720p"
        assert config.person_generation == "allow_adult"