# Milestone 10 Phase 2: Semantic Intelligence Engines

## Implementation Status

**Status:** Complete  
**Completion Date:** 2026-07-28  
**Files Added:** 3 (engines.py, agents.py, evidence.py)  
**Lines of Code:** 1,500+  
**Tests:** 50+ comprehensive tests  

---

## Overview

Phase 2 implements the complete intelligence pipeline as **stateless, deterministic engines** that consume M9's Observation stream and produce immutable content objects with explainability artifacts.

### Key Design Principle

> **Every engine is stateless and deterministic.** Given the same observations, a engine always produces the same results, enabling repeatable analysis and offline composition.

---

## 1. Evidence and Scoring Models (`evidence.py`)

### ContentEvidence

Immutable evidence artifact tracking which observations supported a discovery:

```python
@dataclass(frozen=True)
class ContentEvidence:
    discovery_type: str  # "story", "highlight", "hook", etc.
    discovery_id: str    # ID of the discovered object
    
    observation_ids: List[str]           # Source observations
    observation_types_used: List[str]    # Types used in discovery
    
    evidence_quality: float      # 0-1: how strong/direct
    coverage_percentage: float   # % of discovery supported
    
    summary: str                 # Brief evidence explanation
    reasoning: str               # Why these observations matter
    analysis_method: str         # Which engine produced this
```

**Purpose:** Provides complete traceability from final content object back to M9 observations.

### ScoreCard

Immutable scorecard tracking all scoring decisions:

```python
@dataclass(frozen=True)
class ScoreCard:
    target_type: str      # What was scored
    target_id: str        # ID of scored object
    
    final_score: float            # 0-1 composite score
    final_confidence: float       # Confidence in score
    
    dimension_scores: Dict[ScoringDimension, float]
    dimension_confidences: Dict[ScoringDimension, float]
    dimension_reasoning: Dict[ScoringDimension, str]
    
    aggregation_strategy: str     # How dimensions were combined
    dimension_weights: Dict       # Custom weights used
    
    analysis_engine: str          # Which engine scored this
```

**Purpose:** Complete transparency into scoring decisions for downstream analysis and debugging.

### AnalysisOutput

Bundles the discovered object with supporting evidence and scorecard:

```python
@dataclass(frozen=True)
class AnalysisOutput:
    engine_name: str          # Which engine produced this
    output_type: str          # "story", "highlight", etc.
    
    output_data: Dict[str, Any]   # The discovery (serialized)
    evidence: ContentEvidence     # Traceability
    scorecard: ScoreCard          # Scoring transparency
    
    is_confident: bool            # Should this be trusted?
    requires_review: bool         # Needs human validation?
    review_reason: str
```

---

## 2. Intelligence Engines (`engines.py`)

### Base Class: IntelligenceEngine

```python
class IntelligenceEngine(ABC):
    """Base for all semantic intelligence engines.
    
    Stateless, deterministic engines consume Observations and produce
    immutable content objects with evidence and scorecards.
    """
    
    @abstractmethod
    def analyze(
        self,
        observations: List[Observation],
        timeline: Optional[Timeline] = None,
        session: Optional[AnalysisSession] = None,
    ) -> List[AnalysisOutput]:
        """Analyze and produce outputs."""
        pass
```

**Key Properties:**
- **Stateless**: No instance variables persist between calls
- **Deterministic**: Same observations → same results
- **Pure**: Side-effect free (no external API calls, no I/O)
- **Testable**: Can be tested offline with fixtures

### Seven Implementation Engines

#### 1. **StoryEngine** — Narrative Structure

Builds Story objects from observation sequence:

```python
class StoryEngine(IntelligenceEngine):
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Extract speech, objects, scenes from observations
        # 2. Score narrative structure
        # 3. Create StorySegment objects for narrative phases
        # 4. Create Story root aggregate
        # 5. Generate ContentEvidence and ScoreCard
        # 6. Return AnalysisOutput with all artifacts
```

**Workflow:**
1. Groups observations by type (SPEECH, SCENE_CONTENT, OBJECT)
2. Scores story elements using Importance + Confidence dimensions
3. Segments narrative into phases (introduction → climax → resolution)
4. Produces immutable Story with supporting evidence

**Evidence Provided:**
- Which observations shaped story structure
- Coverage percentage of video in narrative
- Why this segmentation makes sense

