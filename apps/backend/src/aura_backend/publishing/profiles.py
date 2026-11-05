"""M13 Phase 1: Publishing Foundation — Platform Profiles.

Built-in configuration profiles for each publishing platform.
"""

from dataclasses import dataclass

from .models import PlatformType


@dataclass(frozen=True)
class PublishingProfile:
    """Immutable platform-specific publishing profile"""

    platform: PlatformType
    max_duration_seconds: int
    min_duration_seconds: int
    supported_resolutions: tuple[str, ...]  # "1080p", "720p", "480p", "360p", "240p"
    supported_aspect_ratios: tuple[str, ...]  # "16:9", "9:16", "1:1", "4:5"
    required_aspect_ratio: str | None = None
    thumbnail_width: int = 1280
    thumbnail_height: int = 720
    thumbnail_formats: tuple[str, ...] = ("jpg", "png")
    max_title_length: int = 100
    max_description_length: int = 5000
    max_hashtags: int = 30
    max_tags: int = 50
    supports_scheduling: bool = True
    supports_premiere: bool = False
    supports_live: bool = False
    supports_playlist: bool = True
    supports_monetization: bool = True
    supports_comments: bool = True
    supports_embedding: bool = True
    supports_categories: bool = True
    supported_categories: tuple[str, ...] = ()
    custom_metadata_supported: bool = False
    allows_auto_captions: bool = True
    allows_auto_translation: bool = True
    recommended_bitrate_kbps: int = 5000
    recommended_framerate: int = 30
    max_file_size_mb: int = 100000
    supported_codecs: tuple[str, ...] = ("h264", "h265", "vp9")
    supports_hdr: bool = False
    supports_spatial_audio: bool = False

    def to_dict(self) -> dict:
        return {
            "platform": self.platform.value,
            "max_duration_seconds": self.max_duration_seconds,
            "supported_resolutions": self.supported_resolutions,
            "thumbnail_requirements": f"{self.thumbnail_width}x{self.thumbnail_height}",
            "max_title_length": self.max_title_length,
            "max_description_length": self.max_description_length,
            "supports_scheduling": self.supports_scheduling,
            "supports_monetization": self.supports_monetization,
            "recommended_bitrate_kbps": self.recommended_bitrate_kbps,
        }


# Built-in platform profiles

YOUTUBE_PROFILE = PublishingProfile(
    platform=PlatformType.YOUTUBE,
    max_duration_seconds=12 * 60 * 60,  # 12 hours
    min_duration_seconds=1,
    supported_resolutions=("2160p", "1440p", "1080p", "720p", "480p", "360p", "240p"),
    supported_aspect_ratios=("16:9",),
    required_aspect_ratio="16:9",
    thumbnail_width=1280,
    thumbnail_height=720,
    max_title_length=100,
    max_description_length=5000,
    max_hashtags=30,
    max_tags=500,
    supports_scheduling=True,
    supports_premiere=True,
    supports_playlist=True,
    supports_monetization=True,
    supports_categories=True,
    supported_categories=(
        "Music",
        "Short Movies",
        "Short Movies",
        "Trailers",
        "Trailers",
        "Entertainment",
        "Shows",
        "Shows",
        "Movies",
        "Documentaries",
        "Animation",
        "Action/Adventure",
        "Classics",
        "Comedy",
        "Comedy",
        "Crime",
        "Documentary",
        "Drama",
        "Family",
        "Foreign",
        "Horror",
        "Sci-Fi/Fantasy",
        "Thriller",
        "Shorts",
        "Shows",
        "Sports",
        "Sports",
        "Upcoming",
        "Watch Later",
    ),
    allows_auto_captions=True,
    allows_auto_translation=True,
    recommended_bitrate_kbps=8000,
    recommended_framerate=60,
    max_file_size_mb=256000,
    supported_codecs=("h264", "h265", "vp9", "av1"),
    supports_hdr=True,
    supports_spatial_audio=True,
)

