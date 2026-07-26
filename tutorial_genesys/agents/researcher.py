"""Researcher agent — deep-dives into a topic and produces a structured teaching brief."""

from __future__ import annotations

import json
import logging

from tutorial_genesys.config.settings import get_settings
from tutorial_genesys.config.prompts import RESEARCHER_PROMPT
from tutorial_genesys.integration.claude_cli_client import ClaudeCLIClient
from tutorial_genesys.integration.hunter_client import HunterTutorial
from tutorial_genesys.models.research_brief import ResearchBrief

logger = logging.getLogger(__name__)


class Researcher:
    """Uses Claude to research a topic and produce a comprehensive teaching brief."""

    def __init__(self) -> None:
        settings = get_settings()
        self._client = ClaudeCLIClient()
        self._model = settings.writer_model  # Use best model for research

    def research(
        self,
        topic: str,
        source_tutorials: list[HunterTutorial],
    ) -> ResearchBrief:
        """Research a topic using source tutorials and LLM analysis."""
        logger.info("Researching topic: %s (%d sources)", topic, len(source_tutorials))

        # Build source summaries
        summaries = []
        source_urls = []
        for t in source_tutorials[:10]:
            summaries.append(
                f"- [{t.source}] \"{t.title}\" by {t.author or 'Unknown'}\n"
                f"  Score: {t.quality_score:.0f} | Trending: {t.trending_score:.0f}\n"
                f"  Summary: {t.summary[:200]}\n"
                f"  URL: {t.url}"
            )
            source_urls.append(t.url)

        prompt = RESEARCHER_PROMPT.format(
            topic=topic,
            source_summaries="\n".join(summaries) if summaries else "No source tutorials available.",
        )

        try:
            response = self._client.messages.create(
                model=self._model,
                max_tokens=16000,
                messages=[{"role": "user", "content": prompt}],
            )
            text = response.content[0].text.strip()

            # Extract JSON from code fences if present
            if "```json" in text:
                text = text.split("```json")[1].split("```")[0]
            elif "```" in text:
                text = text.split("```")[1].split("```")[0]

            # Isolate the JSON object
            if "{" in text:
                start = text.index("{")
                try:
                    end = text.rindex("}") + 1
                    text = text[start:end]
                except ValueError:
                    # Truncated response — trim to last complete key/value pair
                    text = text[start:]
                    open_braces = text.count("{") - text.count("}")
                    open_brackets = text.count("[") - text.count("]")
                    # Cut off any incomplete trailing token
                    last_safe = max(text.rfind(","), text.rfind("}"), text.rfind("]"))
                    if last_safe > 0:
                        text = text[:last_safe + 1]
                    text += "]" * max(0, open_brackets) + "}" * max(0, open_braces)
                    logger.warning(
                        "Repaired truncated JSON (added %d braces, %d brackets)",
                        open_braces, open_brackets,
                    )

            data = json.loads(text)
            brief = ResearchBrief(**data)
            brief.source_urls = source_urls
            logger.info(
                "Research complete: '%s' — %d concepts, %d FAQs",
                brief.title, len(brief.concepts), len(brief.faq),
            )
            return brief

        except json.JSONDecodeError as e:
            logger.error("Failed to parse research response as JSON: %s", e)
            from tutorial_genesys.models.research_brief import Concept, RealWorldExample, CodeExample
            return ResearchBrief(
                topic=topic,
                title=f"Understanding {topic}",
                subtitle=f"A comprehensive guide to {topic}",
                source_urls=source_urls,
                concepts=[Concept(
                    name=topic,
                    explanation=f"An exploration of {topic} and its impact on AI development.",
                    analogy="Think of it as a new tool in your developer toolkit.",
                    real_world_example=RealWorldExample(
                        company_or_industry="AI industry",
                        use_case=f"Applying {topic} to real-world AI workflows",
                        impact="Improved productivity and developer experience",
                    ),
                    code_example=CodeExample(
                        language="python",
                        description=f"Basic example related to {topic}",
                        code="# Example coming soon\nprint('Hello from the AI world!')",
                    ),
                )],
            )
        except Exception as e:
            logger.error("Research failed: %s", e)
            return ResearchBrief(
                topic=topic,
                title=f"Understanding {topic}",
                source_urls=source_urls,
            )
