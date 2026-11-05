"""
Provider abstractions.

Interfaces for various AI/ML providers.
Provider-agnostic - no implementation included.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, List, Optional


@dataclass
class CompletionRequest:
    """LLM completion request"""

    prompt: str
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    top_p: float = 1.0
    top_k: Optional[int] = None
    stop_sequences: Optional[List[str]] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


@dataclass
class CompletionResponse:
    """LLM completion response"""

    text: str
    model: str
    stop_reason: str
    tokens_used: int
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class LLMProvider(ABC):
    """
    LLM provider interface.

    Abstracts different LLM providers.
    """

    @abstractmethod
    async def complete(self, request: CompletionRequest) -> CompletionResponse:
        """Generate completion"""
        pass

    @abstractmethod
    async def stream_complete(self, request: CompletionRequest):
        """Stream completion tokens"""
        pass

    @abstractmethod
    async def list_models(self) -> List[str]:
        """List available models"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get provider health"""
        pass


class VisionProvider(ABC):
    """
    Vision/image analysis provider interface.
    """

    @abstractmethod
    async def analyze_image(self, image_data: bytes, prompt: str) -> Dict[str, Any]:
        """Analyze an image"""
        pass

    @abstractmethod
    async def extract_text(self, image_data: bytes) -> str:
        """Extract text from image"""
        pass

    @abstractmethod
    async def detect_objects(self, image_data: bytes) -> List[Dict[str, Any]]:
        """Detect objects in image"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get provider health"""
        pass


class EmbeddingProvider(ABC):
    """
    Embedding provider interface.

    Creates vector embeddings for text.
    """

    @abstractmethod
    async def embed_text(self, text: str) -> List[float]:
        """Create embedding for text"""
        pass

    @abstractmethod
    async def embed_batch(self, texts: List[str]) -> List[List[float]]:
        """Create embeddings for multiple texts"""
        pass

    @abstractmethod
    async def similarity(self, text1: str, text2: str) -> float:
        """Calculate text similarity"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get provider health"""
        pass


class SpeechProvider(ABC):
    """
    Speech provider interface.

    Text-to-speech and speech-to-text.
    """

    @abstractmethod
    async def text_to_speech(self, text: str, voice: str = "default") -> bytes:
        """Convert text to speech"""
        pass

    @abstractmethod
    async def speech_to_text(self, audio_data: bytes) -> str:
        """Transcribe speech to text"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get provider health"""
        pass


class ImageGenerationProvider(ABC):
    """
    Image generation provider interface.
    """

    @abstractmethod
    async def generate_image(self, prompt: str, style: str = "default") -> bytes:
        """Generate image from prompt"""
        pass

    @abstractmethod
    async def edit_image(self, image_data: bytes, prompt: str) -> bytes:
        """Edit an existing image"""
        pass

    @abstractmethod
    async def health(self) -> Dict[str, Any]:
        """Get provider health"""
        pass


class PromptRenderer(ABC):
    """
    Prompt rendering interface.

    Converts prompt templates into final prompts.
    """

    @abstractmethod
    async def render(self, template: str, variables: Dict[str, Any]) -> str:
        """Render a prompt template"""
        pass

    @abstractmethod
    async def render_with_context(
        self,
        template: str,
        variables: Dict[str, Any],
        context: Dict[str, Any]
    ) -> str:
        """Render with additional context"""
        pass

    @abstractmethod
    async def validate_template(self, template: str) -> Dict[str, Any]:
        """Validate a prompt template"""
        pass
