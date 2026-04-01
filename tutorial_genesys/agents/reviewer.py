from __future__ import annotations
"""Reviewer agent — quality checks tutorials before publication."""

import json
import logging

import anthropic

from tutorial_genesys.config.settings import get_settings
from tutorial_genesys.config.prompts import REVIEWER_PROMPT
from tutorial_genesys.models.tutorial_content import TutorialContent
from tutorial_genesys.models.review_report import ReviewReport, ReviewIssue

logger = logging.getLogger(__name__)


class Reviewer:
    """Reviews tutorials for accuracy, clarity, engagement, and SEO."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.writer_model

    def review(self, tutorial: TutorialContent) -> ReviewReport:
        """Run a comprehensive review of the tutorial."""
        logger.info("Reviewing tutorial: '%s'", tutorial.title)

        prompt = REVIEWER_PROMPT.format(
            tutorial_content=tutorial.markdown_body[:12000],
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=4096,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()

            # Extract JSON
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]
            if "{" in text:
                text = text[text.index("{"):text.rindex("}") + 1]

            data = json.loads(text)

            report = ReviewReport(
                tutorial_id=tutorial.id,
                overall_score=data.get("overall_score", 0),
                accuracy_score=data.get("accuracy_score", 0),
                clarity_score=data.get("clarity_score", 0),
                engagement_score=data.get("engagement_score", 0),
                completeness_score=data.get("completeness_score", 0),
                seo_score=data.get("seo_score", 0),
                issues=[
                    ReviewIssue(**i) for i in data.get("issues", [])
                ],
                strengths=data.get("strengths", []),
                suggested_title=data.get("suggested_title", ""),
                suggested_meta_description=data.get("suggested_meta_description", ""),
                keywords=data.get("keywords", []),
                ready_to_publish=data.get("ready_to_publish", False),
            )

            logger.info(
                "Review complete: score=%d, issues=%d, ready=%s",
                report.overall_score, len(report.issues), report.ready_to_publish,
            )
            return report

        except Exception as e:
            logger.error("Review failed: %s", e)
            return ReviewReport(
                tutorial_id=tutorial.id,
                overall_score=0,
                issues=[
                    ReviewIssue(
                        severity="critical",
                        location="review",
                        issue=f"Review agent failed: {e}",
                        fix="Retry the review",
                    )
                ],
            )

    def apply_suggestions(
        self, tutorial: TutorialContent, report: ReviewReport
    ) -> TutorialContent:
        """Apply non-content review suggestions (SEO metadata, keywords)."""
        if report.suggested_title and report.overall_score >= 70:
            tutorial.meta_title = report.suggested_title
        if report.suggested_meta_description:
            tutorial.meta_description = report.suggested_meta_description
        if report.keywords:
            tutorial.keywords = list(set(tutorial.keywords + report.keywords))

        tutorial.review_score = report.overall_score
        tutorial.ready_to_publish = report.ready_to_publish and not report.has_blockers

        return tutorial
