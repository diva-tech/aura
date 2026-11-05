# Milestone 10: Content Intelligence & Story Engine

## Phase 1: Domain Models, Scoring Framework, and LLM Providers

**Status:** Complete  
**Completion Date:** 2026-07-28

---

## Overview

Phase 1 establishes the immutable domain model for semantic content intelligence and the pluggable infrastructure for scoring and LLM-driven analysis.

**Key Principle:** All M10 components are built on top of M9's Observation Stream. Nothing modifies M1–M9; everything flows through the existing architecture.

---

## 1. Domain Models (`models.py`)

### Story-Related Models

#### `Story` (Root Aggregate for Phase 1)

```python
@dataclass(frozen=True)
class Story:
    id: str                          # Unique story ID
    session_id: str                  # AnalysisSession reference
    video_id: str                    # Video reference

    title: str                       # Story headline
    summary: str                     # Story summary

    segments: List[StorySegment]     # Narrative structure

    # Metrics
    story_score: float               # 0-1 overall quality
    average_confidence: float        # Average confidence across segments
    coverage_percentage: float       # % of video with identified story

    observation_ids: List[str]       # Source observations from M9
    metadata: Dict[str, Any]         # Provider metadata
    created_at: datetime
```

**Immutability:** Frozen dataclass. New Story objects are created with updated fields; old ones are never mutated.

**Traceability:** Every Story references its source AnalysisSession and observation IDs for full auditability.

#### `StorySegment`

Represents phases of narrative arc (introduction, rising_action, climax, falling_action, resolution).

#### `StoryPhase` Enum

```python
class StoryPhase(str, Enum):
    INTRODUCTION = "introduction"
    RISING_ACTION = "rising_action"
    CLIMAX = "climax"
    FALLING_ACTION = "falling_action"
    RESOLUTION = "resolution"
    UNKNOWN = "unknown"
```

---

### Highlight, Hook, Chapter, Topic, Quote, Recommendation

**`Highlight`** — Key moments in video

- start/end timestamps
- importance, emotion, visual_quality, confidence scores
- observation references

**`Hook`** — Attention-grabbing openings

- HookType enum (question, conflict, surprise, emotion, statement, visual, curiosity)
- hook_score (effectiveness)
- rank (position in ranked list)

**`Chapter`** — Semantic divisions of video

- title, summary
- topic_ids and observation_ids
- importance score

**`Topic`** — Semantic themes

- label, description
- strength, confidence
- observation_ids and chapter_ids

**`Quote`** — Extracted quotable moments

- text, speaker
- quote_type (opinion, definition, statistic, cta, memorable)
- relevance and confidence

**`Recommendation`** — Content recommendations

- RecommendationType enum (youtube_short, podcast_clip, instagram_reel, etc.)
- score and confidence
- observation references

---

### Graph Model: `StoryGraph`

Connects all intelligence components into a coherent graph:

```python
@dataclass(frozen=True)
class StoryGraph:
    id: str
    session_id: str
    video_id: str

    # Core content
    story_id: str
    chapter_ids: List[str]
    highlight_ids: List[str]
    hook_ids: List[str]
    topic_ids: List[str]
    quote_ids: List[str]
    recommendation_ids: List[str]

    # Relationships
    relationships: Dict[str, List[str]]  # Semantic edges

    created_at: datetime
```

**No mutation:** The StoryGraph is built once by Phase 4's ContentPlanner and never modified.

---

### Metrics: `ContentMetrics`

Immutable metrics from the complete M10 pipeline:

```python
@dataclass(frozen=True)
class ContentMetrics:
    id: str
    session_id: str
    video_id: str

    # Processing
    processing_duration_seconds: float

    # Content quality
    story_score: float
    average_confidence: float
    coverage_percentage: float

    # Component counts
    highlight_count: int
    hook_count: int
    chapter_count: int
    topic_count: int
    quote_count: int
    recommendation_count: int

    # Engagement
    engagement_score: float  # 0-100

    # Quality tracking
    observation_count: int
    observation_types_used: List[str]

    created_at: datetime
```

---

## 2. Scoring Framework (`scoring.py`)

### Design: Pluggable, Composable, Independent

The scoring framework is **separated from analysis engines**. This allows:

- Independent tuning of scoring strategies
- Composition of dimension scores into aggregate scores
- Easy testing and benchmarking of scoring logic
- Swappable implementations

### Scoring Dimensions

```python
class ScoringDimension(str, Enum):
    IMPORTANCE = "importance"
    EMOTION = "emotion"
    NOVELTY = "novelty"
    ENGAGEMENT = "engagement"
    SPEECH_QUALITY = "speech_quality"
    VISUAL_QUALITY = "visual_quality"
    TOPIC_STRENGTH = "topic_strength"
    CONFIDENCE = "confidence"
    HOOK_EFFECTIVENESS = "hook_effectiveness"
    RECOMMENDATION_SCORE = "recommendation_score"
```

### Scoring Result

```python
@dataclass(frozen=True)
class ScoringResult:
    dimension: ScoringDimension
    score: float                           # 0-1
    confidence: float                      # 0-1 confidence in score
    reasoning: str                         # Human-readable explanation
    contributing_factors: Dict[str, float] # Breakdown of components
```

