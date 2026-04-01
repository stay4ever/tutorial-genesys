"""Writer agent — transforms research briefs into complete, engaging tutorials."""

from __future__ import annotations

import logging
import re

import anthropic

from tutorial_genesys.config.settings import get_settings
from tutorial_genesys.config.prompts import WRITER_PROMPT
from tutorial_genesys.models.research_brief import ResearchBrief
from tutorial_genesys.models.tutorial_content import TutorialContent, TutorialSection

logger = logging.getLogger(__name__)


class Writer:
    """Uses Claude to write complete tutorials from research briefs."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = anthropic.Anthropic(api_key=settings.anthropic_api_key)
        self._model = settings.writer_model
        self._min_words = settings.min_tutorial_words
        self._max_words = settings.max_tutorial_words

    def write(self, brief: ResearchBrief) -> TutorialContent:
        """Generate a complete tutorial from a research brief."""
        logger.info("Writing tutorial: '%s'", brief.title)

        prompt = WRITER_PROMPT.format(
            research_brief=brief.model_dump_json(indent=2),
            min_words=self._min_words,
            max_words=self._max_words,
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            markdown = response.content[0].text.strip()

            # Parse sections from markdown
            sections = self._parse_sections(markdown)
            word_count = len(markdown.split())

            tutorial = TutorialContent(
                topic=brief.topic,
                title=brief.title,
                subtitle=brief.subtitle,
                difficulty=brief.difficulty,
                estimated_reading_minutes=brief.estimated_reading_minutes,
                markdown_body=markdown,
                sections=sections,
                word_count=word_count,
                keywords=brief.related_topics,
                source_urls=brief.source_urls,
            )

            logger.info(
                "Tutorial written: %d words, %d sections",
                word_count, len(sections),
            )

            if word_count < self._min_words:
                logger.warning(
                    "Tutorial is short (%d words, min %d). Consider regenerating.",
                    word_count, self._min_words,
                )

            return tutorial

        except Exception as e:
            logger.error("Writing failed: %s", e)
            return TutorialContent(
                topic=brief.topic,
                title=brief.title,
                subtitle=brief.subtitle,
                markdown_body=f"# {brief.title}\n\n*Generation failed. Please retry.*",
            )

    def _parse_sections(self, markdown: str) -> list[TutorialSection]:
        """Extract sections from markdown headings."""
        sections: list[TutorialSection] = []
        heading_pattern = re.compile(r"^(#{2,4})\s+(.+)$", re.MULTILINE)

        matches = list(heading_pattern.finditer(markdown))
        for i, match in enumerate(matches):
            level = len(match.group(1))
            heading = match.group(2).strip()
            start = match.end()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(markdown)
            content = markdown[start:end].strip()

            sections.append(
                TutorialSection(
                    heading=heading,
                    level=level,
                    content_markdown=content,
                    has_code="```" in content,
                    has_challenge="try it yourself" in content.lower()
                    or "challenge" in content.lower(),
                )
            )

        return sections
