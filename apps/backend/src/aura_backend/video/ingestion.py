"""Video ingestion and analysis pipeline.

Complete end-to-end flow with M8 Task Orchestration:
1. Create AnalysisSession (root aggregate)
2. Import video file
3. Plan analysis workflow (Task Graph)
4. Submit to M8 Task Orchestration Runtime
5. Collect all observations (append-only)
6. Build knowledge graph via registered agent
7. Persist complete session to Memory Runtime

Architectural Principles:
- Analysis work orchestrated via M8 Task Graph
- Providers remain stateless (input → output only)
- All outputs converted to immutable Observations
- Only pipeline persists to Memory Runtime
- AnalysisSession is the root aggregate
- No direct agent invocation (via M8 ExecutionEngine)
"""

from datetime import datetime
from typing import Optional, Tuple, List, Dict, Any

from aura_backend.video.models import (
    AnalysisSession,
    Observation,
    Timeline,
    TimelineEvent,
    TimelineEventType,
    Video,
    KnowledgeNode,
)
from aura_backend.video.providers import VideoProvider, ProviderRegistry
from aura_backend.video.analysis_planner import (
    AnalysisPlanner,
    TaskGraph,
    Task,
)


class VideoIngestionPipeline:
    """Complete video ingestion and analysis orchestrator.

    Uses M8 Task Orchestration Runtime for all analysis work:
    - Manages AnalysisSession as root aggregate
    - Coordinates video import and metadata extraction
    - Creates TaskGraph via AnalysisPlanner
    - Submits graph to M8 ExecutionEngine
    - Collects results and converts to immutable Observations
    - Builds knowledge graph via registered agent
    - Persists complete results to Memory Runtime (sole entry point)
    """

    def __init__(
        self,
        provider_registry: ProviderRegistry,
        execution_engine=None,  # M8 ExecutionEngine
        analysis_planner: Optional[AnalysisPlanner] = None,
        memory_manager=None,  # M7 MemoryManager
    ):
        self.registry = provider_registry
        self.execution_engine = execution_engine
        self.planner = analysis_planner or AnalysisPlanner(execution_engine)
        self.memory = memory_manager

    async def create_analysis_session(
        self,
        video_id: str,
        session_type: str = "initial",
    ) -> AnalysisSession:
        """Create new analysis session.

        Args:
            video_id: ID of video being analyzed
            session_type: Type of analysis (initial, refinement, etc.)

        Returns:
            AnalysisSession in pending state
        """
        session = AnalysisSession(
            video_id=video_id,
            session_type=session_type,
            status="pending",
            started_at=datetime.utcnow(),
        )
        return session

    async def ingest_video(
        self,
        file_path: str,
        video_provider_name: str = "ffmpeg",
        session: Optional[AnalysisSession] = None,
    ) -> Tuple[Video, Timeline, AnalysisSession]:
        """Import video file and extract metadata.

        Args:
            file_path: Path to video file
            video_provider_name: Name of registered video provider
            session: AnalysisSession to associate with (created if None)

        Returns:
            Tuple of (Video, Timeline, AnalysisSession)
        """
        # Create session if needed
        if session is None:
            session = await self.create_analysis_session(video_id="")

        # Mark in progress
        session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status="in_progress",
            started_at=session.started_at,
        )

        # Get provider
        provider = self.registry.get_video_provider(video_provider_name)
        if not provider:
            raise ValueError(f"Provider '{video_provider_name}' not registered")

        # Check support
        if not await provider.is_supported(file_path):
            raise ValueError(
                f"Provider '{video_provider_name}' does not support '{file_path}'"
            )

        # Extract metadata (stateless provider)
        metadata = await provider.extract_metadata(file_path)

        # Create immutable Video
        video = Video(
            file_path=file_path,
            metadata=metadata,
            imported_at=datetime.utcnow(),
        )

        # Update session with video_id
        session = AnalysisSession(
            id=session.id,
            video_id=video.id,
            session_type=session.session_type,
            status=session.status,
            started_at=session.started_at,
        )

        # Create Timeline with import event
        import_event = TimelineEvent(
            video_id=video.id,
            event_type=TimelineEventType.VIDEO_IMPORTED,
            timestamp=datetime.utcnow(),
            data={
                "file_path": file_path,
                "file_size_bytes": metadata.file_size_bytes,
                "duration_seconds": metadata.duration_seconds,
                "fps": metadata.fps,
                "resolution": f"{metadata.width}x{metadata.height}",
            },
            source="VideoIngestionPipeline",
        )

        timeline = Timeline(
            video_id=video.id,
            events=[import_event],
            observations=[],
            created_at=datetime.utcnow(),
        )

        # Associate timeline with session
        session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status=session.status,
            started_at=session.started_at,
            timeline_id=timeline.id,
        )

        return video, timeline, session

    async def extract_and_analyze(
        self,
        video: Video,
        timeline: Timeline,
        session: AnalysisSession,
    ) -> Tuple[Timeline, AnalysisSession]:
        """Extract frames/audio and run analysis via M8 Task Orchestration.

        IMPLEMENTATION: Uses AnalysisPlanner to create Task Graph, submits to M8
        ExecutionEngine for distributed execution. All results collected and
        converted to immutable Observation objects (append-only).

        Args:
            video: Video object
            timeline: Current timeline
            session: Current session

        Returns:
            Tuple of (updated_timeline, updated_session)
        """
        observations: List[Observation] = []  # Append-only collection
        events: List[TimelineEvent] = list(timeline.events)

        if not video.metadata:
            return timeline, session

        # Plan analysis workflow
        task_graph = await self.planner.plan_analysis(
            session_id=session.id,
            video_id=video.id,
            video_metadata=video.metadata.to_dict(),
            has_frames=True,
            has_audio=True,
        )

        # Validate graph
        errors = self.planner.validate_graph(task_graph)
        if errors:
            raise ValueError(f"Invalid task graph: {errors}")

        # Submit to M8 ExecutionEngine
        if not self.execution_engine:
            raise ValueError("M8 ExecutionEngine not configured")

        # Execute graph (M8 handles scheduling, dispatching, capability resolution)
        completed_graph = await self.execution_engine.execute_graph(
            task_graph.to_dict(),
            context={"session_id": session.id, "video_id": video.id},
        )

        # Collect and convert results to Observations (append-only)
        observations.extend(
            await self._collect_observations_from_graph(completed_graph, video.id)
        )

        # Add timeline events for completed stages
        if observations:
            events.append(TimelineEvent(
                video_id=video.id,
                event_type=TimelineEventType.OBSERVATION_CREATED,
                timestamp=datetime.utcnow(),
                data={"observation_count": len(observations)},
                source="M8ExecutionEngine",
            ))

        # Update timeline (immutable - create new with observations appended)
        updated_timeline = Timeline(
            id=timeline.id,
            video_id=timeline.video_id,
            events=events,
            observations=list(timeline.observations) + observations,  # Append-only
            created_at=timeline.created_at,
            updated_at=datetime.utcnow(),
        )

        # Update session with observation IDs
        updated_session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status=session.status,
            started_at=session.started_at,
            timeline_id=session.timeline_id,
            observation_ids=session.observation_ids + [obs.id for obs in observations],
        )

        return updated_timeline, updated_session

    async def build_knowledge_graph(
        self,
        video_id: str,
        observations: List[Observation],
        session: AnalysisSession,
    ) -> Tuple[List[KnowledgeNode], AnalysisSession]:
        """Build knowledge graph from observations via registered agent.

        IMPLEMENTATION: If M8 is available, submits KnowledgeBuilder as registered
        agent task. Otherwise, executes locally for backward compatibility.

        Args:
            video_id: Video being analyzed
            observations: All observations from analysis
            session: Current session

        Returns:
            Tuple of (knowledge_nodes, updated_session)
        """
        knowledge_nodes: List[KnowledgeNode] = []

        if self.execution_engine and observations:
            # Submit KnowledgeBuilder as M8 agent task
            knowledge_task = Task(
                id=f"knowledge_build_{video_id}_{datetime.utcnow().timestamp()}",
                task_type="knowledge_building",  # Will be resolved via CapabilityResolver
                agent_name="knowledge_building_agent",
                session_id=session.id,
                video_id=video_id,
                input_data={
                    "observations": [obs.to_dict() for obs in observations],
                },
                depends_on=[],
            )

            # Execute single task via M8
            result = await self.execution_engine.execute_task(knowledge_task.to_dict())
            if result and "output_data" in result:
                node_dicts = result["output_data"].get("knowledge_nodes", [])
                knowledge_nodes = [
                    KnowledgeNode(**node_dict) for node_dict in node_dicts
                ]
        else:
            # Fallback: Local execution for backward compatibility
            from aura_backend.video.knowledge_builder import KnowledgeBuilder
            builder = KnowledgeBuilder()
            knowledge_nodes = await builder.build_knowledge_graph(video_id, observations)

        # Update session with knowledge node IDs
        updated_session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status=session.status,
            started_at=session.started_at,
            timeline_id=session.timeline_id,
            observation_ids=session.observation_ids,
            knowledge_node_ids=[node.id for node in knowledge_nodes],
        )

        return knowledge_nodes, updated_session

    async def complete_session(
        self,
        session: AnalysisSession,
        timeline: Timeline,
    ) -> AnalysisSession:
        """Mark session complete with metrics.

        Args:
            session: Current session
            timeline: Completed timeline with all results

        Returns:
            Completed AnalysisSession
        """
        metrics = {
            "observation_count": len(timeline.observations),
            "event_count": len(timeline.events),
            "duration_seconds": session.duration_seconds,
            "observation_breakdown": self._breakdown_observations(
                timeline.observations
            ),
        }

        return AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status="completed",
            started_at=session.started_at,
            completed_at=datetime.utcnow(),
            timeline_id=session.timeline_id,
            observation_ids=session.observation_ids,
            knowledge_node_ids=session.knowledge_node_ids,
            metrics=metrics,
        )

    async def persist_session_to_memory(
        self,
        session: AnalysisSession,
        video: Video,
        timeline: Timeline,
        knowledge_nodes: Optional[List[KnowledgeNode]] = None,
    ) -> None:
        """Persist complete analysis session to Memory Runtime.

        IMPORTANT: This is the ONLY entry point for persisting results.
        Providers, agents, and knowledge builder NEVER access Memory Runtime directly.

        Args:
            session: Completed AnalysisSession
            video: Video object
            timeline: Timeline with all events and observations
            knowledge_nodes: Optional knowledge graph nodes
        """
        if not self.memory:
            return

        # Store video
        await self.memory.store(video.to_dict(), memory_type="episodic")

        # Store analysis session
        await self.memory.store(session.to_dict(), memory_type="episodic")

        # Store timeline
        await self.memory.store(timeline.to_dict(), memory_type="episodic")

        # Store observations
        for observation in timeline.observations:
            await self.memory.store(observation.to_dict(), memory_type="episodic")

        # Store events
        for event in timeline.events:
            await self.memory.store(event.to_dict(), memory_type="episodic")

        # Store knowledge nodes
        if knowledge_nodes:
            for node in knowledge_nodes:
                await self.memory.store(node.to_dict(), memory_type="semantic")

    # Private helper methods

    async def _collect_observations_from_graph(
        self,
        completed_graph: Dict[str, Any],
        video_id: str,
    ) -> List[Observation]:
        """Extract and convert observations from completed task graph.

        Collects all observations from analysis agent task outputs
        and converts them to immutable Observation objects.

        Args:
            completed_graph: Task graph results from M8
            video_id: Video being analyzed

        Returns:
            List of immutable Observation objects (append-only)
        """
        observations: List[Observation] = []

        # Task graph structure: tasks dict with task_id → task_data
        tasks = completed_graph.get("tasks", {})

        for task_id, task_data in tasks.items():
            if task_data.get("status") != "completed":
                continue

            output = task_data.get("output_data", {})
            if not output:
                continue

            # Extract observations from task output
            agent_name = task_data.get("agent_name", "")
            task_type = task_data.get("task_type", "")

            # Each agent task produces observations in output_data["observations"]
            task_observations = output.get("observations", [])
            for obs_dict in task_observations:
                # Reconstruct immutable Observation
                obs = Observation(
                    video_id=video_id,
                    observation_type=obs_dict.get("observation_type"),
                    source_agent=agent_name,
                    start_timestamp=obs_dict.get("start_timestamp", 0.0),
                    end_timestamp=obs_dict.get("end_timestamp", 0.0),
                    confidence=obs_dict.get("confidence", 1.0),
                    payload=obs_dict.get("payload", {}),
                    metadata=obs_dict.get("metadata", {}),
                )
                observations.append(obs)

        return observations

    def _breakdown_observations(
        self,
        observations: List[Observation],
    ) -> Dict[str, int]:
        """Count observations by type."""
        breakdown: Dict[str, int] = {}
        for obs in observations:
            obs_type = obs.observation_type.value
            breakdown[obs_type] = breakdown.get(obs_type, 0) + 1
        return breakdown

    # Backward compatibility methods

    async def add_observations_to_session(
        self,
        session: AnalysisSession,
        observations: List[Observation],
        timeline: Timeline,
    ) -> Tuple[AnalysisSession, Timeline]:
        """Add observations to session and timeline (Phase 1 compatibility)."""
        updated_timeline = Timeline(
            id=timeline.id,
            video_id=timeline.video_id,
            events=list(timeline.events),
            observations=list(timeline.observations) + observations,
            created_at=timeline.created_at,
            updated_at=datetime.utcnow(),
        )

        observation_ids = session.observation_ids + [obs.id for obs in observations]
        updated_session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status=session.status,
            started_at=session.started_at,
            completed_at=session.completed_at,
            timeline_id=session.timeline_id,
            observation_ids=observation_ids,
            knowledge_node_ids=session.knowledge_node_ids,
            metrics=session.metrics,
            metadata=session.metadata,
        )

        return updated_session, updated_timeline
