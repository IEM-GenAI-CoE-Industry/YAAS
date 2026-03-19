"""
YouTube Analytics Agent
--------------------------------
Fetch and analyze real YouTube video performance data using OAuth 2.0.

APIs Used:
- YouTube Data API v3     (video metadata: views, likes, comments, title)
- YouTube Analytics API v2 (watch time, demographics, traffic sources)

Prerequisites:
    pip install google-auth-oauthlib google-api-python-client python-dotenv
    - client_secrets.json must exist in the working directory
    - YouTube Data API v3 and YouTube Analytics API enabled in GCP
    - OAuth consent screen configured with required scopes
"""

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from util.constants import ANALYTICS_SCOPES

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class VideoMetrics:
    video_id: str
    title: str
    views: int
    likes: int
    comments: int
    watch_time: float               # estimatedMinutesWatched from Analytics API
    average_view_duration: float    # averageViewDuration from Analytics API
    engagement_rate: float          # (likes + comments) / views
    # CTR is unavailable via public YouTube APIs at video level.
    # Only accessible in YouTube Studio with private credentials.
    click_through_rate: Optional[float] = None
    demographics: Dict[str, Any] = field(default_factory=dict)
    traffic_sources: Dict[str, float] = field(default_factory=dict)


@dataclass
class PerformanceInsight:
    insight_type: str
    message: str
    recommendation: str
    priority: str = "medium"


