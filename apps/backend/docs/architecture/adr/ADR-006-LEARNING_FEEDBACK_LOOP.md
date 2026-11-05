# ADR-006: Learning Feedback Loop

**Date**: 2026-07-30  
**Status**: Accepted  
**Deciders**: Architecture Team  
**Affects**: M14

## Context

Creating recommendations is only half the value. System must learn from:

- Which recommendations creators accept
- Performance impact of recommendations
- Creator feedback and behavior changes
- Long-term outcome metrics

Without feedback, system cannot improve recommendations over time.

## Decision

Implement **closed-loop learning** with explicit feedback capture and memory update.

### Learning Cycle

```
1. Analysis: Collect analytics data
2. Generation: Generate recommendations
3. Application: Creator applies recommendation
4. Measurement: Measure impact (increased views, engagement, etc.)
5. Feedback: Capture feedback in learning memory
6. Optimization: Use memory to improve future recommendations
7. Repeat: Next job uses improved memory
```

### Key Components

1. **LearningMemory**: Captures learning history
   - Which recommendations were accepted
   - Performance impact of changes
   - Feature importance for this creator
   - Optimization history

2. **RecommendationAcceptance**: Tracks acceptance

   ```python
   @dataclass(frozen=True)
   class RecommendationAcceptance:
       recommendation_id: str
       creator_id: str
       accepted: bool
       impact_metric: float  # +0.15 means 15% improvement
       created_at: datetime
   ```

3. **ExperimentRecord**: A/B test results

   ```python
   @dataclass(frozen=True)
   class ExperimentRecord:
       control_version: str
       variant_version: str
       creator_id: str
       statistically_significant: bool
       effect_size: float
   ```

4. **OptimizationHistory**: What was tried
   ```python
   @dataclass(frozen=True)
   class OptimizationHistory:
       optimization_id: str
       creator_id: str
       change_description: str
       success: bool
       learned_at: datetime
   ```

### Feedback Sources

1. **Direct**: Creator explicitly accepts/rejects recommendation
2. **Implicit**: Measure content performance before/after recommendation
3. **Behavioral**: Creator applies similar changes on their own
4. **Comparative**: A/B test recommendations with control group

### Memory Update Workflow

1. **Collection**: Collect feedback from multiple sources
2. **Validation**: Validate statistical significance
3. **Aggregation**: Aggregate into learning insights
4. **Storage**: Store in LearningMemory
5. **Indexing**: Index for efficient retrieval
6. **Pruning**: Keep recent history, prune old

## Benefits

✓ **Continuous improvement**: Recommendations improve over time
✓ **Personalization**: Each creator gets customized recommendations
✓ **Measurable impact**: Can quantify improvement
✓ **Explainability**: Memory provides "why" for recommendations
✓ **Long-term value**: Creates lasting competitive advantage

## Consequences

**Positive:**

- Creates network effect (more data → better recommendations)
- Enables personalization at scale
- Can measure ROI of learning system
- Natural for ML optimization

**Negative:**

- Requires tracking long-term outcomes (months/years)
- Privacy considerations for tracking creator behavior
- Must handle cold-start (new creators with no history)
- Memory management complexity

## Privacy & Ethics

Important safeguards:

1. **Consent**: Collect feedback only with creator consent
2. **Transparency**: Explain how feedback is used
3. **Control**: Creators can request deletion from memory
4. **Aggregation**: Don't store individual performance metrics
5. **Fairness**: Don't let memory create feedback loops (e.g., favoring already-popular creators)

## Cold-Start Problem

For new creators without history:

1. **Default recommendations**: Use platform-wide patterns
2. **Diversity**: Suggest varied experiments
3. **Quick feedback**: Prioritize quick-win recommendations
4. **Gradual personalization**: Build memory over first 5-10 jobs
5. **Bootstrap**: Use similar-creator memories

## Future Evolution

- **ML-based prediction**: Use learning memory as ML features
- **Collaborative filtering**: Learn from similar creators
- **Causal inference**: Distinguish correlation from causation
- **Multi-armed bandit**: Optimize exploration vs. exploitation
- **Reinforcement learning**: Direct optimization of recommendations

## See Also

- M14 Learning Engine: Feedback loop implementation
- ADR-007: Capability Negotiation

## References

- M14 Phase 1: Learning Foundation (LearningMemory)
- M14 Phase 3: Learning Orchestration (ProfileUpdate, MemoryUpdate agents)
- M14 Phase 4: Production Readiness (Dashboard, monitoring)