YOUTUBE_SHORTS_PROFILE = PublishingProfile(
    platform=PlatformType.YOUTUBE_SHORTS,
    max_duration_seconds=60,
    min_duration_seconds=1,
    supported_resolutions=("1080p", "720p", "480p"),
    supported_aspect_ratios=("9:16",),
    required_aspect_ratio="9:16",
    thumbnail_width=1080,
    thumbnail_height=1920,
    max_title_length=100,
    max_description_length=2500,
    max_hashtags=30,
    supports_scheduling=True,
    supports_premiere=False,
    supports_playlist=False,
    supports_monetization=True,
    supports_categories=False,
    allows_auto_captions=True,
    allows_auto_translation=True,
    recommended_bitrate_kbps=6000,
    recommended_framerate=60,
    max_file_size_mb=500,
    supported_codecs=("h264", "h265"),
)

TIKTOK_PROFILE = PublishingProfile(
    platform=PlatformType.TIKTOK,
    max_duration_seconds=10 * 60,  # 10 minutes
    min_duration_seconds=3,
    supported_resolutions=("1080p", "720p", "480p"),
    supported_aspect_ratios=("9:16", "16:9", "1:1"),
    required_aspect_ratio="9:16",
    thumbnail_width=540,
    thumbnail_height=960,
    max_title_length=150,
    max_description_length=2200,
    max_hashtags=30,
    max_tags=10,
    supports_scheduling=True,
    supports_premiere=False,
    supports_playlist=False,
    supports_monetization=True,
    supports_categories=False,
    allows_auto_captions=True,
    allows_auto_translation=False,
    recommended_bitrate_kbps=3000,
    recommended_framerate=30,
    max_file_size_mb=287,
    supported_codecs=("h264", "h265"),
)

INSTAGRAM_REEL_PROFILE = PublishingProfile(
    platform=PlatformType.INSTAGRAM_REEL,
    max_duration_seconds=90,
    min_duration_seconds=3,
    supported_resolutions=("1080p", "720p", "480p"),
    supported_aspect_ratios=("9:16", "1:1", "4:5"),
    required_aspect_ratio="9:16",
    thumbnail_width=1080,
    thumbnail_height=1350,
    max_title_length=2200,
    max_description_length=2200,
    max_hashtags=30,
    max_tags=20,
    supports_scheduling=True,
    supports_premiere=False,
    supports_playlist=False,
    supports_monetization=True,
    supports_categories=False,
    allows_auto_captions=True,
    allows_auto_translation=False,
    recommended_bitrate_kbps=8000,
    recommended_framerate=30,
    max_file_size_mb=100,
    supported_codecs=("h264", "h265"),
)

INSTAGRAM_FEED_PROFILE = PublishingProfile(
    platform=PlatformType.INSTAGRAM_FEED,
    max_duration_seconds=60 * 60,  # 1 hour
    min_duration_seconds=3,
    supported_resolutions=("1080p", "720p", "480p"),
    supported_aspect_ratios=("1:1", "4:5", "16:9"),
    required_aspect_ratio="1:1",
    thumbnail_width=1080,
    thumbnail_height=1080,
    max_title_length=2200,
    max_description_length=2200,
    max_hashtags=30,
    supports_scheduling=True,
    supports_premiere=False,
    supports_playlist=False,
    supports_monetization=False,
    supports_categories=False,
    allows_auto_captions=True,
    allows_auto_translation=False,
    recommended_bitrate_kbps=6000,
    recommended_framerate=30,
    max_file_size_mb=100,
    supported_codecs=("h264", "h265"),
)

