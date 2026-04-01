"""Tutorial content model — the full generated tutorial."""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

from pydantic import BaseModel, Field


class TutorialSection(BaseModel):
    heading: str
    level: int = 2  # h2, h3, etc.
    content_markdown: str
    has_code: bool = False
    has_challenge: bool = False
    anchor: str = ""

    def model_post_init(self, __context) -> None:
        if not self.anchor:
            self.anchor = self.heading.lower().replace(" ", "-").replace("'", "")[:50]


class TutorialContent(BaseModel):
    id: str = Field(default_factory=lambda: uuid4().hex[:12])
    topic: str
    title: str
    subtitle: str = ""
    slug: str = ""
    difficulty: str = "intermediate"
    category: str = "AI Guides"
    author: str = "The Pulse AI"
    estimated_reading_minutes: int = 15
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    published_at: datetime | None = None

    # Content
    hero_svg: str = ""
    markdown_body: str = ""
    sections: list[TutorialSection] = Field(default_factory=list)
    word_count: int = 0

    # SEO
    meta_title: str = ""
    meta_description: str = ""
    keywords: list[str] = Field(default_factory=list)
    og_image_url: str = ""

    # Quality
    review_score: float = 0.0
    ready_to_publish: bool = False

    # Source attribution
    source_tutorial_ids: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)

    def model_post_init(self, __context) -> None:
        if not self.slug:
            self.slug = self.title.lower()
            for ch in ["'", '"', "?", "!", ".", ",", ":", ";", "(", ")"]:
                self.slug = self.slug.replace(ch, "")
            self.slug = "-".join(self.slug.split())[:80]
        if self.markdown_body and not self.word_count:
            self.word_count = len(self.markdown_body.split())
