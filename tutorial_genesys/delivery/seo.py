from __future__ import annotations
"""SEO metadata generator for tutorials."""

import json
import logging

from tutorial_genesys.config.settings import get_settings
from tutorial_genesys.config.prompts import SEO_PROMPT
from tutorial_genesys.integration.claude_cli_client import ClaudeCLIClient
from tutorial_genesys.models.tutorial_content import TutorialContent

logger = logging.getLogger(__name__)


class SEOGenerator:
    """Generates optimized SEO metadata for tutorials."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = ClaudeCLIClient()
        self._model = settings.classifier_model  # Fast model for metadata

    def generate(self, tutorial: TutorialContent) -> TutorialContent:
        """Generate and apply SEO metadata to a tutorial."""
        prompt = SEO_PROMPT.format(
            title=tutorial.title,
            topic=tutorial.topic,
            summary=tutorial.subtitle or tutorial.markdown_body[:500],
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=500,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()

            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            if "{" in text:
                text = text[text.index("{"):text.rindex("}") + 1]

            data = json.loads(text)

            tutorial.meta_title = data.get("meta_title", tutorial.title)[:60]
            tutorial.meta_description = data.get("meta_description", "")[:155]
            if data.get("keywords"):
                tutorial.keywords = list(set(tutorial.keywords + data["keywords"]))
            if data.get("slug"):
                tutorial.slug = data["slug"]

            logger.info("SEO metadata generated for '%s'", tutorial.title)

        except Exception as e:
            logger.warning("SEO generation failed: %s", e)
            if not tutorial.meta_title:
                tutorial.meta_title = tutorial.title[:60]
            if not tutorial.meta_description:
                tutorial.meta_description = tutorial.subtitle[:155]

        return tutorial
