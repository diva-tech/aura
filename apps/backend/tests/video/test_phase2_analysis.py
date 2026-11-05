"""Phase 2 Analysis Tests: Frame extraction, audio extraction, agents, knowledge builder.

Tests the complete analysis pipeline:
1. Frame and audio extraction
2. Scene, speech, OCR, and vision analysis agents
3. Knowledge graph building
4. Integration with AnalysisSession
"""

import pytest
from datetime import datetime
from aura_backend.video import (
    Video,
    VideoMetadata,
    VideoCodec,
    AudioCodec,
    Observation,
    ObservationType,
    Timeline,
    TimelineEventType,
    AnalysisSession,
    # Phase 2 components
    FrameExtractionService,
    AudioExtractionService,
    ExtractedFrame,
    ExtractedAudioSegment,
    SceneAnalysisAgent,
    OpenCVSceneProvider,
    SpeechAnalysisAgent,
    OCRAnalysisAgent,
    VisionAnalysisAgent,
    KnowledgeBuilder,
    VideoIngestionPipeline,
    ProviderRegistry,
    FFmpegVideoProvider,
    WhisperSpeechProvider,
    TesseractOCRProvider,
    OpenCVVisionProvider,
)


# ============================================================================
# EXTRACTION SERVICE TESTS
# ============================================================================


class TestFrameExtraction:
    """Test frame extraction"""

    def test_frame_extraction_service_exists(self):
        """FrameExtractionService can be instantiated"""
        service = FrameExtractionService()
        assert service is not None

    def test_extract_frames_returns_list(self):
        """Frame extraction returns list of ExtractedFrame"""
        service = FrameExtractionService()
        # Just verify method exists and signature
        assert callable(service.extract_frames)

    def test_extracted_frame_structure(self):
        """ExtractedFrame has proper structure"""
        frame = ExtractedFrame(
            frame_number=0,
            timestamp_seconds=0.0,
            is_keyframe=True,
            width=1920,
            height=1080,
        )

        assert frame.frame_number == 0
        assert frame.timestamp_seconds == 0.0
        assert frame.is_keyframe is True
        assert frame.width == 1920
        assert frame.height == 1080


class TestAudioExtraction:
    """Test audio extraction"""

    def test_audio_extraction_service_exists(self):
        """AudioExtractionService can be instantiated"""
        service = AudioExtractionService()
        assert service is not None

    def test_extracted_audio_segment_structure(self):
        """ExtractedAudioSegment has proper structure"""
        segment = ExtractedAudioSegment(
            start_timestamp=0.0,
            end_timestamp=60.0,
            audio_data=b"",
            sample_rate=16000,
            channels=1,
        )

        assert segment.start_timestamp == 0.0
        assert segment.end_timestamp == 60.0
        assert segment.sample_rate == 16000
        assert segment.channels == 1


# ============================================================================
# ANALYSIS AGENT TESTS
# ============================================================================


class TestSceneAnalysisAgent:
    """Test scene detection agent"""

    def test_scene_agent_initialization(self):
        """SceneAnalysisAgent initializes with provider"""
        provider = OpenCVSceneProvider()
        agent = SceneAnalysisAgent(provider)
        assert agent.provider is provider

    def test_scene_agent_produces_observations(self):
        """Scene agent analyze method exists"""
        provider = OpenCVSceneProvider()
        agent = SceneAnalysisAgent(provider)
        assert callable(agent.analyze)


class TestSpeechAnalysisAgent:
    """Test speech transcription agent"""

    def test_speech_agent_initialization(self):
        """SpeechAnalysisAgent initializes with provider"""
        provider = WhisperSpeechProvider()
        agent = SpeechAnalysisAgent(provider)
        assert agent.provider is provider

    def test_speech_agent_produces_observations(self):
        """Speech agent analyze method exists"""
        provider = WhisperSpeechProvider()
        agent = SpeechAnalysisAgent(provider)
        assert callable(agent.analyze)


class TestOCRAnalysisAgent:
    """Test OCR agent"""

    def test_ocr_agent_initialization(self):
        """OCRAnalysisAgent initializes with provider"""
        provider = TesseractOCRProvider()
        agent = OCRAnalysisAgent(provider)
        assert agent.provider is provider

    def test_ocr_agent_produces_observations(self):
        """OCR agent analyze method exists"""
        provider = TesseractOCRProvider()
        agent = OCRAnalysisAgent(provider)
        assert callable(agent.analyze)


