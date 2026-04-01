"""Tests for the tutorial renderer."""

from tutorial_genesys.models.tutorial_content import TutorialContent, TutorialSection
from tutorial_genesys.delivery.renderer import render_tutorial


class TestRenderer:
    def test_basic_render(self):
        tutorial = TutorialContent(
            topic="RAG",
            title="Building RAG Systems",
            subtitle="A hands-on guide",
            markdown_body="## Introduction\n\nThis is a tutorial about RAG.\n\n## Setup\n\nInstall the deps.",
            sections=[
                TutorialSection(heading="Introduction", content_markdown="This is a tutorial about RAG."),
                TutorialSection(heading="Setup", content_markdown="Install the deps."),
            ],
        )
        html = render_tutorial(tutorial)
        assert "Building RAG Systems" in html
        assert "The Pulse" in html
        assert "pulse-green" in html or "#00c853" in html

    def test_code_blocks_rendered(self):
        tutorial = TutorialContent(
            topic="Python",
            title="Python Basics",
            markdown_body='## Code\n\n```python\nprint("hello")\n```\n',
            sections=[],
        )
        html = render_tutorial(tutorial)
        assert "code-block" in html
        assert "python" in html

    def test_seo_metadata(self):
        tutorial = TutorialContent(
            topic="AI",
            title="AI Guide",
            meta_title="Learn AI Fast",
            meta_description="A quick guide to AI",
            keywords=["ai", "machine learning"],
        )
        html = render_tutorial(tutorial)
        assert "Learn AI Fast" in html
        assert "A quick guide to AI" in html

    def test_toc_generation(self):
        tutorial = TutorialContent(
            topic="test",
            title="Test",
            markdown_body="## One\n\nContent\n\n## Two\n\nMore",
            sections=[
                TutorialSection(heading="One", content_markdown="Content"),
                TutorialSection(heading="Two", content_markdown="More"),
            ],
        )
        html = render_tutorial(tutorial)
        assert "In This Tutorial" in html
