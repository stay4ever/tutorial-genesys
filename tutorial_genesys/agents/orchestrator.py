"""Orchestrator — coordinates the full tutorial generation pipeline."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field

from tutorial_genesys.agents.researcher import Researcher
from tutorial_genesys.agents.writer import Writer
from tutorial_genesys.agents.illustrator import Illustrator
from tutorial_genesys.agents.reviewer import Reviewer
from tutorial_genesys.agents.publisher import Publisher
from tutorial_genesys.integration.topic_selector import TopicSelector, TopicCandidate
from tutorial_genesys.integration.hunter_client import HunterTutorial
from tutorial_genesys.models.tutorial_content import TutorialContent
from tutorial_genesys.models.research_brief import ResearchBrief
from tutorial_genesys.models.review_report import ReviewReport
from tutorial_genesys.models.publish_manifest import PublishManifest

logger = logging.getLogger(__name__)


@dataclass
class GenerationResult:
    """Result of a single tutorial generation."""
    topic: str
    brief: ResearchBrief | None = None
    tutorial: TutorialContent | None = None
    review: ReviewReport | None = None
    manifest: PublishManifest | None = None
    success: bool = False
    error: str = ""


@dataclass
class PipelineResult:
    """Result of a full pipeline run."""
    results: list[GenerationResult] = field(default_factory=list)

    @property
    def successful(self) -> list[GenerationResult]:
        return [r for r in self.results if r.success]

    @property
    def failed(self) -> list[GenerationResult]:
        return [r for r in self.results if not r.success]


class Orchestrator:
    """Runs the full tutorial generation pipeline."""

    def __init__(self) -> None:
        self.topic_selector = TopicSelector()
        self.researcher = Researcher()
        self.writer = Writer()
        self.illustrator = Illustrator()
        self.reviewer = Reviewer()
        self.publisher = Publisher()

    async def run(self, max_tutorials: int = 3, deploy: bool = False) -> PipelineResult:
        """Execute the full pipeline: select → research → write → review → publish.

        1. Select top topics from Tutorial Hunter
        2. For each topic: research → write → review → publish
        3. Only publish if review score >= 70
        4. Auto-deploy to ai-evolution.com.au when PULSE_API_KEY is configured
        """
        from tutorial_genesys.config.settings import get_settings
        if not deploy and get_settings().pulse_api_key:
            deploy = True
            logger.info("PULSE_API_KEY detected — production deployment enabled")
        logger.info("=== Tutorial Genesys Pipeline Starting ===")
        logger.info("Deploy mode: %s", "ON" if deploy else "OFF (local only)")
        pipeline_result = PipelineResult()

        # Step 1: Select topics
        logger.info("Step 1: Selecting topics from Tutorial Hunter...")
        candidates = await self.topic_selector.select_topics(max_topics=max_tutorials)
        if not candidates:
            logger.warning("No topics selected. Pipeline ending early.")
            return pipeline_result

        # Step 2-5: Generate each tutorial
        for i, candidate in enumerate(candidates, 1):
            logger.info(
                "=== Generating tutorial %d/%d: %s ===",
                i, len(candidates), candidate.topic[:50],
            )
            result = self._generate_one(candidate, deploy=deploy)
            pipeline_result.results.append(result)

        logger.info(
            "=== Pipeline Complete: %d successful, %d failed ===",
            len(pipeline_result.successful), len(pipeline_result.failed),
        )
        return pipeline_result

    def _generate_one(
        self, candidate: TopicCandidate, deploy: bool = False
    ) -> GenerationResult:
        """Generate a single tutorial through all stages."""
        result = GenerationResult(topic=candidate.topic)

        try:
            # Research
            logger.info("  [1/4] Researching...")
            brief = self.researcher.research(
                topic=candidate.topic,
                source_tutorials=candidate.source_tutorials,
            )
            result.brief = brief

            if not brief.concepts:
                result.error = "Research produced no concepts"
                logger.warning("  Research failed: no concepts")
                return result

            # Write
            logger.info("  [2/4] Writing tutorial...")
            tutorial = self.writer.write(brief)
            result.tutorial = tutorial

            if tutorial.word_count < 500:
                result.error = f"Tutorial too short ({tutorial.word_count} words)"
                logger.warning("  Writing failed: too short")
                return result

            # Review
            logger.info("  [3/4] Reviewing...")
            review = self.reviewer.review(tutorial)
            result.review = review
            tutorial = self.reviewer.apply_suggestions(tutorial, review)

            # Publish
            logger.info("  [4/4] Publishing...")
            html = self.publisher.render(tutorial)
            if deploy:
                manifest = self.publisher.deploy_to_pulse(tutorial, html)
            else:
                manifest = self.publisher.save_local(tutorial, html)
            result.manifest = manifest

            if review.overall_score >= 70:
                result.success = True
                logger.info(
                    "  Tutorial generated successfully: '%s' (score: %d, deploy: %s)",
                    tutorial.title, review.overall_score, manifest.deploy_status,
                )
            else:
                result.error = f"Review score too low ({review.overall_score})"
                logger.warning(
                    "  Tutorial below quality threshold: score=%d",
                    review.overall_score,
                )

        except Exception as e:
            result.error = str(e)
            logger.error("  Generation failed: %s", e)

        return result

    async def generate_single(
        self,
        topic: str,
        source_tutorials: list[HunterTutorial] | None = None,
        deploy: bool = False,
    ) -> GenerationResult:
        """Generate a single tutorial for a specific topic."""
        from tutorial_genesys.integration.hunter_client import HunterClient

        if source_tutorials is None:
            client = HunterClient()
            all_tutorials = await client.get_top_tutorials(limit=50)
            source_tutorials = [
                t for t in all_tutorials if topic.lower() in t.topic.lower()
            ]

        candidate = TopicCandidate(
            topic=topic,
            source_tutorials=source_tutorials or [],
            avg_quality=0,
            avg_trending=0,
            tutorial_potential=0,
        )
        return self._generate_one(candidate, deploy=deploy)
