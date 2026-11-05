# M10 Phase 1: Quick Reference

## Domain Models

### Creating Story Objects

```python
from aura_backend.content import (
    Story, StorySegment, StoryPhase,
    Highlight, Hook, HookType,
    Chapter, Topic, Quote, Recommendation,
    StoryGraph, ContentMetrics
)

# Create a story segment (narrative phase)
segment = StorySegment(
    story_id="s1",
    video_id="v1",
    phase=StoryPhase.CLIMAX,
    start_timestamp=30.0,
    end_timestamp=45.0,
    description="The turning point",
    importance=0.95,
    observation_ids=["obs-1", "obs-2"],
)

# Create complete story
story = Story(
    session_id="sess-1",
    video_id="v1",
    title="User Journey",
    summary="Complete narrative arc",
    segments=[segment],
    story_score=0.85,
    observation_ids=["obs-1", "obs-2", "obs-3"],
)

# Verify immutability
# story.title = "New Title"  # Raises FrozenInstanceError
```

### Creating Highlights

```python
highlight = Highlight(
    session_id="sess-1",
    video_id="v1",
    story_id="s1",
    start_timestamp=15.0,
    end_timestamp=20.0,
    title="Peak Engagement",
    description="Audience fully engaged",
    reason="High emotion + novelty",

    # Multi-dimensional scoring
    importance=0.9,
    emotion=0.85,
    visual_quality=0.8,
    confidence=0.92,

    observation_ids=["obs-5", "obs-6"],
)
```

### Creating Hooks

```python
hook = Hook(
    session_id="sess-1",
    video_id="v1",
    start_timestamp=0.0,
    end_timestamp=3.0,
    hook_type=HookType.QUESTION,
    title="Have you ever wondered?",
    description="Opens with compelling question",
    hook_score=0.95,
    confidence=0.88,
    rank=1,  # Top hook
    observation_ids=["obs-1"],
)
```

### Creating Chapters

```python
chapter = Chapter(
    session_id="sess-1",
    video_id="v1",
    story_id="s1",
    start_timestamp=0.0,
    end_timestamp=60.0,
    title="Introduction",
    summary="Scene setting and context",
    importance=0.7,
    topic_ids=["topic-1", "topic-2"],
    observation_ids=["obs-1", "obs-2", "obs-3"],
)
```

### Creating Topics

```python
topic = Topic(
    session_id="sess-1",
    video_id="v1",
    label="Artificial Intelligence",
    description="Discussions of AI systems and capabilities",
    strength=0.92,
    confidence=0.85,
    observation_ids=["obs-5", "obs-6", "obs-7"],
    chapter_ids=["c1", "c2"],
)
```

### Creating Quotes

```python
quote = Quote(
    session_id="sess-1",
    video_id="v1",
    start_timestamp=45.2,
    end_timestamp=52.1,
    text="AI will augment human capabilities",
    speaker="Jane Smith",
    quote_type="opinion",
    relevance=0.95,
    confidence=0.98,
    observation_ids=["obs-12"],
)
```

### Creating Recommendations

```python
from aura_backend.content import RecommendationType

recommendation = Recommendation(
    session_id="sess-1",
    video_id="v1",
    rec_type=RecommendationType.YOUTUBE_SHORT,
    title="30-second summary",
    description="Extract highlights 15s-45s",
    reason="Peak engagement and emotional impact",
    score=0.89,
    confidence=0.92,
    start_timestamp=15.0,
    end_timestamp=45.0,
    observation_ids=["obs-5", "obs-6"],
)
```

### Creating Story Graph

```python
graph = StoryGraph(
    session_id="sess-1",
    video_id="v1",
    story_id="s1",
    chapter_ids=["c1", "c2", "c3"],
    highlight_ids=["h1", "h2", "h3"],
    hook_ids=["k1", "k2"],
    topic_ids=["t1", "t2", "t3", "t4"],
    quote_ids=["q1", "q2", "q3"],
    recommendation_ids=["r1", "r2"],
    relationships={
        "h1": ["t1", "t2"],  # Highlight h1 has topics t1, t2
        "c1": ["h1", "h2"],  # Chapter c1 contains highlights h1, h2
        "t1": ["q1", "q2"],  # Topic t1 has quotes q1, q2
    },
)
```

### Metrics

```python
metrics = ContentMetrics(
    session_id="sess-1",
    video_id="v1",
    processing_duration_seconds=23.4,
    story_score=0.85,
    average_confidence=0.89,
    coverage_percentage=82.5,
    highlight_count=5,
    hook_count=2,
    chapter_count=4,
    topic_count=8,
    quote_count=12,
    recommendation_count=3,
    engagement_score=78.3,
    observation_count=42,
)

# Access metrics
print(f"Story quality: {metrics.story_score}")
print(f"Processed in {metrics.processing_duration_seconds}s")
print(f"Found {metrics.highlight_count} highlights")
```

