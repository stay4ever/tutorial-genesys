"""Topic selector — chooses the best topics to write tutorials about."""

from __future__ import annotations

import logging

from tutorial_genesys.integration.hunter_client import HunterClient, HunterTutorial

logger = logging.getLogger(__name__)


class TopicCandidate:
    """A topic evaluated for tutorial potential."""

    def __init__(
        self,
        topic: str,
        source_tutorials: list[HunterTutorial],
        avg_quality: float,
        avg_trending: float,
        tutorial_potential: float,
    ) -> None:
        self.topic = topic
        self.source_tutorials = source_tutorials
        self.avg_quality = avg_quality
        self.avg_trending = avg_trending
        self.tutorial_potential = tutorial_potential

    def __repr__(self) -> str:
        return (
            f"TopicCandidate('{self.topic}', potential={self.tutorial_potential:.1f}, "
            f"sources={len(self.source_tutorials)})"
        )


class TopicSelector:
    """Selects the best topics to generate tutorials for."""

    def __init__(self) -> None:
        self._client = HunterClient()

    async def select_topics(self, max_topics: int = 5) -> list[TopicCandidate]:
        """Analyze Hunter results and select the best tutorial candidates.

        Selection criteria:
        - High trending score (people want to learn this NOW)
        - Multiple source tutorials available (enough material to synthesize)
        - Good quality source material (better inputs = better output)
        - Topic diversity (don't write 5 tutorials on the same sub-topic)
        """
        tutorials = await self._client.get_top_tutorials(limit=100)
        if not tutorials:
            logger.warning("No tutorials from Hunter — nothing to select")
            return []

        # Group by topic
        topic_groups: dict[str, list[HunterTutorial]] = {}
        for t in tutorials:
            topic = t.topic or "general"
            topic_groups.setdefault(topic, []).append(t)

        # Score each topic
        candidates: list[TopicCandidate] = []
        for topic, group in topic_groups.items():
            avg_quality = sum(t.quality_score for t in group) / len(group)
            avg_trending = sum(t.trending_score for t in group) / len(group)

            # Tutorial potential: trending topics with enough quality source material
            source_bonus = min(2.0, len(group) / 5)  # More sources = better
            potential = (avg_trending * 0.4 + avg_quality * 0.3) * source_bonus

            candidates.append(
                TopicCandidate(
                    topic=topic,
                    source_tutorials=group,
                    avg_quality=avg_quality,
                    avg_trending=avg_trending,
                    tutorial_potential=potential,
                )
            )

        # Sort by potential, pick top N
        candidates.sort(key=lambda c: c.tutorial_potential, reverse=True)
        selected = candidates[:max_topics]

        logger.info(
            "Selected %d topics from %d candidates",
            len(selected), len(candidates),
        )
        for c in selected:
            logger.info(
                "  %s (potential=%.1f, sources=%d)",
                c.topic[:40], c.tutorial_potential, len(c.source_tutorials),
            )

        return selected
