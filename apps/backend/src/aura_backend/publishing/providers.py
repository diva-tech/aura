"""M13 Phase 2: Publishing Providers — Abstract Interface.

Provider abstraction for platform-agnostic publishing.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass

from .context import PublishCapability, PublishingContext
from .models import PublishingResult


@dataclass(frozen=True)
class UploadResponse:
    """Immutable upload response"""

    is_success: bool = False
    platform_video_id: str = ""
    platform_url: str = ""
    platform_thumbnail_url: str = ""
    error_code: str = ""
    error_message: str = ""
    warning_messages: tuple[str, ...] = ()
    metadata_synced: bool = False
    thumbnail_uploaded: bool = False


class PublishingProvider(ABC):
    """Abstract publishing provider interface"""

    @property
    @abstractmethod
    def provider_name(self) -> str:
        """Provider name"""

    @property
    @abstractmethod
    def capabilities(self) -> PublishCapability:
        """Provider capabilities"""

    @abstractmethod
    async def is_available(self) -> bool:
        """Check if provider is available"""

    @abstractmethod
    async def authenticate(self, context: PublishingContext) -> bool:
        """Authenticate with platform account"""

    @abstractmethod
    async def validate_credentials(self, context: PublishingContext) -> bool:
        """Validate platform credentials"""

    @abstractmethod
    async def upload_video(self, context: PublishingContext) -> UploadResponse:
        """Upload video to platform"""

    @abstractmethod
    async def upload_thumbnail(self, context: PublishingContext) -> bool:
        """Upload thumbnail to platform"""

    @abstractmethod
    async def set_metadata(self, context: PublishingContext) -> bool:
        """Set video metadata (title, description, tags)"""

    @abstractmethod
    async def set_privacy(self, context: PublishingContext, privacy_level: str) -> bool:
        """Set video privacy level"""

    @abstractmethod
    async def schedule_publish(self, context: PublishingContext) -> bool:
        """Schedule video for later publishing"""

    @abstractmethod
    async def publish_draft(self, context: PublishingContext, video_id: str) -> bool:
        """Publish a draft video"""

    @abstractmethod
    async def get_video_status(self, context: PublishingContext, video_id: str) -> dict:
        """Get video processing status"""

    @abstractmethod
    async def add_to_playlist(
        self, context: PublishingContext, video_id: str, playlist_id: str
    ) -> bool:
        """Add video to playlist"""

    @abstractmethod
    async def generate_captions(self, context: PublishingContext, video_id: str) -> bool:
        """Generate auto captions"""

    @abstractmethod
    async def publish(self, context: PublishingContext) -> PublishingResult:
        """Execute full publishing workflow"""


class ProviderRegistry:
    """Registry for publishing providers"""

    def __init__(self):
        self._providers: dict[str, PublishingProvider] = {}

    def register(self, name: str, provider: PublishingProvider) -> None:
        """Register a provider"""
        self._providers[name] = provider

    def get(self, name: str) -> PublishingProvider | None:
        """Get provider by name"""
        return self._providers.get(name)

    def get_by_platform(self, platform_name: str) -> PublishingProvider | None:
        """Get provider by platform name"""
        for provider in self._providers.values():
            if provider.capabilities.platform.value == platform_name:
                return provider
        return None

    def list_providers(self) -> dict[str, PublishingProvider]:
        """List all registered providers"""
        return dict(self._providers)

    def list_available_providers(self) -> dict[str, PublishingProvider]:
        """List available providers (not async in registry)"""
        return dict(self._providers)

    def get_provider_for_platform(self, platform: str) -> PublishingProvider | None:
        """Get provider for specific platform"""
        return self.get_by_platform(platform)
