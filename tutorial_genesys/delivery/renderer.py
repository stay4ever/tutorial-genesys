"""Renderer — converts tutorial markdown to styled HTML using The Pulse templates."""

from __future__ import annotations

import re
import logging
from pathlib import Path

import mistune
from jinja2 import Template
from pygments import highlight
from pygments.lexers import get_lexer_by_name, TextLexer
from pygments.formatters import HtmlFormatter

from tutorial_genesys.models.tutorial_content import TutorialContent

logger = logging.getLogger(__name__)

TEMPLATE_DIR = Path(__file__).parent.parent / "templates"
STYLES_DIR = TEMPLATE_DIR / "styles"


class PulseCodeRenderer(mistune.HTMLRenderer):
    """Custom mistune renderer with Pulse-styled code blocks and callouts."""

    def block_code(self, code: str, info: str | None = None, **attrs) -> str:
        lang = info or "text"
        try:
            lexer = get_lexer_by_name(lang, stripall=True)
        except Exception:
            lexer = TextLexer(stripall=True)

        formatter = HtmlFormatter(
            nowrap=True,
            style="monokai",
        )
        highlighted = highlight(code, lexer, formatter)

        return (
            f'<div class="code-block">'
            f'<div class="code-block-header"><span>{lang}</span></div>'
            f'<pre><code>{highlighted}</code></pre>'
            f'</div>\n'
        )

    def codespan(self, text: str, **attrs) -> str:
        return f'<code>{mistune.html(text)}</code>'

    def blockquote(self, text: str, **attrs) -> str:
        # Detect callout type from content
        callout_type = "tip"
        title = "Tip"
        lower = text.lower()
        if "warning" in lower or "caution" in lower:
            callout_type = "warning"
            title = "Warning"
        elif "note" in lower or "info" in lower:
            callout_type = "info"
            title = "Note"

        return (
            f'<div class="callout callout-{callout_type}">'
            f'<div class="callout-title">{title}</div>'
            f'{text}'
            f'</div>\n'
        )

    def heading(self, text: str, level: int, **attrs) -> str:
        anchor = text.lower().strip()
        for ch in ["'", '"', "?", "!", ".", ",", ":", ";", "(", ")"]:
            anchor = anchor.replace(ch, "")
        anchor = re.sub(r"\s+", "-", anchor)[:60]
        return f'<h{level} id="{anchor}">{text}</h{level}>\n'


def _inject_challenges(html: str) -> str:
    """Wrap 'Try It Yourself' sections in challenge boxes."""
    pattern = re.compile(
        r'<h[34][^>]*>([^<]*(?:Try It Yourself|Challenge)[^<]*)</h[34]>\s*'
        r'((?:(?!<h[234]).)*)',
        re.DOTALL | re.IGNORECASE,
    )

    def replace_challenge(match):
        heading = match.group(1)
        content = match.group(2)
        return (
            f'<div class="challenge">'
            f'<span class="challenge-label">Try It Yourself</span>'
            f'<h4>{heading}</h4>'
            f'{content}'
            f'</div>'
        )

    return pattern.sub(replace_challenge, html)


def render_tutorial(
    tutorial: TutorialContent,
    concept_diagram: str = "",
) -> str:
    """Render a TutorialContent object to a complete HTML page."""
    # Load CSS
    css_path = STYLES_DIR / "pulse.css"
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""

    # Parse markdown to HTML
    renderer = PulseCodeRenderer()
    markdown_parser = mistune.create_markdown(renderer=renderer)
    content_html = markdown_parser(tutorial.markdown_body)

    # Post-process: inject challenge boxes
    content_html = _inject_challenges(content_html)

    # Build TOC items from sections
    toc_items = [
        {"heading": s.heading, "anchor": s.anchor}
        for s in tutorial.sections
        if s.level == 2
    ]

    # Load and render Jinja template
    template_path = TEMPLATE_DIR / "tutorial.html"
    template_str = template_path.read_text(encoding="utf-8")
    template = Template(template_str)

    html = template.render(
        title=tutorial.title,
        subtitle=tutorial.subtitle,
        slug=tutorial.slug,
        meta_title=tutorial.meta_title or tutorial.title,
        meta_description=tutorial.meta_description or tutorial.subtitle,
        keywords=tutorial.keywords,
        author=tutorial.author,
        category=tutorial.category,
        difficulty=tutorial.difficulty,
        estimated_reading_minutes=tutorial.estimated_reading_minutes,
        created_at=tutorial.created_at.isoformat(),
        hero_svg=tutorial.hero_svg,
        toc_items=toc_items,
        concept_diagram=concept_diagram,
        content_html=content_html,
        css=css,
    )

    logger.info(
        "Rendered tutorial '%s': %d chars HTML",
        tutorial.title, len(html),
    )
    return html