---

## Scoring Framework

### Using the Scoring Pipeline

```python
from aura_backend.content import (
    ScoringPipeline,
    ScoringDimension,
)

# Create pipeline with default strategies
pipeline = ScoringPipeline()

# Score content across dimensions
data = {
    "entity_count": 8,
    "primary_topics": ["AI", "innovation"],
    "duration_seconds": 35,
    "speech_emotion": 0.8,
    "face_emotions": [0.75, 0.85],
    "text_sentiment": 0.7,
}

# Get composite score
final_score = pipeline.score(
    data,
    dimensions=[
        ScoringDimension.IMPORTANCE,
        ScoringDimension.EMOTION,
        ScoringDimension.ENGAGEMENT,
    ],
    weights={
        ScoringDimension.IMPORTANCE: 1.5,  # Weight importance higher
        ScoringDimension.ENGAGEMENT: 1.2,
    },
    aggregation="confidence_weighted",  # or "weighted", "min", "max"
)

print(f"Final score: {final_score:.2f}")
```

### Get Detailed Scoring Results

```python
# Get detailed breakdown
aggregate, dimension_results = pipeline.score_detailed(
    data,
    dimensions=[
        ScoringDimension.IMPORTANCE,
        ScoringDimension.EMOTION,
    ],
)

for dimension, result in dimension_results.items():
    print(f"\n{dimension.value}:")
    print(f"  Score: {result.score:.2f}")
    print(f"  Confidence: {result.confidence:.2f}")
    print(f"  Reasoning: {result.reasoning}")
    print(f"  Factors: {result.contributing_factors}")
```

### Composing Scores Manually

```python
from aura_backend.content import (
    ScoringRegistry,
    ScoringDimension,
    ScoreAggregator,
)

# Get individual dimension scores
registry = ScoringRegistry()

results = registry.score_dimensions(
    data,
    [ScoringDimension.IMPORTANCE, ScoringDimension.NOVELTY],
)

# Aggregate with custom strategy
aggregate = ScoreAggregator.confidence_weighted_average(
    list(results.values()),
    weights={
        ScoringDimension.IMPORTANCE: 1.5,
        ScoringDimension.NOVELTY: 1.0,
    },
)
```

### Custom Scoring Strategy

```python
from aura_backend.content import ScoringStrategy, ScoringResult, ScoringDimension

class CustomImportanceScorer(ScoringStrategy):
    def score(self, data):
        # Your custom logic
        score = 0.8

        return ScoringResult(
            dimension=ScoringDimension.IMPORTANCE,
            score=score,
            confidence=0.85,
            reasoning="Custom calculation",
            contributing_factors={"custom_factor": 0.8},
        )

# Register and use
registry = ScoringRegistry()
registry.register_strategy(
    ScoringDimension.IMPORTANCE,
    CustomImportanceScorer()
)
```

---

## LLM Providers

### Using Default Registry

```python
from aura_backend.content import (
    create_default_registry,
    LLMModel,
)

# Get default registry (has Claude, OpenAI, Gemini, Ollama)
registry = create_default_registry()

# Get specific provider
claude = registry.get("claude")
openai = registry.get("openai")

# Get provider for model
gpt4 = registry.get_by_model(LLMModel.GPT_4O)

# Get default provider
default = registry.get_default()
```

### Text Generation

```python
# Simple text generation
response = claude.generate(
    prompt="Extract topics from this transcript: ...",
    system="You are an expert content analyst",
    max_tokens=500,
)

if response.is_success():
    print(response.content)
else:
    print(f"Error: {response.error}")

# Check usage
print(f"Input tokens: {response.usage['input_tokens']}")
print(f"Output tokens: {response.usage['output_tokens']}")
```

### JSON Generation

```python
schema = {
    "type": "object",
    "properties": {
        "highlights": {
            "type": "array",
            "items": {
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "reason": {"type": "string"},
                    "score": {"type": "number"},
                },
            },
        },
    },
}

response = claude.generate_json(
    prompt="Identify highlights in this content: ...",
    schema=schema,
)

if response.is_success():
    data = response.get_json()
    for highlight in data["highlights"]:
        print(f"- {highlight['title']}: {highlight['reason']}")
```

### Provider-Specific Initialization

