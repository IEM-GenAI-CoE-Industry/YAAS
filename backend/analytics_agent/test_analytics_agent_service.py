"""
test_analytics_agent_service.py
--------------------------------
Comprehensive test suite for AnalyticsAgent.

Run with:
    pip install pytest pytest-mock
    pytest test_analytics_agent_service.py -v

Or from any directory:
    pytest /Users/satabarto/Project/YAAS/YAAS/backend/analytics_agent/test_analytics_agent_service.py -v
"""

import sys
sys.path.insert(0, "/Users/satabarto/Project/YAAS/YAAS/backend/analytics_agent")

import pytest
from unittest.mock import MagicMock, patch, PropertyMock

from analytics_agent_service import (
    AnalyticsAgent,
    VideoMetrics,
    PerformanceInsight,
    display_results,
)


# ──────────────────────────────────────────────
# Fixtures
# ──────────────────────────────────────────────

@pytest.fixture
def mock_credentials():
    return MagicMock()


@pytest.fixture
def agent(mock_credentials):
    with patch("analytics_agent_service.build"):
        return AnalyticsAgent(credentials=mock_credentials)


@pytest.fixture
def sample_metrics():
    return VideoMetrics(
        video_id="abc123",
        title="Test Video",
        views=10000,
        likes=400,
        comments=60,
        watch_time=5000.0,
        average_view_duration=180.0,
        engagement_rate=0.046,
        click_through_rate=None,
        demographics={"age": {"18-24": 0.4, "25-34": 0.3}, "gender": {"male": 0.6, "female": 0.4}, "location": {"US": 0.5}},
        traffic_sources={"youtube search": 0.5, "suggested videos": 0.3}
    )


@pytest.fixture
def zero_views_metrics():
    return VideoMetrics(
        video_id="zero1",
        title="Zero Views Video",
        views=0,
        likes=0,
        comments=0,
        watch_time=0.0,
        average_view_duration=0.0,
        engagement_rate=0.0,
        demographics={"age": {}, "gender": {}, "location": {}},
        traffic_sources={}
    )


def _mock_youtube_response(title="Test Video", views=10000, likes=400, comments=60):
    """Build a fake YouTube Data API response."""
    return {
        "items": [{
            "statistics": {
                "viewCount": str(views),
                "likeCount": str(likes),
                "commentCount": str(comments),
            },
            "snippet": {"title": title}
        }]
    }


def _mock_analytics_rows(watch_time=5000.0, avg_duration=180.0):
    """Build a fake Analytics API watch time response."""
    return {"rows": [[watch_time, avg_duration]]}


# ──────────────────────────────────────────────
# 1. Initialisation
# ──────────────────────────────────────────────

class TestInit:
    def test_credentials_stored(self, mock_credentials):
        with patch("analytics_agent_service.build"):
            ag = AnalyticsAgent(mock_credentials)
        assert ag.credentials is mock_credentials

    def test_youtube_service_built(self, mock_credentials):
        with patch("analytics_agent_service.build") as mock_build:
            AnalyticsAgent(mock_credentials)
            calls = [c.args[0] for c in mock_build.call_args_list]
            assert "youtube" in calls

    def test_analytics_service_built(self, mock_credentials):
        with patch("analytics_agent_service.build") as mock_build:
            AnalyticsAgent(mock_credentials)
            calls = [c.args[0] for c in mock_build.call_args_list]
            assert "youtubeAnalytics" in calls

    def test_default_thresholds_set(self, agent):
        assert agent.thresholds["engagement_rate"] == 0.04
        assert agent.thresholds["like_to_view_ratio"] == 0.035
        assert agent.thresholds["comment_to_view_ratio"] == 0.005
        assert agent.thresholds["watch_time_threshold"] == 240


# ──────────────────────────────────────────────
# 2. get_video_analytics
# ──────────────────────────────────────────────

