"""Context compression strategies."""

from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional

from aura_backend.memory.knowledge.objects import MemoryItem


class CompressionStrategy(ABC):
    """Abstract base for compression strategies"""

    @property
    @abstractmethod
    def name(self) -> str:
        """Strategy name"""
        pass

    @abstractmethod
    async def compress(
        self, items: List[MemoryItem], target_tokens: int
    ) -> tuple[List[MemoryItem], float]:
        """Compress items to fit token budget.

        Returns: (compressed_items, compression_ratio)
        """
        pass


class TokenBudgetStrategy(CompressionStrategy):
    """Compress to fit within token budget"""

    @property
    def name(self) -> str:
        return "token_budget"

    async def compress(
        self, items: List[MemoryItem], target_tokens: int
    ) -> tuple[List[MemoryItem], float]:
        """Keep items until token budget exhausted"""
        # Stub: future will estimate tokens and select items
        return items, 1.0


class RankingStrategy(CompressionStrategy):
    """Rank items by importance and recency"""

    @property
    def name(self) -> str:
        return "ranking"

    async def compress(
        self, items: List[MemoryItem], target_tokens: int
    ) -> tuple[List[MemoryItem], float]:
        """Rank items by importance/recency and keep top"""
        # Stub: future will rank and select
        return items, 1.0


class SummarizationStrategy(CompressionStrategy):
    """Summarize groups of items"""

    @property
    def name(self) -> str:
        return "summarization"

    async def compress(
        self, items: List[MemoryItem], target_tokens: int
    ) -> tuple[List[MemoryItem], float]:
        """Group and summarize items"""
        # Stub: future will use LLM to summarize
        return items, 1.0


class DeduplicationStrategy(CompressionStrategy):
    """Remove duplicate information"""

    @property
    def name(self) -> str:
        return "deduplication"

    async def compress(
        self, items: List[MemoryItem], target_tokens: int
    ) -> tuple[List[MemoryItem], float]:
        """Remove duplicates"""
        # Stub: future will detect and remove duplicates
        return items, 1.0


class WindowingStrategy(CompressionStrategy):
    """Keep sliding window of recent items"""

    def __init__(self, window_size: int = 10):
        self.window_size = window_size

    @property
    def name(self) -> str:
        return "windowing"

    async def compress(
        self, items: List[MemoryItem], target_tokens: int
    ) -> tuple[List[MemoryItem], float]:
        """Keep recent items within window"""
        # Sort by created_at, take most recent window_size items
        sorted_items = sorted(items, key=lambda x: x.metadata.created_at, reverse=True)
        compressed = sorted_items[: self.window_size]
        compression_ratio = len(compressed) / len(items) if items else 1.0
        return compressed, compression_ratio


class ContextBuilder:
    """Build optimized LLM context from memory"""

    def __init__(self, strategy: Optional[CompressionStrategy] = None):
        self.strategy = strategy or WindowingStrategy(window_size=10)

    async def build_context(
        self,
        goal: str,
        memories: List[MemoryItem],
        max_tokens: int = 4000,
    ) -> Dict[str, Any]:
        """Build optimized context for LLM

        Returns: {
            "context": "formatted context string",
            "memory_items": [list of included MemoryItem],
            "compression_ratio": float,
            "token_estimate": int,
        }
        """
        if not memories:
            return {
                "context": f"Goal: {goal}\n\nNo prior memory available.",
                "memory_items": [],
                "compression_ratio": 1.0,
                "token_estimate": len(goal.split()),
            }

        # Compress memories
        compressed, ratio = await self.strategy.compress(memories, max_tokens)

        # Build context string
        context_parts = [f"Goal: {goal}\n"]
        context_parts.append("Recent Memory:\n")

        for item in compressed:
            if item.summary:
                context_parts.append(f"- {item.summary}")
            else:
                context_parts.append(f"- {item.content[:200]}")

        context_string = "\n".join(context_parts)

        return {
            "context": context_string,
            "memory_items": compressed,
            "compression_ratio": ratio,
            "token_estimate": len(context_string.split()),
        }
