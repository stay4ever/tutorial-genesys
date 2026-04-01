"""Publish manifest model — deployment record."""

from __future__ import annotations

from datetime import datetime, timezone

from pydantic import BaseModel, Field


class PublishManifest(BaseModel):
    tutorial_id: str
    slug: str
    title: str
    published_url: str = ""
    published_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    html_file: str = ""
    assets: list[str] = Field(default_factory=list)
    deploy_target: str = "ai-evolution.com.au"
    deploy_status: str = "pending"  # pending, deployed, failed
    seo_metadata: dict = Field(default_factory=dict)