class TestGetVideoAnalytics:
    def test_returns_video_metrics_instance(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response()
        with patch.object(agent, "_get_watch_time_metrics", return_value=(5000.0, 180.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert isinstance(result, VideoMetrics)

    def test_video_id_set_correctly(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response()
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.video_id == "abc123"

    def test_title_extracted(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(title="My Reel")
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.title == "My Reel"

    def test_views_parsed_as_int(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(views=99999)
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.views == 99999
        assert isinstance(result.views, int)

    def test_likes_parsed_as_int(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(likes=500)
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.likes == 500

    def test_comments_parsed_as_int(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(comments=75)
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.comments == 75

    def test_engagement_rate_calculated(self, agent):
        # views=1000, likes=30, comments=10 → (30+10)/1000 = 0.04
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(views=1000, likes=30, comments=10)
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.engagement_rate == pytest.approx(0.04)

    def test_engagement_rate_zero_when_no_views(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(views=0, likes=0, comments=0)
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.engagement_rate == 0.0

    def test_ctr_is_none(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response()
        with patch.object(agent, "_get_watch_time_metrics", return_value=(0.0, 0.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.click_through_rate is None

    def test_raises_on_invalid_video_id(self, agent):
        agent.youtube.videos().list().execute.return_value = {"items": []}
        with pytest.raises(ValueError, match="Invalid video ID"):
            agent.get_video_analytics("bad_id")

    def test_watch_time_from_analytics_api(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response()
        with patch.object(agent, "_get_watch_time_metrics", return_value=(9999.0, 300.0)) as mock_wt, \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            result = agent.get_video_analytics("abc123")
        assert result.watch_time == 9999.0
        assert result.average_view_duration == 300.0


# ──────────────────────────────────────────────
# 3. _get_watch_time_metrics
# ──────────────────────────────────────────────

class TestGetWatchTimeMetrics:
    def test_returns_watch_time_and_avg_duration(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = _mock_analytics_rows(1234.5, 95.0)
        watch_time, avg_duration = agent._get_watch_time_metrics("abc123")
        assert watch_time == 1234.5
        assert avg_duration == 95.0

    def test_returns_zeros_when_no_rows(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {"rows": []}
        watch_time, avg_duration = agent._get_watch_time_metrics("abc123")
        assert watch_time == 0.0
        assert avg_duration == 0.0

    def test_returns_zeros_on_api_exception(self, agent):
        agent.youtube_analytics.reports().query().execute.side_effect = Exception("API error")
        watch_time, avg_duration = agent._get_watch_time_metrics("abc123")
        assert watch_time == 0.0
        assert avg_duration == 0.0

    def test_handles_none_values_in_row(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {"rows": [[None, None]]}
        watch_time, avg_duration = agent._get_watch_time_metrics("abc123")
        assert watch_time == 0.0
        assert avg_duration == 0.0

    def test_handles_missing_rows_key(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {}
        watch_time, avg_duration = agent._get_watch_time_metrics("abc123")
        assert watch_time == 0.0
        assert avg_duration == 0.0


# ──────────────────────────────────────────────
# 4. _get_audience_demographics
# ──────────────────────────────────────────────

class TestGetAudienceDemographics:
    def _setup_demo_mocks(self, agent, age_rows=None, gender_rows=None, country_rows=None):
        """Wire up three sequential execute() calls for age, gender, country."""
        execute_mock = agent.youtube_analytics.reports().query().execute
        execute_mock.side_effect = [
            {"rows": age_rows or []},
            {"rows": gender_rows or []},
            {"rows": country_rows or []},
        ]

    def test_returns_dict_with_age_gender_location_keys(self, agent):
        self._setup_demo_mocks(agent)
        result = agent._get_audience_demographics("abc123")
        assert "age" in result
        assert "gender" in result
        assert "location" in result

    def test_age_percentages_divided_by_100(self, agent):
        self._setup_demo_mocks(agent, age_rows=[["age18-24", 40.0], ["age25-34", 60.0]])
        result = agent._get_audience_demographics("abc123")
        assert result["age"]["age18-24"] == pytest.approx(0.4)
        assert result["age"]["age25-34"] == pytest.approx(0.6)

    def test_gender_percentages_divided_by_100(self, agent):
        self._setup_demo_mocks(agent, gender_rows=[["male", 70.0], ["female", 30.0]])
        result = agent._get_audience_demographics("abc123")
        assert result["gender"]["male"] == pytest.approx(0.7)

    def test_location_normalised_by_total_views(self, agent):
        self._setup_demo_mocks(agent, country_rows=[["US", 600], ["IN", 400]])
        result = agent._get_audience_demographics("abc123")
        assert result["location"]["US"] == pytest.approx(0.6)
        assert result["location"]["IN"] == pytest.approx(0.4)

    def test_empty_demographics_on_api_exception(self, agent):
        agent.youtube_analytics.reports().query().execute.side_effect = Exception("quota exceeded")
        result = agent._get_audience_demographics("abc123")
        assert result == {"age": {}, "gender": {}, "location": {}}

    def test_empty_rows_returns_empty_dicts(self, agent):
        self._setup_demo_mocks(agent)
        result = agent._get_audience_demographics("abc123")
        assert result["age"] == {}
        assert result["gender"] == {}
        assert result["location"] == {}


# ──────────────────────────────────────────────
# 5. _get_traffic_sources
# ──────────────────────────────────────────────

class TestGetTrafficSources:
    def test_normalises_to_percentage(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {
            "rows": [["YT_SEARCH", 600], ["SUGGESTED_VIDEOS", 400]]
        }
        result = agent._get_traffic_sources("abc123")
        assert result["yt search"] == pytest.approx(0.6)
        assert result["suggested videos"] == pytest.approx(0.4)

    def test_source_keys_lowercased_and_underscores_replaced(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {
            "rows": [["EXT_URL", 1000]]
        }
        result = agent._get_traffic_sources("abc123")
        assert "ext url" in result

    def test_returns_empty_dict_on_no_rows(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {"rows": []}
        result = agent._get_traffic_sources("abc123")
        assert result == {}

    def test_returns_empty_dict_on_exception(self, agent):
        agent.youtube_analytics.reports().query().execute.side_effect = Exception("error")
        result = agent._get_traffic_sources("abc123")
        assert result == {}

    def test_percentages_sum_to_one(self, agent):
        agent.youtube_analytics.reports().query().execute.return_value = {
            "rows": [["A", 300], ["B", 300], ["C", 400]]
        }
        result = agent._get_traffic_sources("abc123")
        assert sum(result.values()) == pytest.approx(1.0)


# ──────────────────────────────────────────────
# 6. generate_performance_insights
# ──────────────────────────────────────────────

class TestGeneratePerformanceInsights:
    def test_returns_list(self, agent, sample_metrics):
        result = agent.generate_performance_insights(sample_metrics)
        assert isinstance(result, list)

    def test_all_items_are_performance_insight(self, agent, sample_metrics):
        result = agent.generate_performance_insights(sample_metrics)
        assert all(isinstance(i, PerformanceInsight) for i in result)

    def test_high_engagement_insight_when_above_threshold(self, agent, sample_metrics):
        sample_metrics.engagement_rate = 0.05  # above 0.04
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "High Engagement" in types

    def test_low_engagement_insight_when_below_threshold(self, agent, sample_metrics):
        sample_metrics.engagement_rate = 0.01  # below 0.04
        sample_metrics.likes = 100
        sample_metrics.comments = 0
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Low Engagement" in types

    def test_low_like_ratio_insight(self, agent, sample_metrics):
        sample_metrics.views = 10000
        sample_metrics.likes = 10   # ratio = 0.001, below 0.035
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Low Like Ratio" in types

    def test_no_low_like_ratio_when_above_threshold(self, agent, sample_metrics):
        sample_metrics.views = 1000
        sample_metrics.likes = 100  # ratio = 0.1, above 0.035
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Low Like Ratio" not in types

    def test_low_comment_activity_insight(self, agent, sample_metrics):
        sample_metrics.views = 10000
        sample_metrics.comments = 1  # ratio = 0.0001, below 0.005
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Low Comment Activity" in types

    def test_low_avg_view_duration_insight(self, agent, sample_metrics):
        sample_metrics.average_view_duration = 30.0  # below 60s
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Low Average View Duration" in types

    def test_strong_retention_insight(self, agent, sample_metrics):
        sample_metrics.average_view_duration = 300.0  # above 240s
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Strong Retention" in types

    def test_no_view_duration_insight_when_zero(self, agent, sample_metrics):
        sample_metrics.average_view_duration = 0.0
        insights = agent.generate_performance_insights(sample_metrics)
        types = [i.insight_type for i in insights]
        assert "Low Average View Duration" not in types
        assert "Strong Retention" not in types

    def test_insights_have_non_empty_messages(self, agent, sample_metrics):
        insights = agent.generate_performance_insights(sample_metrics)
        for insight in insights:
            assert insight.message
            assert insight.recommendation

    def test_priority_values_are_valid(self, agent, sample_metrics):
        insights = agent.generate_performance_insights(sample_metrics)
        valid_priorities = {"high", "medium", "low"}
        for insight in insights:
            assert insight.priority in valid_priorities

    def test_zero_views_does_not_raise(self, agent, zero_views_metrics):
        result = agent.generate_performance_insights(zero_views_metrics)
        assert isinstance(result, list)

    def test_engagement_rate_appears_in_message(self, agent, sample_metrics):
        sample_metrics.engagement_rate = 0.046
        insights = agent.generate_performance_insights(sample_metrics)
        engagement_insights = [i for i in insights if "Engagement" in i.insight_type]
        assert any("0.046" in i.message for i in engagement_insights)


# ──────────────────────────────────────────────
# 7. VideoMetrics dataclass
# ──────────────────────────────────────────────

class TestVideoMetrics:
    def test_default_ctr_is_none(self):
        m = VideoMetrics(
            video_id="x", title="t", views=1, likes=1,
            comments=1, watch_time=1.0, average_view_duration=1.0,
            engagement_rate=0.1
        )
        assert m.click_through_rate is None

    def test_default_demographics_is_empty_dict(self):
        m = VideoMetrics(
            video_id="x", title="t", views=1, likes=1,
            comments=1, watch_time=1.0, average_view_duration=1.0,
            engagement_rate=0.1
        )
        assert m.demographics == {}

    def test_default_traffic_sources_is_empty_dict(self):
        m = VideoMetrics(
            video_id="x", title="t", views=1, likes=1,
            comments=1, watch_time=1.0, average_view_duration=1.0,
            engagement_rate=0.1
        )
        assert m.traffic_sources == {}


# ──────────────────────────────────────────────
# 8. PerformanceInsight dataclass
# ──────────────────────────────────────────────

class TestPerformanceInsight:
    def test_default_priority_is_medium(self):
        insight = PerformanceInsight("type", "msg", "rec")
        assert insight.priority == "medium"

    def test_custom_priority_set(self):
        insight = PerformanceInsight("type", "msg", "rec", priority="high")
        assert insight.priority == "high"


# ──────────────────────────────────────────────
# 9. display_results
# ──────────────────────────────────────────────

class TestDisplayResults:
    def test_prints_title(self, sample_metrics, capsys):
        display_results(sample_metrics, [])
        captured = capsys.readouterr()
        assert "Test Video" in captured.out

    def test_prints_video_id(self, sample_metrics, capsys):
        display_results(sample_metrics, [])
        captured = capsys.readouterr()
        assert "abc123" in captured.out

    def test_prints_views(self, sample_metrics, capsys):
        display_results(sample_metrics, [])
        captured = capsys.readouterr()
        assert "10,000" in captured.out

    def test_ctr_unavailable_message(self, sample_metrics, capsys):
        sample_metrics.click_through_rate = None
        display_results(sample_metrics, [])
        captured = capsys.readouterr()
        assert "unavailable" in captured.out

    def test_prints_insight_type(self, sample_metrics, capsys):
        insight = PerformanceInsight("Low Engagement", "msg", "rec", "high")
        display_results(sample_metrics, [insight])
        captured = capsys.readouterr()
        assert "Low Engagement" in captured.out

    def test_prints_recommendation(self, sample_metrics, capsys):
        insight = PerformanceInsight("type", "msg", "Do something now.", "medium")
        display_results(sample_metrics, [insight])
        captured = capsys.readouterr()
        assert "Do something now." in captured.out

    def test_prints_demographics_when_present(self, sample_metrics, capsys):
        display_results(sample_metrics, [])
        captured = capsys.readouterr()
        assert "AUDIENCE DEMOGRAPHICS" in captured.out

    def test_prints_traffic_sources_when_present(self, sample_metrics, capsys):
        display_results(sample_metrics, [])
        captured = capsys.readouterr()
        assert "TRAFFIC SOURCES" in captured.out

    def test_handles_none_metrics(self, capsys):
        display_results(None, [])
        captured = capsys.readouterr()
        assert "Failed to fetch" in captured.out


# ──────────────────────────────────────────────
# 10. Integration
# ──────────────────────────────────────────────

class TestIntegration:
    def test_full_pipeline_returns_insights_for_high_performer(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(
            views=50000, likes=3000, comments=500
        )
        with patch.object(agent, "_get_watch_time_metrics", return_value=(20000.0, 300.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {"18-24": 0.5}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={"yt search": 0.7}):
            metrics = agent.get_video_analytics("abc123")
            insights = agent.generate_performance_insights(metrics)

        assert metrics.views == 50000
        assert metrics.watch_time == 20000.0
        types = [i.insight_type for i in insights]
        assert "Strong Retention" in types
        assert "High Engagement" in types

    def test_full_pipeline_returns_insights_for_low_performer(self, agent):
        agent.youtube.videos().list().execute.return_value = _mock_youtube_response(
            views=10000, likes=10, comments=2
        )
        with patch.object(agent, "_get_watch_time_metrics", return_value=(100.0, 20.0)), \
             patch.object(agent, "_get_audience_demographics", return_value={"age": {}, "gender": {}, "location": {}}), \
             patch.object(agent, "_get_traffic_sources", return_value={}):
            metrics = agent.get_video_analytics("abc123")
            insights = agent.generate_performance_insights(metrics)

        types = [i.insight_type for i in insights]
        assert "Low Engagement" in types
        assert "Low Average View Duration" in types