```python
from aura_backend.content import (
    AnthropicProvider,
    OpenAIProvider,
    GeminiProvider,
    LocalOllamaProvider,
    LLMModel,
)

# Claude (Anthropic)
claude = AnthropicProvider(
    api_key="sk-ant-...",
    model=LLMModel.CLAUDE_3_5_SONNET,
)

# GPT-4 (OpenAI)
gpt4 = OpenAIProvider(
    api_key="sk-...",
    model=LLMModel.GPT_4O,
)

# Gemini (Google)
gemini = GeminiProvider(
    api_key="...",
    model=LLMModel.GEMINI_2_0_PRO,
)

# Local Ollama
ollama = LocalOllamaProvider(
    base_url="http://localhost:11434",
    model="neural-chat",
)
```

### Creating Custom Provider

```python
from aura_backend.content import LLMProvider, LLMResponse, LLMModel

class CustomLLMProvider(LLMProvider):
    def generate(self, prompt, system=None, **kwargs):
        # Your implementation
        return LLMResponse(
            model="custom",
            content="Response",
            stop_reason="stop_sequence",
            usage={"input_tokens": 10, "output_tokens": 5},
        )

    def generate_json(self, prompt, schema, system=None, **kwargs):
        # Your implementation
        return self.generate(prompt, system, **kwargs)

    def supports_model(self, model):
        return model == LLMModel.LOCAL_OLLAMA

    def get_default_model(self):
        return LLMModel.LOCAL_OLLAMA

# Register
registry = LLMProviderRegistry()
registry.register("custom", CustomLLMProvider(), is_default=True)
```

---

## Common Patterns

### Scoring Highlight Importance

```python
pipeline = ScoringPipeline()

highlight_data = {
    "entity_count": 5,
    "primary_topics": ["leadership"],
    "duration_seconds": 8,
    "speech_emotion": 0.85,
    "face_emotions": [0.8, 0.9],
    "has_hook": True,
}

score = pipeline.score(
    highlight_data,
    dimensions=[
        ScoringDimension.IMPORTANCE,
        ScoringDimension.EMOTION,
        ScoringDimension.ENGAGEMENT,
    ],
)

highlight = Highlight(
    session_id="sess-1",
    video_id="v1",
    importance=score,
)
```

### Ranking Hooks

```python
hooks = [...]  # List of Hook objects

# Create hooks with scores
scored_hooks = []
for hook, score in zip(hooks, hook_scores):
    scored_hook = Hook(
        session_id=hook.session_id,
        video_id=hook.video_id,
        # ... other fields ...
        hook_score=score,
        rank=len(scored_hooks) + 1,  # Set rank
    )
    scored_hooks.append(scored_hook)

# Sort by rank
ranked = sorted(scored_hooks, key=lambda h: h.rank)
```

### Building Knowledge Graph

```python
# Create all content objects
story = Story(...)
chapters = [Chapter(...), ...]
highlights = [Highlight(...), ...]
topics = [Topic(...), ...]
quotes = [Quote(...), ...]

# Build relationships
relationships = {
    # Map highlights to topics
    highlights[0].id: [topics[0].id, topics[1].id],
    # Map chapters to highlights
    chapters[0].id: [highlights[0].id, highlights[1].id],
    # Map topics to quotes
    topics[0].id: [quotes[0].id, quotes[1].id],
}

# Create graph
graph = StoryGraph(
    session_id="sess-1",
    video_id="v1",
    story_id=story.id,
    chapter_ids=[c.id for c in chapters],
    highlight_ids=[h.id for h in highlights],
    topic_ids=[t.id for t in topics],
    quote_ids=[q.id for q in quotes],
    relationships=relationships,
)
```

---

## Testing

Run Phase 1 tests:

```bash
cd app-backend
pytest tests/content/test_m10_phase1.py -v

# Specific test class
pytest tests/content/test_m10_phase1.py::TestStory -v

# Specific test
pytest tests/content/test_m10_phase1.py::TestStory::test_story_creation -v
```

---

## Key Principles

1. **Immutability**: All models are frozen. Create new instances with updated fields.
2. **Traceability**: Every object references session_id, video_id, and observation_ids.
3. **Pluggability**: Scoring strategies and LLM providers are interchangeable.
4. **Composition**: Dimension scores are composed into final scores.
5. **Separation**: Scoring is separate from analysis logic.

---

## Next Phase (Phase 2)

Phase 2 implements the **Intelligence Engines**:

- StoryEngine: Builds Story objects from observations
- HighlightEngine: Identifies key moments
- HookEngine: Ranks attention-grabbers
- ChapterEngine: Structures video into chapters
- TopicEngine: Extracts semantic topics
- QuoteEngine: Identifies quotable moments
- RecommendationEngine: Produces recommendations

Each engine:

- Consumes Observation stream
- Uses scoring pipeline
- Produces immutable domain objects
- Registers as M6 Agent