Every ScoringResult is immutable and includes reasoning for interpretability.

### Strategy Pattern: `ScoringStrategy`

Base class for all scorers:

```python
class ScoringStrategy(ABC):
    @abstractmethod
    def score(self, data: Dict[str, Any]) -> ScoringResult:
        pass
```

**Reference Implementations:**

1. **`ImportanceScorer`** — Content significance
   - Entity count (0.3)
   - Primary topics presence (0.4)
   - Segment duration (0.3)

2. **`EmotionScorer`** — Emotional intensity
   - Speech emotion from Whisper/M9 (0.4)
   - Face emotions from vision analysis (0.35)
   - Text sentiment (0.25)

3. **`NoveltyScorer`** — Unexpectedness
   - Rare entities (0.35)
   - Scene transitions (0.35)
   - New topics (0.3)

4. **`EngagementScorer`** — Audience engagement potential
   - Questions/CTAs (0.25)
   - CTA strength (0.2)
   - Pacing (0.2)
   - Hook presence (0.35)

5. **`SpeechQualityScorer`** — Audio quality
   - SNR (signal-to-noise ratio) (0.35)
   - Clarity/articulation (0.35)
   - Artifact absence (0.3)

6. **`VisualQualityScorer`** — Video quality
   - Resolution (0.3)
   - Lighting (0.35)
   - Sharpness (0.35)

7. **`TopicStrengthScorer`** — Topic prominence
   - Mention count (0.4)
   - Duration (0.3)
   - Associated entities (0.3)

8. **`ConfidenceScorer`** — Meta-confidence
   - Data quality (0.35)
   - Signal agreement (0.35)
   - Observation coverage (0.3)

### Aggregation: `ScoreAggregator`

Combines dimension scores into final scores via multiple strategies:

```python
class ScoreAggregator:
    @staticmethod
    def weighted_average(scores, weights=None) -> float

    @staticmethod
    def confidence_weighted_average(scores, weights=None) -> float

    @staticmethod
    def min_score(scores) -> float

    @staticmethod
    def max_score(scores) -> float
```

**Confidence-weighted average** is default: low-confidence scores have less influence on final score.

### Registry: `ScoringRegistry`

Pluggable strategy registration:

```python
registry = ScoringRegistry()
registry.register_strategy(ScoringDimension.IMPORTANCE, CustomImportanceScorer())
```

### Pipeline: `ScoringPipeline`

Complete end-to-end scoring:

```python
pipeline = ScoringPipeline(registry)

# Score across dimensions with aggregation
final_score = pipeline.score(
    data={...},
    dimensions=[ScoringDimension.IMPORTANCE, ScoringDimension.ENGAGEMENT],
    weights={ScoringDimension.IMPORTANCE: 1.5},
    aggregation="confidence_weighted"
)

# Get detailed breakdowns
aggregate, detailed_results = pipeline.score_detailed(data)
```

---

## 3. LLM Provider Abstraction (`llm_providers.py`)

### Design: Provider-Agnostic

Every M10 intelligence component uses a common LLM interface. Implementations can be swapped without touching analysis code.

### LLM Models

```python
class LLMModel(str, Enum):
    CLAUDE_3_5_SONNET = "claude-3-5-sonnet"
    CLAUDE_3_OPUS = "claude-3-opus"
    GPT_4_TURBO = "gpt-4-turbo"
    GPT_4O = "gpt-4o"
    GEMINI_2_0_PRO = "gemini-2-0-pro"
    LOCAL_OLLAMA = "local-ollama"
```

### LLM Response

```python
@dataclass(frozen=True)
class LLMResponse:
    model: str
    content: str
    stop_reason: str  # "stop_sequence", "max_tokens", "error"
    usage: Dict[str, int]  # input_tokens, output_tokens
    error: Optional[str]
    metadata: Dict[str, Any]
```

Immutable response with:

- `is_success()` — Check if generation succeeded
- `get_json()` — Extract and parse JSON from response

### Provider Interface

```python
class LLMProvider(ABC):
    @abstractmethod
    def generate(self, prompt: str, system: Optional[str] = None, **kwargs) -> LLMResponse:
        pass

    @abstractmethod
    def generate_json(self, prompt: str, schema: Dict[str, Any], system: Optional[str] = None, **kwargs) -> LLMResponse:
        pass

    @abstractmethod
    def supports_model(self, model: LLMModel) -> bool:
        pass

    @abstractmethod
    def get_default_model(self) -> LLMModel:
        pass
```

### Reference Implementations

**1. `AnthropicProvider`** — Claude

```python
provider = AnthropicProvider(api_key="sk-...", model=LLMModel.CLAUDE_3_5_SONNET)
response = provider.generate("Extract topics from transcript", system="You are an expert analyst")
```

**2. `OpenAIProvider`** — GPT-4, GPT-4o

```python
provider = OpenAIProvider(api_key="sk-...", model=LLMModel.GPT_4O)
response = provider.generate_json("List highlights", schema={"highlights": [...]})
```

**3. `GeminiProvider`** — Google Gemini