class AnalyticsAgent:
    """
    YouTube Analytics Agent using OAuth 2.0 authentication.

    Fetches real data from:
    - YouTube Data API v3 (video metadata)
    - YouTube Analytics API v2 (watch time, demographics, traffic sources)
    """

    def __init__(self, credentials):
        """
        Initialize the agent with OAuth credentials.

        Args:
            credentials: google.oauth2.credentials.Credentials from OAuth flow
        """
        self.credentials = credentials
        self.youtube = self._build_youtube_service()
        self.youtube_analytics = self._build_youtube_analytics_service()
        self.thresholds = {
            "engagement_rate": 0.04,
            "like_to_view_ratio": 0.035,
            "comment_to_view_ratio": 0.005,
            "watch_time_threshold": 240
        }

    def _build_youtube_service(self):
        """Build YouTube Data API v3 service with OAuth credentials."""
        return build("youtube", "v3", credentials=self.credentials)

    def _build_youtube_analytics_service(self):
        """Build YouTube Analytics API v2 service with OAuth credentials."""
        return build("youtubeAnalytics", "v2", credentials=self.credentials)

    def get_video_analytics(self, video_id: str) -> VideoMetrics:
        """
        Fetch real analytics for a video.

        Uses YouTube Data API for metadata and YouTube Analytics API for
        watch time, demographics, and traffic sources.
        """
        logger.info(f"Fetching analytics for video: {video_id}")

        request = self.youtube.videos().list(part="statistics,snippet", id=video_id)
        response = request.execute()

        if not response.get("items"):
            raise ValueError("Invalid video ID or video not found.")

        video_data = response["items"][0]
        stats = video_data["statistics"]
        snippet = video_data["snippet"]

        views = int(stats.get("viewCount", 0))
        likes = int(stats.get("likeCount", 0))
        comments = int(stats.get("commentCount", 0))

        # shareCount is deprecated in YouTube Data API — excluded from engagement
        engagement_rate = (likes + comments) / views if views > 0 else 0

        watch_time, avg_view_duration = self._get_watch_time_metrics(video_id)
        demographics = self._get_audience_demographics(video_id)
        traffic_sources = self._get_traffic_sources(video_id)

        return VideoMetrics(
            video_id=video_id,
            title=snippet["title"],
            views=views,
            likes=likes,
            comments=comments,
            watch_time=watch_time,
            average_view_duration=avg_view_duration,
            engagement_rate=engagement_rate,
            click_through_rate=None,    # Not available via public API
            demographics=demographics,
            traffic_sources=traffic_sources
        )

    def _get_watch_time_metrics(self, video_id: str) -> tuple:
        """
        Fetch real watch time metrics from YouTube Analytics API.

        Returns:
            tuple: (estimatedMinutesWatched, averageViewDuration)
        """
        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

            response = self.youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="estimatedMinutesWatched,averageViewDuration",
                filters=f"video=={video_id}"
            ).execute()

            if response.get("rows") and len(response["rows"]) > 0:
                row = response["rows"][0]
                watch_time = float(row[0]) if row[0] is not None else 0.0
                avg_duration = float(row[1]) if len(row) > 1 and row[1] is not None else 0.0
                logger.info(f"Real watch time: {watch_time} min, avg duration: {avg_duration} sec")
                return watch_time, avg_duration
            else:
                logger.warning(f"No watch time data available for video {video_id}")
                return 0.0, 0.0

        except Exception as e:
            logger.warning(f"Failed to fetch watch time metrics: {e}")
            return 0.0, 0.0

    def _get_audience_demographics(self, video_id: str) -> Dict[str, Any]:
        """
        Fetch real audience demographics from YouTube Analytics API.

        Returns age group and gender distribution percentages.
        Note: Demographics may be empty for small channels or new videos.
        """
        demographics = {"age": {}, "gender": {}, "location": {}}

        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

            age_response = self.youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="viewerPercentage",
                dimensions="ageGroup",
                filters=f"video=={video_id}"
            ).execute()

            if age_response.get("rows"):
                for row in age_response["rows"]:
                    age_group = row[0]
                    percentage = float(row[1]) / 100.0 if row[1] else 0.0
                    demographics["age"][age_group] = percentage

            gender_response = self.youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="viewerPercentage",
                dimensions="gender",
                filters=f"video=={video_id}"
            ).execute()

            if gender_response.get("rows"):
                for row in gender_response["rows"]:
                    gender = row[0]
                    percentage = float(row[1]) / 100.0 if row[1] else 0.0
                    demographics["gender"][gender] = percentage

            country_response = self.youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="views",
                dimensions="country",
                maxResults=10,
                sort="-views",
                filters=f"video=={video_id}"
            ).execute()

            if country_response.get("rows"):
                total_views = sum(float(row[1]) for row in country_response["rows"])
                if total_views > 0:
                    for row in country_response["rows"]:
                        country = row[0]
                        percentage = float(row[1]) / total_views
                        demographics["location"][country] = percentage

        except Exception as e:
            logger.warning(f"Failed to fetch demographics: {e}")
            # Expected for small channels or new videos

        return demographics

    def _get_traffic_sources(self, video_id: str) -> Dict[str, float]:
        """
        Fetch real traffic source distribution from YouTube Analytics API.

        Returns percentage breakdown of traffic sources (search, suggested, etc.)
        """
        traffic_sources = {}

        try:
            end_date = datetime.now().strftime("%Y-%m-%d")
            start_date = (datetime.now() - timedelta(days=730)).strftime("%Y-%m-%d")

            response = self.youtube_analytics.reports().query(
                ids="channel==MINE",
                startDate=start_date,
                endDate=end_date,
                metrics="views",
                dimensions="insightTrafficSourceType",
                filters=f"video=={video_id}"
            ).execute()

            if response.get("rows"):
                total_views = sum(float(row[1]) for row in response["rows"])
                if total_views > 0:
                    for row in response["rows"]:
                        source_type = row[0].lower().replace("_", " ")
                        percentage = float(row[1]) / total_views
                        traffic_sources[source_type] = percentage

        except Exception as e:
            logger.warning(f"Failed to fetch traffic sources: {e}")

        return traffic_sources

    def generate_performance_insights(self, video_metrics: VideoMetrics) -> List[PerformanceInsight]:
        """
        Generate rule-based performance insights from video metrics.

        Note: CTR insights are skipped — CTR is not available via public API.
        """
        insights = []
        engagement = video_metrics.engagement_rate
        like_ratio = video_metrics.likes / video_metrics.views if video_metrics.views > 0 else 0
        comment_ratio = video_metrics.comments / video_metrics.views if video_metrics.views > 0 else 0

        if engagement < self.thresholds["engagement_rate"]:
            insights.append(PerformanceInsight(
                "Low Engagement",
                f"Engagement rate is {engagement:.3f}, below optimal levels.",
                "Add call-to-actions, ask questions, and encourage viewer interaction throughout the video.",
                "high"
            ))
        else:
            insights.append(PerformanceInsight(
                "High Engagement",
                f"Strong engagement rate of {engagement:.3f}.",
                "Your content resonates well with viewers. Continue with similar content style.",
                "low"
            ))

        if like_ratio < self.thresholds["like_to_view_ratio"]:
            insights.append(PerformanceInsight(
                "Low Like Ratio",
                f"Like-to-view ratio is {like_ratio:.4f}.",
                "Remind viewers to like the video at strategic moments (beginning, middle, end).",
                "medium"
            ))

        if comment_ratio < self.thresholds["comment_to_view_ratio"]:
            insights.append(PerformanceInsight(
                "Low Comment Activity",
                f"Comment-to-view ratio is {comment_ratio:.4f}.",
                "Pose discussion questions, respond to early comments to encourage more interaction.",
                "medium"
            ))

        if video_metrics.average_view_duration > 0:
            if video_metrics.average_view_duration < 60:
                insights.append(PerformanceInsight(
                    "Low Average View Duration",
                    f"Average view duration is {video_metrics.average_view_duration:.1f} seconds.",
                    "Improve your hook in the first 30 seconds. Consider re-structuring content to maintain interest.",
                    "high"
                ))
            elif video_metrics.average_view_duration >= 240:
                insights.append(PerformanceInsight(
                    "Strong Retention",
                    f"Excellent average view duration of {video_metrics.average_view_duration:.1f} seconds.",
                    "Your content structure keeps viewers engaged. Maintain this pacing in future videos.",
                    "low"
                ))

        return insights


