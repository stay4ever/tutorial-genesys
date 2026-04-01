from __future__ import annotations
"""Publisher agent — renders final HTML and deploys to ai-evolution.com.au."""

import logging
from pathlib import Path

import httpx
import mistune

from tutorial_genesys.config.settings import get_settings
from tutorial_genesys.models.tutorial_content import TutorialContent, TutorialSection
from tutorial_genesys.models.publish_manifest import PublishManifest
from tutorial_genesys.agents.illustrator import Illustrator
from tutorial_genesys.delivery.renderer import render_tutorial

logger = logging.getLogger(__name__)

_md = mistune.create_markdown()


class Publisher:
    """Renders tutorials to HTML and deploys them to ai-evolution.com.au."""

    def __init__(self) -> None:
        self._settings = get_settings()
        self._illustrator = Illustrator()

    def render(self, tutorial: TutorialContent) -> str:
        """Render tutorial to full HTML page using The Pulse templates."""
        if not tutorial.hero_svg:
            tutorial.hero_svg = self._illustrator.generate_hero_svg(
                tutorial.title, tutorial.category,
            )

        concept_names = [s.heading for s in tutorial.sections[:6] if s.level == 2]
        concept_diagram = ""
        if len(concept_names) >= 3:
            concept_diagram = self._illustrator.generate_concept_diagram(concept_names)

        return render_tutorial(tutorial, concept_diagram=concept_diagram)

    def save_local(self, tutorial: TutorialContent, html: str) -> PublishManifest:
        """Save rendered tutorial to local output directory."""
        output_dir = self._settings.output_path / tutorial.slug
        output_dir.mkdir(parents=True, exist_ok=True)

        (output_dir / "index.html").write_text(html, encoding="utf-8")
        if tutorial.hero_svg:
            (output_dir / "hero.svg").write_text(tutorial.hero_svg, encoding="utf-8")
        (output_dir / "tutorial.md").write_text(tutorial.markdown_body, encoding="utf-8")
        (output_dir / "meta.json").write_text(
            tutorial.model_dump_json(indent=2, exclude={"hero_svg", "markdown_body"}),
            encoding="utf-8",
        )

        manifest = PublishManifest(
            tutorial_id=tutorial.id,
            slug=tutorial.slug,
            title=tutorial.title,
            html_file=str(output_dir / "index.html"),
            assets=[str(p) for p in output_dir.iterdir()],
            deploy_status="saved_locally",
        )
        logger.info("Tutorial saved to %s", output_dir)
        return manifest

    def deploy_to_pulse(self, tutorial: TutorialContent, html: str) -> PublishManifest:
        """Save locally then deploy to ai-evolution.com.au via the pipeline REST API.

        Endpoint: POST /api/tutorials/bulk-publish/
        Auth:     Authorization: Bearer <PULSE_API_KEY>

        Converts H2 sections → TutorialLesson objects so the Academy page shows
        individual lessons with XP and optional quiz data.
        """
        manifest = self.save_local(tutorial, html)

        if not self._settings.pulse_api_key:
            logger.warning("PULSE_API_KEY not set — tutorial saved locally only")
            manifest.deploy_status = "skipped_no_api_key"
            return manifest

        lessons = self._sections_to_lessons(tutorial)
        xp_total = sum(l["xp_reward"] for l in lessons)

        payload = {
            "title": tutorial.title,
            "slug": tutorial.slug,
            "subtitle": tutorial.subtitle or "",
            "description": tutorial.meta_description or f"A comprehensive guide to {tutorial.topic}.",
            "content_html": html,
            "hero_svg": tutorial.hero_svg or "",
            "category": tutorial.category or "AI Guides",
            "difficulty": tutorial.difficulty or "intermediate",
            "is_free": True,
            "xp_total": xp_total,
            "meta_title": tutorial.meta_title or tutorial.title[:60],
            "meta_description": tutorial.meta_description or "",
            "keywords": tutorial.keywords or [],
            "author": tutorial.author or self._settings.pulse_author_name,
            "estimated_reading_minutes": tutorial.estimated_reading_minutes or 10,
            "source_data": {"source_urls": tutorial.source_urls},
            "lessons": lessons,
        }

        url = f"{self._settings.pulse_api_url}/tutorials/bulk-publish/"
        headers = {
            "Authorization": f"Bearer {self._settings.pulse_api_key}",
            "Content-Type": "application/json",
        }

        try:
            resp = httpx.post(url, headers=headers, json={"tutorials": [payload]}, timeout=60.0)
            if resp.status_code in (200, 201):
                data = resp.json()
                result = (data.get("results") or [{}])[0]
                manifest.deploy_status = "deployed"
                manifest.published_url = (
                    f"{self._settings.pulse_api_url.replace('/api', '')}"
                    f"/academy/{tutorial.slug}/"
                )
                logger.info(
                    "Deployed '%s' → %s (status=%s, lessons=%d, xp=%d)",
                    tutorial.title,
                    manifest.published_url,
                    result.get("status", "?"),
                    len(lessons),
                    xp_total,
                )
            else:
                manifest.deploy_status = f"failed_{resp.status_code}"
                logger.error(
                    "Deploy failed for '%s': %s — %s",
                    tutorial.title, resp.status_code, resp.text[:300],
                )
        except Exception as exc:
            manifest.deploy_status = f"error: {exc}"
            logger.error("Deploy error for '%s': %s", tutorial.title, exc)

        return manifest

    # ── Internal helpers ─────────────────────────────────────────────────

    def _sections_to_lessons(self, tutorial: TutorialContent) -> list[dict]:
        """Convert H2 tutorial sections into lesson dicts for the Django API.

        Each H2 heading becomes one lesson.  The section's markdown is rendered
        to HTML inline.  XP is higher for code-heavy sections.
        """
        h2_sections = [s for s in tutorial.sections if s.level == 2]

        if not h2_sections:
            # Fallback: single lesson wrapping the whole tutorial
            return [{
                "title": tutorial.title,
                "subtitle": tutorial.subtitle or "",
                "content_html": _md(tutorial.markdown_body),
                "xp_reward": 75,
                "quiz_data": None,
            }]

        lessons = []
        for section in h2_sections:
            content_html = _md(section.content_markdown) if section.content_markdown else ""
            xp = 100 if section.has_code else (80 if section.has_challenge else 60)
            lessons.append({
                "title": section.heading,
                "subtitle": "",
                "content_html": content_html,
                "xp_reward": xp,
                "quiz_data": None,
            })

        return lessons

    # Keep the async variant for backwards compatibility / future use
    async def deploy_to_pulse_async(self, tutorial: TutorialContent, html: str) -> PublishManifest:
        """Async wrapper — delegates to the sync deploy_to_pulse."""
        return self.deploy_to_pulse(tutorial, html)