```python
provider = GeminiProvider(api_key="...", model=LLMModel.GEMINI_2_0_PRO)
```

**4. `LocalOllamaProvider`** — Local models

```python
provider = LocalOllamaProvider(base_url="http://localhost:11434", model="neural-chat")
```

### Registry: `LLMProviderRegistry`

```python
registry = create_default_registry()
registry.register("custom", CustomProvider(), is_default=True)

claude = registry.get("claude")
gemini = registry.get_by_model(LLMModel.GEMINI_2_0_PRO)
default = registry.get_default()
```

---

## 4. Architectural Principles

### Immutability

- All domain models are frozen dataclasses
- New instances created with updated fields; old ones never mutated
- Enables safe concurrent processing

### Traceability

- Every content intelligence object references:
  - `session_id` (AnalysisSession)
  - `video_id` (source video)
  - `observation_ids` (M9 observations used)
- Full auditability from raw observations to final story

### Separation of Concerns

- **Domain models:** What we're analyzing
- **Scoring:** How we rank content
- **LLM providers:** External intelligence
- **Agents (Phase 2):** Business logic for discoveries

### Provider Abstraction

- No third-party data structures leak outside providers
- All results converted to immutable domain objects immediately
- Easy to swap implementations

### M1–M9 Preservation

- M10 consumes only Observation objects from M9
- M10 persists only through M7 Memory Runtime (via M9's pipeline)
- No modifications to existing milestones

---

## 5. Integration with M1–M9

### Input: Observation Stream (M9)

```python
# M9 produces observations
observations = timeline.get_observations_by_type(ObservationType.SPEECH)

# M10 consumes them
story_engine = StoryEngine(llm_provider, scoring_registry)
story = story_engine.build_story(observations)
```

### Integration Points

**M6 Agent Framework:**

- Phase 2 engines (StoryAgent, HighlightAgent, etc.) are ExecutableAgent subclasses

**M8 Task Orchestration:**

- Phase 4's ContentPlanner creates TaskGraph
- M8's Scheduler/Dispatcher/CapabilityResolver executes agents in parallel
- Results collected and appended to AnalysisSession

**M7 Memory Runtime:**

- M9's VideoIngestionPipeline has sole access to Memory (via persist_session_to_memory)
- M9 appends M10 results to session before persisting
- Immutable domain objects guarantee consistency

---

## 6. Key Architectural Decisions

### Decision 1: Separate Scoring from Analysis

**Rationale:** Scoring is a cross-cutting concern. Separating it allows:

- Independent tuning of scoring weights
- Reuse across engines
- Easy testing and benchmarking
- Pluggable strategies

### Decision 2: Immutable Domain Models

**Rationale:** Enables:

- Thread-safe concurrent processing (Phase 3+)
- Audit trail of changes
- Easy serialization to JSON for Memory Runtime
- Clear semantics (no hidden state)

### Decision 3: Provider-Agnostic LLM Abstraction

**Rationale:**

- Cost optimization: swap providers based on task
- Resilience: fallback to alternative providers
- Testing: mock implementations for unit tests
- Independence: change LLM without touching analysis logic

### Decision 4: Graph Model (StoryGraph)

**Rationale:** Stores all relationships:

- Highlights belong to Chapters belong to Stories
- Topics span multiple Highlights
- Quotes reference specific Observations
- Enables downstream traversal and ranking

---

## 7. Phase 1 → Phase 2 Handoff

Phase 2 builds the analysis engines that **produce** these models:

- **StoryEngine** → produces Story, StorySegment
- **HighlightEngine** → produces Highlight objects
- **HookEngine** → produces Hook objects with ranking
- **ChapterEngine** → produces Chapter objects
- **TopicEngine** → produces Topic objects
- **QuoteEngine** → produces Quote objects
- **RecommendationEngine** → produces Recommendation objects

Each engine:

1. Consumes Observation stream from M9
2. Uses LLM provider to analyze content
3. Uses scoring pipeline to rank candidates
4. Returns immutable domain objects
5. Registers as M6 Agent for M8 orchestration

---

## 8. Testing Strategy

Phase 1 tests verify:

- ✓ Model immutability (frozen dataclasses)
- ✓ Scoring strategies are pluggable
- ✓ LLM providers are interchangeable
- ✓ Registry patterns work correctly
- ✓ JSON serialization/deserialization
- ✓ Reference implementations don't crash

---

## File Structure

```
aura_backend/content/
├── __init__.py                         # Exports
├── models.py                           # Domain models
├── scoring.py                          # Scoring framework
├── llm_providers.py                    # LLM provider abstraction
├── M10_PHASE1_ARCHITECTURE.md         # This file
└── tests/
    └── test_m10_phase1.py             # Phase 1 tests
```

---

## Next: Phase 2

Phase 2 implements the **Intelligence Engines**:

- StoryEngine
- HighlightEngine
- HookEngine
- ChapterEngine
- TopicEngine
- QuoteEngine
- RecommendationEngine

Each engine:

- Takes Observation stream as input
- Produces immutable domain objects
- Uses scoring pipeline for ranking
- Registers as M6 Agent for M8 orchestration