LINKEDIN_PROFILE = PublishingProfile(
    platform=PlatformType.LINKEDIN,
    max_duration_seconds=10 * 60,  # 10 minutes
    min_duration_seconds=3,
    supported_resolutions=("1080p", "720p", "480p"),
    supported_aspect_ratios=("16:9", "1:1", "9:16"),
    thumbnail_width=1200,
    thumbnail_height=627,
    max_title_length=200,
    max_description_length=3000,
    max_hashtags=3,
    max_tags=50,
    supports_scheduling=True,
    supports_premiere=False,
    supports_playlist=False,
    supports_monetization=False,
    supports_categories=False,
    allows_auto_captions=True,
    allows_auto_translation=False,
    recommended_bitrate_kbps=5000,
    recommended_framerate=30,
    max_file_size_mb=200,
    supported_codecs=("h264",),
)

PODCAST_PROFILE = PublishingProfile(
    platform=PlatformType.PODCAST,
    max_duration_seconds=12 * 60 * 60,  # 12 hours
    min_duration_seconds=60,  # 1 minute
    supported_resolutions=("1080p", "720p"),  # Video podcasts
    supported_aspect_ratios=("16:9", "1:1"),
    thumbnail_width=1400,
    thumbnail_height=1400,
    max_title_length=200,
    max_description_length=4000,
    max_hashtags=0,
    max_tags=100,
    supports_scheduling=True,
    supports_premiere=False,
    supports_playlist=True,
    supports_monetization=True,
    supports_categories=True,
    supports_comments=True,
    allows_auto_captions=True,
    allows_auto_translation=True,
    recommended_bitrate_kbps=128,  # Audio bitrate
    recommended_framerate=30,
    max_file_size_mb=5000,
    supported_codecs=("aac", "mp3", "opus"),
)

CUSTOM_PROFILE = PublishingProfile(
    platform=PlatformType.CUSTOM,
    max_duration_seconds=24 * 60 * 60,  # 24 hours
    min_duration_seconds=1,
    supported_resolutions=("4320p", "2160p", "1440p", "1080p", "720p", "480p", "360p"),
    supported_aspect_ratios=("16:9", "9:16", "1:1", "4:5", "21:9"),
    thumbnail_width=1920,
    thumbnail_height=1080,
    max_title_length=500,
    max_description_length=10000,
    max_hashtags=100,
    max_tags=500,
    supports_scheduling=True,
    supports_premiere=True,
    supports_playlist=True,
    supports_monetization=True,
    supports_categories=True,
    custom_metadata_supported=True,
    allows_auto_captions=True,
    allows_auto_translation=True,
    recommended_bitrate_kbps=50000,
    recommended_framerate=120,
    max_file_size_mb=1000000,
    supported_codecs=("h264", "h265", "vp9", "av1", "prores"),
    supports_hdr=True,
    supports_spatial_audio=True,
)


def get_profile(platform: PlatformType) -> PublishingProfile:
    """Get profile for platform"""
    profiles = {
        PlatformType.YOUTUBE: YOUTUBE_PROFILE,
        PlatformType.YOUTUBE_SHORTS: YOUTUBE_SHORTS_PROFILE,
        PlatformType.TIKTOK: TIKTOK_PROFILE,
        PlatformType.INSTAGRAM_REEL: INSTAGRAM_REEL_PROFILE,
        PlatformType.INSTAGRAM_FEED: INSTAGRAM_FEED_PROFILE,
        PlatformType.LINKEDIN: LINKEDIN_PROFILE,
        PlatformType.PODCAST: PODCAST_PROFILE,
        PlatformType.CUSTOM: CUSTOM_PROFILE,
    }
    return profiles.get(platform, CUSTOM_PROFILE)


def get_all_profiles() -> dict[str, PublishingProfile]:
    """Get all built-in profiles"""
    return {
        "youtube": YOUTUBE_PROFILE,
        "youtube_shorts": YOUTUBE_SHORTS_PROFILE,
        "tiktok": TIKTOK_PROFILE,
        "instagram_reel": INSTAGRAM_REEL_PROFILE,
        "instagram_feed": INSTAGRAM_FEED_PROFILE,
        "linkedin": LINKEDIN_PROFILE,
        "podcast": PODCAST_PROFILE,
        "custom": CUSTOM_PROFILE,
    }
