"""Knowledge builder: Create semantic knowledge graph from observations.

The KnowledgeBuilder consumes ONLY immutable Observation objects.
It does NOT:
- Access providers
- Access Memory Runtime directly
- Modify AnalysisSession
- Create side effects

It DOES:
- Build KnowledgeNode objects from observations
- Create relationships between observations
- Extract semantic entities
- Aggregate related discoveries
"""

from typing import List, Dict, Set, Optional, Any
from collections import defaultdict
from aura_backend.video.models import (
    Observation,
    ObservationType,
    KnowledgeNode,
)


class KnowledgeBuilder:
    """Build semantic knowledge graph from observations.

    Process:
    1. Group observations by type and semantic entity
    2. Extract entities (people, objects, locations)
    3. Create KnowledgeNode for each entity
    4. Link observations to nodes
    5. Track relationships
    """

    def __init__(self):
        self.nodes: Dict[str, KnowledgeNode] = {}
        self.observation_to_nodes: Dict[str, List[str]] = defaultdict(list)

    async def build_knowledge_graph(
        self,
        video_id: str,
        observations: List[Observation],
    ) -> List[KnowledgeNode]:
        """Build knowledge graph from observations.

        Args:
            video_id: Video being analyzed
            observations: All observations from analysis

        Returns:
            List of KnowledgeNode objects
        """
        nodes = []

        # Extract entities from observations
        entities = self._extract_entities(observations)

        # Create knowledge nodes for each entity
        for entity_type, entity_values in entities.items():
            for entity_label, related_obs_ids in entity_values.items():
                node = KnowledgeNode(
                    video_id=video_id,
                    node_type=entity_type,
                    label=entity_label,
                    observations=list(related_obs_ids),
                    metadata={
                        "observation_count": len(related_obs_ids),
                        "first_timestamp": self._get_first_timestamp(
                            observations, related_obs_ids
                        ),
                        "last_timestamp": self._get_last_timestamp(
                            observations, related_obs_ids
                        ),
                    },
                )
                nodes.append(node)
                self.nodes[node.id] = node

        return nodes

    def _extract_entities(
        self,
        observations: List[Observation],
    ) -> Dict[str, Dict[str, Set[str]]]:
        """Extract entities from observations.

        Returns:
            Dict[entity_type][entity_label] = set of observation IDs
        """
        entities: Dict[str, Dict[str, Set[str]]] = defaultdict(
            lambda: defaultdict(set)
        )

        for obs in observations:
            if obs.observation_type == ObservationType.SPEECH:
                # Entity: speaker
                speaker = obs.payload.get("speaker")
                if speaker:
                    entities["person"][speaker].add(obs.id)
                # Entity: language
                language = obs.payload.get("language", "unknown")
                entities["language"][language].add(obs.id)

            elif obs.observation_type == ObservationType.OBJECT:
                # Entity: object class
                obj_class = obs.payload.get("class", "unknown")
                entities["object"][obj_class].add(obs.id)

            elif obs.observation_type == ObservationType.FACE:
                # Entity: face (group faces by proximity in time)
                face_idx = obs.payload.get("face_index", 0)
                entities["face"][f"face_{face_idx}"].add(obs.id)

            elif obs.observation_type == ObservationType.LOGO:
                # Entity: brand/logo
                logo_name = obs.payload.get("name", "unknown")
                entities["brand"][logo_name].add(obs.id)

            elif obs.observation_type == ObservationType.SCENE_CONTENT:
                # Entity: scene type
                scene_desc = obs.payload.get("description", "unknown")
                entities["scene"][scene_desc].add(obs.id)

            elif obs.observation_type == ObservationType.ACTIVITY:
                # Entity: activity type
                activity = obs.payload.get("type", "unknown")
                entities["activity"][activity].add(obs.id)

        return entities

    def _get_first_timestamp(
        self,
        observations: List[Observation],
        obs_ids: List[str],
    ) -> float:
        """Get earliest timestamp for observations"""
        times = [
            obs.start_timestamp
            for obs in observations
            if obs.id in obs_ids
        ]
        return min(times) if times else 0.0

    def _get_last_timestamp(
        self,
        observations: List[Observation],
        obs_ids: List[str],
    ) -> float:
        """Get latest timestamp for observations"""
        times = [
            obs.end_timestamp
            for obs in observations
            if obs.id in obs_ids
        ]
        return max(times) if times else 0.0

    def build_observation_relationships(
        self,
        observations: List[Observation],
    ) -> Dict[str, List[str]]:
        """Build relationships between observations.

        Returns:
            Dict[obs_id] = list of related obs_ids
        """
        relationships: Dict[str, List[str]] = defaultdict(list)

        # Group observations by timestamp ranges
        by_time = defaultdict(list)
        for obs in observations:
            # Use 1-second buckets
            bucket = int(obs.start_timestamp)
            by_time[bucket].append(obs.id)

        # Observations in same time bucket are related
        for bucket, obs_ids in by_time.items():
            for obs_id in obs_ids:
                for related_id in obs_ids:
                    if obs_id != related_id:
                        relationships[obs_id].append(related_id)

        return relationships

    def get_nodes(self) -> List[KnowledgeNode]:
        """Get all built knowledge nodes"""
        return list(self.nodes.values())

    def get_entity_summary(self) -> Dict[str, Any]:
        """Get summary of extracted entities"""
        summary = {}
        for node in self.nodes.values():
            if node.node_type not in summary:
                summary[node.node_type] = []
            summary[node.node_type].append({
                "label": node.label,
                "observation_count": len(node.observations),
                "first_time": node.metadata.get("first_timestamp"),
                "last_time": node.metadata.get("last_timestamp"),
            })
        return summary