#### 2. **HighlightEngine** — Key Moments

Identifies peak moments through observation clustering:

```python
class HighlightEngine(IntelligenceEngine):
    def _find_highlight_candidates(self, observations):
        # Find dense clusters of observations
        # Return 5-10 candidate windows
    
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Find candidate highlight windows
        # 2. Score each on Importance, Emotion, Engagement
        # 3. Create Highlight for each candidate
        # 4. Generate evidence (why this is a key moment)
        # 5. Return ranked AnalysisOutputs
```

**Scoring Dimensions:**
- Importance: How significant is this moment?
- Emotion: Emotional intensity (speech + faces + sentiment)
- Engagement: Would audience care? (questions, CTAs, hooks)
- Visual Quality: Resolution, lighting, sharpness

#### 3. **HookEngine** — Attention Grabbers

Analyzes opening sequence for hooks:

```python
class HookEngine(IntelligenceEngine):
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Focus on opening 15% of video
        # 2. Identify hook types: Question, Conflict, Surprise, etc.
        # 3. Score each on Engagement + Novelty
        # 4. Rank by hook_score
        # 5. Return top 3 hooks with evidence
```

**Hook Types:**
- Question: Opens with compelling question
- Conflict: Introduces problem/tension
- Surprise: Unexpected element
- Emotion: Emotional appeal
- Statement: Provocative claim
- Visual: Strong visual element
- Curiosity: "Wait, what?"

#### 4. **ChapterEngine** — Temporal Structure

Segments video into semantic chapters:

```python
class ChapterEngine(IntelligenceEngine):
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Count scene transitions (SCENE_CONTENT observations)
        # 2. Create chapters based on scene boundaries
        # 3. Score chapters on Importance + Topic Strength
        # 4. Assign titles and summaries
        # 5. Return Chapter objects with evidence
```

**Chapter Structure:**
- Temporal divisions based on scene changes
- 3-5 chapters per video (configurable)
- Each has title, summary, importance score
- Tracks associated topics and observations

#### 5. **TopicEngine** — Semantic Themes

Extracts semantic topics from observations:

```python
class TopicEngine(IntelligenceEngine):
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Extract entities from OBJECT observations
        # 2. Count entity mentions (strength metric)
        # 3. Score on Topic Strength dimension
        # 4. Create Topic for each entity
        # 5. Link observations and chapters
```

**Topic Extraction:**
- Entity detection from object observations
- Mention count → strength (more mentions = stronger topic)
- Duration → relevance (how long discussed)
- Associated chapters and observations

#### 6. **QuoteEngine** — Quotable Moments

Identifies memorable quotes from speech:

```python
class QuoteEngine(IntelligenceEngine):
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Filter to SPEECH observations
        # 2. Extract text from payload
        # 3. Score on Topic Strength (length, keywords)
        # 4. Create Quote for each candidate
        # 5. Return top 3 with evidence
```

**Quote Attributes:**
- Text content
- Speaker (if available)
- Type: opinion, definition, statistic, CTA, memorable
- Relevance score
- Timestamp for easy reference

#### 7. **RecommendationEngine** — Actionable Suggestions

Produces content recommendations:

```python
class RecommendationEngine(IntelligenceEngine):
    def analyze(self, observations) -> List[AnalysisOutput]:
        # 1. Analyze engagement patterns
        # 2. Score on Engagement dimension
        # 3. Create Recommendations for:
        #    - YouTube Short (30s version)
        #    - Podcast Clip (key audio moments)
        #    - Thumbnail (peak visual moment)
        #    - Title/Subtitle suggestions
        # 4. Provide specific time ranges
```

**Recommendation Types:**
- youtube_short, podcast_clip, instagram_reel, linkedin_clip
- strong_cta, trim_silence, split_chapter
- thumbnail, title, subtitle

---

## 3. M6 Agent Wrappers (`agents.py`)

### ContentIntelligenceAgent

Wraps IntelligenceEngine for M8 orchestration:

```python
class ContentIntelligenceAgent(ExecutableAgent):
    """M6 Agent wrapper for IntelligenceEngine."""
    
    async def execute(
        self,
        context: AgentContext,
        input_data: Dict[str, Any],
    ) -> AgentResult:
        """Execute via M8 Task Orchestration.
        
        Input: serialized observations + session context
        Output: AnalysisOutput objects (serialized)
        """
```