def display_results(metrics: VideoMetrics, insights: List[PerformanceInsight]):
    """Display the analysis results."""
    print("\n" + "=" * 60)
    print("YOUTUBE VIDEO ANALYTICS REPORT")
    print("=" * 60)

    if metrics:
        print(f"Video: {metrics.title}")
        print(f"Video ID: {metrics.video_id}")
        print(f"Views: {metrics.views:,}")
        print(f"Likes: {metrics.likes:,}")
        print(f"Comments: {metrics.comments:,}")
        print(f"Engagement Rate: {metrics.engagement_rate:.3f}")
        print(f"Watch Time: {metrics.watch_time:,.1f} minutes")
        print(f"Avg View Duration: {metrics.average_view_duration:.1f} seconds")

        if metrics.click_through_rate is None:
            print("Click-through Rate: (unavailable via public API)")
        else:
            print(f"Click-through Rate: {metrics.click_through_rate:.3f}")

        if metrics.demographics.get("age"):
            print("\n" + "-" * 40)
            print("AUDIENCE DEMOGRAPHICS")
            print("-" * 40)
            if metrics.demographics["age"]:
                print("Age Distribution:")
                for age, pct in metrics.demographics["age"].items():
                    print(f"  {age}: {pct:.1%}")
            if metrics.demographics["gender"]:
                print("Gender Distribution:")
                for gender, pct in metrics.demographics["gender"].items():
                    print(f"  {gender}: {pct:.1%}")
            if metrics.demographics["location"]:
                print("Top Locations:")
                for loc, pct in list(metrics.demographics["location"].items())[:5]:
                    print(f"  {loc}: {pct:.1%}")

        if metrics.traffic_sources:
            print("\n" + "-" * 40)
            print("TRAFFIC SOURCES")
            print("-" * 40)
            for source, pct in sorted(metrics.traffic_sources.items(), key=lambda x: -x[1]):
                print(f"  {source}: {pct:.1%}")

        print("\n" + "-" * 40)
        print("PERFORMANCE INSIGHTS & RECOMMENDATIONS")
        print("-" * 40)

        for insight in insights:
            priority_emoji = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(insight.priority, "⚪")
            print(f"{priority_emoji} {insight.insight_type}: {insight.message}")
            if insight.recommendation:
                print(f"   💡 Recommendation: {insight.recommendation}\n")
            else:
                print("\n")
    else:
        print("Failed to fetch video metrics")

    print("=" * 60)


def run_analytics_agent(global_state: dict) -> dict:
    """
    Entry point for the Analytics Agent.
    Requires 'video_id' in global state to fetch real analytics.
    """
    video_id = global_state.get("video_id")
    if not video_id:
        raise ValueError("Analytics Agent requires 'video_id' in global state.")
        
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # client_secrets.json should be stored securely, not hardcoded locally in prod
    secrets_file = os.path.join(script_dir, "client_secrets.json")
    
    if not os.path.exists(secrets_file):
        logger.warning(f"client_secrets.json not found at {secrets_file}. Cannot run analytics.")
        return global_state
        
    try:
        flow = InstalledAppFlow.from_client_secrets_file(secrets_file, ANALYTICS_SCOPES)
        # Using run_local_server might pause a completely headless backend,
        # but matches the original agent's OAuth flow design.
        credentials = flow.run_local_server(port=0)
        
        agent = AnalyticsAgent(credentials)
        metrics = agent.get_video_analytics(video_id)
        insights = agent.generate_performance_insights(metrics)
        
        global_state["analytics"] = {
            "metrics": metrics.__dict__,
            "insights": [i.__dict__ for i in insights]
        }
        
    except Exception as e:
        logger.error(f"Analytics Agent failed: {e}")
        
    return global_state