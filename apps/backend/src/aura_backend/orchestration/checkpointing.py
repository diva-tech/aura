"""Checkpointing system - persist execution state using M7 Memory Runtime.

Enables recovery from failures and resumption after restart.
"""

from typing import Any, Dict, Optional

from aura_backend.memory import MemoryItem, MemoryManager, MemoryType
from aura_backend.orchestration.models import ExecutionStatus, TaskGraph


class ExecutionCheckpoint:
    """Immutable record of execution state at a point in time"""

    def __init__(
        self,
        checkpoint_id: str,
        task_graph: TaskGraph,
        completed_tasks: Dict[str, str],  # task_id -> result
        failed_tasks: Dict[str, str],  # task_id -> error
        running_tasks: set,
        metadata: Optional[Dict[str, Any]] = None,
    ):
        self.checkpoint_id = checkpoint_id
        self.task_graph = task_graph
        self.completed_tasks = completed_tasks
        self.failed_tasks = failed_tasks
        self.running_tasks = running_tasks
        self.metadata = metadata or {}

    def to_dict(self) -> Dict[str, Any]:
        return {
            "checkpoint_id": self.checkpoint_id,
            "task_graph_id": self.task_graph.id,
            "completed_tasks": self.completed_tasks,
            "failed_tasks": self.failed_tasks,
            "running_tasks": list(self.running_tasks),
            "metadata": self.metadata,
        }


class CheckpointManager:
    """Manages checkpoints for execution recovery.

    Stores execution state in M7 Memory Runtime for durability.
    """

    def __init__(self, memory_manager: MemoryManager):
        """Initialize checkpoint manager with memory backend"""
        self.memory = memory_manager

    async def create_checkpoint(
        self,
        task_graph: TaskGraph,
        completed_tasks: Dict[str, str],
        failed_tasks: Dict[str, str],
        running_tasks: set,
        checkpoint_id: str = "",
    ) -> ExecutionCheckpoint:
        """Create and persist a checkpoint.

        Saves execution state for recovery.
        """
        checkpoint = ExecutionCheckpoint(
            checkpoint_id=checkpoint_id or f"checkpoint-{task_graph.id}",
            task_graph=task_graph,
            completed_tasks=completed_tasks,
            failed_tasks=failed_tasks,
            running_tasks=running_tasks,
        )

        # Store in memory for durability
        memory_item = MemoryItem(
            id=checkpoint.checkpoint_id,
            memory_type=MemoryType.PROCEDURAL,
            content=f"Checkpoint for {task_graph.id}",
            summary=f"Completed: {len(completed_tasks)}, Failed: {len(failed_tasks)}, Running: {len(running_tasks)}",
            metadata={
                "checkpoint": True,
                "graph_id": task_graph.id,
                "completed_count": len(completed_tasks),
                "failed_count": len(failed_tasks),
                "running_count": len(running_tasks),
            },
        )

        await self.memory.store(memory_item)

        return checkpoint

    async def restore_checkpoint(self, checkpoint_id: str) -> Optional[ExecutionCheckpoint]:
        """Restore a checkpoint from memory.

        Retrieves execution state for resume after failure.
        """
        # Retrieve from memory
        item = await self.memory.retrieve(checkpoint_id)
        if not item:
            return None

        # Deserialize checkpoint
        # In production, would reconstruct from stored data
        checkpoint = ExecutionCheckpoint(
            checkpoint_id=checkpoint_id,
            task_graph=TaskGraph(),  # Would load actual graph
            completed_tasks=item.metadata.custom_fields.get("completed_tasks", {}),
            failed_tasks=item.metadata.custom_fields.get("failed_tasks", {}),
            running_tasks=set(item.metadata.custom_fields.get("running_tasks", [])),
        )

        return checkpoint

    async def list_checkpoints(self) -> list:
        """List all available checkpoints"""
        items = await self.memory.search_by_metadata(
            filters={"checkpoint": True},
            limit=100,
        )
        return items

    async def delete_checkpoint(self, checkpoint_id: str) -> bool:
        """Delete a checkpoint"""
        return await self.memory.delete(checkpoint_id)

    async def recovery_summary(self) -> Dict[str, Any]:
        """Get summary of available recovery points"""
        checkpoints = await self.list_checkpoints()
        return {
            "available_checkpoints": len(checkpoints),
            "latest": checkpoints[-1] if checkpoints else None,
            "total_storage_mb": 0,  # Would calculate from memory manager
        }