**Execution Flow:**
1. Receive serialized observations from M8 Dispatcher
2. Reconstruct Observation objects
3. Run engine.analyze()
4. Serialize results back to JSON
5. Return via AgentResult

### Seven Agent Subclasses

Each engine has a corresponding M6 agent:

```python
class StoryAnalysisAgent(ContentIntelligenceAgent):
    def __init__(self, scoring_registry=None):
        super().__init__(StoryEngine(scoring_registry))

class HighlightAnalysisAgent(ContentIntelligenceAgent):
    # ... similar structure
```

### ContentIntelligenceAgentRegistry

Registry for M8 Dispatcher:

```python
class ContentIntelligenceAgentRegistry:
    """Registry of M6 agents for M8."""
    
    def register(self, agent: ContentIntelligenceAgent)
    def get(self, agent_name: str)
    def list_agents(self) -> List[str]
    def get_agents_by_output_type(self, output_type: str)
```

---

## 4. Execution Model

### Via M8 Task Orchestration

```
M9: VideoIngestionPipeline
   ↓ (submits observations)
M8: TaskGraph (7 analysis tasks)
   ├→ StoryAnalysisAgent (parallel)
   ├→ HighlightAnalysisAgent (parallel)
   ├→ HookAnalysisAgent (parallel)
   ├→ ChapterAnalysisAgent (parallel)
   ├→ TopicAnalysisAgent (parallel)
   ├→ QuoteAnalysisAgent (parallel)
   └→ RecommendationAnalysisAgent (parallel)
   ↓ (collects results)
M9: Appends AnalysisOutput[] to AnalysisSession
   ↓
M7: Persists to Memory Runtime
```

**Concurrency:** All 7 engines execute in parallel (no dependencies).

**Determinism:** Same observation set always produces same outputs.

**Statelessness:** Engines don't retain state between executions.

---

## 5. Explainability Architecture

### Evidence Chain

```
AnalysisOutput
├─ Highlight (discovery)
│  ├─ ContentEvidence
│  │  ├─ observation_ids: [obs-5, obs-6, obs-12]
│  │  ├─ summary: "3 observations support highlight"
│  │  ├─ reasoning: "High emotion + novelty"
│  │  └─ analysis_method: "HighlightEngine"
│  └─ ScoreCard
│     ├─ final_score: 0.85
│     ├─ dimension_scores: {
│     │    IMPORTANCE: 0.9,
│     │    EMOTION: 0.8,
│     │    ENGAGEMENT: 0.82
│     │  }
│     └─ dimension_reasoning: {
│          IMPORTANCE: "High entity count (5 entities)",
│          EMOTION: "Strong facial expressions (0.8 avg)",
│          ENGAGEMENT: "Multiple questions detected"
│        }
```

### Query Example: "Why is this a highlight?"

```
1. Look at AnalysisOutput.evidence.reasoning:
   → "High emotion and novelty detected"

2. Check ScoreCard.dimension_reasoning:
   → EMOTION: "Speech emotion 0.7 + face emotions [0.75, 0.8]"
   → ENGAGEMENT: "Strong questions and hook presence"

3. Trace back to observations:
   → [obs-5, obs-6, obs-12] are the evidence
   → Pull these observations to see raw data

4. Result: Human understands exactly why engine scored this as highlight
```

---

## 6. Determinism Guarantees

### Statelessness

Engines have **zero instance state**:
- No caches
- No session storage
- No external API state
- Only pure functions

```python
# This is safe - engine produces same result
engine = HighlightEngine()
result1 = engine.analyze(observations)

result2 = engine.analyze(observations)  # Identical to result1
```

### Determinism

```python
# These produce identical results:
engine1 = StoryEngine()
engine2 = StoryEngine()

output1 = engine1.analyze(observations)
output2 = engine2.analyze(observations)

assert output1[0].output_data == output2[0].output_data
```

### Implications

- **Offline analysis**: Run engines on historical data
- **Validation**: Compare outputs across versions
- **Debugging**: Reproduce issues reliably
- **Testing**: Comprehensive coverage with fixtures

---

## 7. Integration with M1–M9

### Input: M9 Observations

Engines consume only immutable Observation objects:

```python
observations: List[Observation] = [
    Observation(
        id="obs-5",
        video_id="v1",
        observation_type=ObservationType.SPEECH,
        source_agent="WhisperSpeechProvider",
        start_timestamp=30.0,
        end_timestamp=35.0,
        payload={"text": "...", "speaker": "..."},
        metadata={},
    ),
    # ...
]

output = engine.analyze(observations)
```

### Output: AnalysisSession Integration

M9 appends Phase 2 outputs to session:

```python
session = AnalysisSession(...)
analysis_outputs = [
    output1, output2, output3, ...
]

# M9 converts outputs to observation-compatible format
# and appends to session.metadata or new observations
```

### No M1–M9 Modifications

- Phase 2 is **purely additive**
- No changes to Video, Timeline, Observation models
- No changes to M6, M7, M8 contracts
- Backward compatible with existing code

---

## 8. Key Architectural Decisions

### Decision 1: Stateless Engines
**Rationale:** Enables parallel execution, repeatable analysis, offline composition.
**Alternative Considered:** Stateful engines with caching (rejected due to complexity and non-determinism).

### Decision 2: Evidence + Scorecard
**Rationale:** Explainability is critical for AI systems. Every discovery needs justification.
**Alternative Considered:** Just scorecards (rejected; lost traceability to observations).

### Decision 3: M6 Agents for Orchestration
**Rationale:** Leverages M8 Task Orchestration, enables concurrent execution, allows dispatcher to manage resources.
**Alternative Considered:** Direct engine invocation (rejected; loses M8 benefits).

### Decision 4: Immutable Output Objects
**Rationale:** Prevents mutation bugs, enables safe concurrency, fits M7 persistence model.
**Alternative Considered:** Mutable objects with validation (rejected due to safety concerns).

### Decision 5: No LLM Calls in Engines
**Rationale:** Keeps engines deterministic and fast. LLM integration happens in Phase 3.
**Alternative Considered:** Use LLMs in engines (rejected; introduces non-determinism and latency).

---

## 9. Phase 2 → Phase 3 Handoff

Phase 3 will add **LLM-powered enhancement**:

- **LLM-based reranking**: Use Claude/GPT to reorder highlights by importance
- **LLM-based summarization**: Generate better titles and descriptions
- **LLM-based narrative**: Build prose story descriptions
- **LLM-based recommendations**: Generate custom social media suggestions

All LLM integration happens **after** Phase 2 analysis, preserving determinism and allowing fallback to Phase 2 results if LLM fails.

---

## 10. Testing Strategy

Phase 2 tests verify:

✅ **Immutability** — ContentEvidence, ScoreCard, AnalysisOutput frozen  
✅ **Statelessness** — Same observations → same outputs  
✅ **Determinism** — Multiple engine instances → identical results  
✅ **Evidence Quality** — Traceable to source observations  
✅ **Scorecard Accuracy** — Dimension scores compose correctly  
✅ **Agent Execution** — M6 wrapper handles async correctly  
✅ **Registry Patterns** — EngineRegistry and AgentRegistry work  
✅ **Edge Cases** — Empty observations, single observation, large sets  
✅ **Integration** — All 7 engines can run on same observations  

---

## 11. File Structure

```
aura_backend/content/
├── __init__.py                    # Updated exports
├── models.py                      # Phase 1: Domain models
├── scoring.py                     # Phase 1: Scoring framework
├── llm_providers.py               # Phase 1: LLM abstraction
├── evidence.py                    # Phase 2: Evidence + scoring
├── engines.py                     # Phase 2: Intelligence engines
├── agents.py                      # Phase 2: M6 agents
├── M10_PHASE1_ARCHITECTURE.md    # Phase 1 design
└── M10_PHASE2_ARCHITECTURE.md    # This file

tests/content/
├── test_m10_phase1.py            # Phase 1 tests
└── test_m10_phase2.py            # Phase 2 tests (50+ tests)
```

---

## Next: Phase 3

Phase 3 will implement **LLM Enhancement and Story Composition**:

- **StoryComposer**: Build narrative prose from segments
- **HighlightRanker**: Rerank using Claude/GPT
- **TitleGenerator**: LLM-based title generation
- **DescriptionWriter**: Expand discovery descriptions
- **RecommendationRefiner**: Customize recommendations

All LLM calls happen **after** Phase 2 analysis, preserving determinism.