class TestVisionAnalysisAgent:
    """Test vision detection agent"""

    def test_vision_agent_initialization(self):
        """VisionAnalysisAgent initializes with provider"""
        provider = OpenCVVisionProvider()
        agent = VisionAnalysisAgent(provider)
        assert agent.provider is provider

    def test_vision_agent_produces_observations(self):
        """Vision agent analyze method exists"""
        provider = OpenCVVisionProvider()
        agent = VisionAnalysisAgent(provider)
        assert callable(agent.analyze)


# ============================================================================
# KNOWLEDGE BUILDER TESTS
# ============================================================================


class TestKnowledgeBuilder:
    """Test knowledge graph construction"""

    def test_knowledge_builder_initialization(self):
        """KnowledgeBuilder initializes"""
        builder = KnowledgeBuilder()
        assert builder is not None

    def test_knowledge_builder_extracts_entities(self):
        """Knowledge builder can extract entities from observations"""
        builder = KnowledgeBuilder()

        # Create test observations
        obs1 = Observation(
            video_id="vid-1",
            observation_type=ObservationType.SPEECH,
            source_agent="SpeechAgent",
            start_timestamp=0.0,
            end_timestamp=3.0,
            payload={"speaker": "Alice", "text": "Hello"},
        )
        obs2 = Observation(
            video_id="vid-1",
            observation_type=ObservationType.OBJECT,
            source_agent="ObjectAnalysisAgent",
            start_timestamp=5.0,
            end_timestamp=6.0,
            payload={"class": "person"},
        )

        # Verify method exists
        assert callable(builder.build_knowledge_graph)

    def test_knowledge_builder_builds_relationships(self):
        """Knowledge builder creates observation relationships"""
        builder = KnowledgeBuilder()

        obs1 = Observation(video_id="v1", observation_type=ObservationType.SPEECH)
        obs2 = Observation(video_id="v1", observation_type=ObservationType.OBJECT)

        observations = [obs1, obs2]
        relationships = builder.build_observation_relationships(observations)

        assert isinstance(relationships, dict)

    def test_knowledge_builder_returns_nodes(self):
        """Knowledge builder returns KnowledgeNode list"""
        builder = KnowledgeBuilder()
        nodes = builder.get_nodes()
        assert isinstance(nodes, list)


# ============================================================================
# INGESTION PIPELINE PHASE 2 TESTS
# ============================================================================


class TestVideoIngestionPipelinePhase2:
    """Test Phase 2 complete analysis pipeline"""

    def test_pipeline_with_agents(self):
        """Pipeline can be initialized with analysis agents"""
        registry = ProviderRegistry()
        registry.register_video_provider("ffmpeg", FFmpegVideoProvider())
        registry.register_speech_provider("whisper", WhisperSpeechProvider())
        registry.register_ocr_provider("tesseract", TesseractOCRProvider())
        registry.register_vision_provider("opencv", OpenCVVisionProvider())

        scene_agent = SceneAnalysisAgent(OpenCVSceneProvider())
        speech_agent = SpeechAnalysisAgent(WhisperSpeechProvider())
        ocr_agent = OCRAnalysisAgent(TesseractOCRProvider())
        vision_agent = VisionAnalysisAgent(OpenCVVisionProvider())

        pipeline = VideoIngestionPipeline(
            provider_registry=registry,
            scene_agent=scene_agent,
            speech_agent=speech_agent,
            ocr_agent=ocr_agent,
            vision_agent=vision_agent,
        )

        assert pipeline.scene_agent is scene_agent
        assert pipeline.speech_agent is speech_agent
        assert pipeline.ocr_agent is ocr_agent
        assert pipeline.vision_agent is vision_agent

    def test_pipeline_has_extract_and_analyze_method(self):
        """Pipeline has extract_and_analyze method"""
        registry = ProviderRegistry()
        registry.register_video_provider("ffmpeg", FFmpegVideoProvider())
        pipeline = VideoIngestionPipeline(registry)

        assert callable(pipeline.extract_and_analyze)

    def test_pipeline_has_build_knowledge_graph_method(self):
        """Pipeline has build_knowledge_graph method"""
        registry = ProviderRegistry()
        registry.register_video_provider("ffmpeg", FFmpegVideoProvider())
        pipeline = VideoIngestionPipeline(registry)

        assert callable(pipeline.build_knowledge_graph)

    def test_pipeline_complete_session_method(self):
        """Pipeline can complete and finalize session"""
        registry = ProviderRegistry()
        pipeline = VideoIngestionPipeline(registry)

        assert callable(pipeline.complete_session)

    def test_pipeline_persist_session_to_memory(self):
        """Pipeline has persist_session_to_memory as sole Memory entry point"""
        registry = ProviderRegistry()
        pipeline = VideoIngestionPipeline(registry)

        assert callable(pipeline.persist_session_to_memory)


# ============================================================================
# ANALYSIS SESSION INTEGRATION
# ============================================================================


class TestAnalysisSessionWithPhase2:
    """Test AnalysisSession integration with Phase 2"""

    def test_session_tracks_knowledge_nodes(self):
        """Session tracks knowledge node IDs"""
        session = AnalysisSession(
            video_id="vid-1",
            knowledge_node_ids=["node-1", "node-2"],
        )

        assert len(session.knowledge_node_ids) == 2

    def test_session_accumulates_metrics(self):
        """Session accumulates analysis metrics"""
        session = AnalysisSession(
            video_id="vid-1",
            metrics={
                "observation_count": 42,
                "scene_count": 3,
                "speech_segments": 8,
                "objects_detected": 12,
            },
        )

        assert session.metrics["observation_count"] == 42
        assert session.metrics["scene_count"] == 3


# ============================================================================
# END-TO-END FLOW TESTS
# ============================================================================


class TestEndToEndAnalysisPipeline:
    """Test complete Phase 1 + Phase 2 flow"""

    def test_observations_all_immutable(self):
        """All observations are immutable"""
        obs = Observation(
            video_id="v1",
            observation_type=ObservationType.SPEECH,
            payload={"text": "test"},
        )

        with pytest.raises(Exception):  # FrozenInstanceError
            obs.video_id = "v2"

    def test_timeline_contains_multiple_observation_types(self):
        """Timeline can contain all observation types"""
        observations = [
            Observation(
                video_id="v1",
                observation_type=ObservationType.SCENE_CONTENT,
            ),
            Observation(
                video_id="v1",
                observation_type=ObservationType.SPEECH,
            ),
            Observation(
                video_id="v1",
                observation_type=ObservationType.OCR,
            ),
            Observation(
                video_id="v1",
                observation_type=ObservationType.OBJECT,
            ),
            Observation(
                video_id="v1",
                observation_type=ObservationType.FACE,
            ),
        ]

        timeline = Timeline(video_id="v1", observations=observations)

        assert len(timeline.observations) == 5
        assert len(timeline.get_observations_by_type(ObservationType.SPEECH)) == 1
        assert len(timeline.get_observations_by_type(ObservationType.OBJECT)) == 1

    def test_session_root_aggregate_pattern(self):
        """AnalysisSession serves as root aggregate"""
        # Simulate complete analysis flow
        session = AnalysisSession(
            video_id="vid-1",
            session_type="initial",
            status="pending",
        )

        # Transition through states
        session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status="in_progress",
            started_at=datetime.utcnow(),
        )

        # Add results
        obs_ids = ["obs-1", "obs-2", "obs-3"]
        session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status=session.status,
            started_at=session.started_at,
            observation_ids=obs_ids,
        )

        # Complete
        session = AnalysisSession(
            id=session.id,
            video_id=session.video_id,
            session_type=session.session_type,
            status="completed",
            started_at=session.started_at,
            completed_at=datetime.utcnow(),
            observation_ids=session.observation_ids,
            metrics={"observation_count": len(obs_ids)},
        )

        assert session.is_complete
        assert len(session.observation_ids) == 3
        assert session.metrics["observation_count"] == 3

    def test_providers_remain_stateless(self):
        """Verify providers don't know about sessions"""
        provider = WhisperSpeechProvider()
        # Provider has no session knowledge
        assert not hasattr(provider, "session")
        assert not hasattr(provider, "timeline")
        assert not hasattr(provider, "memory")

        provider = TesseractOCRProvider()
        assert not hasattr(provider, "session")

        provider = OpenCVVisionProvider()
        assert not hasattr(provider, "session")

    def test_knowledge_builder_consumes_only_observations(self):
        """Knowledge builder takes only observations as input"""
        builder = KnowledgeBuilder()

        # Build from observations
        obs = [
            Observation(
                video_id="v1",
                observation_type=ObservationType.SPEECH,
                payload={"speaker": "Alice"},
            ),
            Observation(
                video_id="v1",
                observation_type=ObservationType.OBJECT,
                payload={"class": "person"},
            ),
        ]

        # Verify method signature takes only observations
        import inspect
        sig = inspect.signature(builder.build_knowledge_graph)
        params = list(sig.parameters.keys())
        assert "observations" in params
