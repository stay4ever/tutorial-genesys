"""Client for reading Tutorial Hunter pipeline results."""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from pathlib import Path

import httpx

from tutorial_genesys.config.settings import get_settings

logger = logging.getLogger(__name__)


@dataclass
class HunterTutorial:
    """Simplified tutorial data from Tutorial Hunter."""
    id: str
    title: str
    url: str
    source: str
    author: str
    topic: str
    difficulty: str
    content_type: str
    summary: str
    quality_score: float
    trending_score: float
    final_rank: float
    tags: list[str]
    engagement: dict


@dataclass
class HunterTrend:
    """Simplified trend data from Tutorial Hunter."""
    topic: str
    query: str
    velocity: float
    volume: int
    sources: list[str]
    category: str


class HunterClient:
    """Reads Tutorial Hunter output via API or direct DB access."""

    def __init__(self) -> None:
        self._settings = get_settings()

    async def get_top_tutorials(self, limit: int = 20) -> list[HunterTutorial]:
        """Fetch top-ranked tutorials from Tutorial Hunter API."""
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                resp = await client.get(
                    f"{self._settings.hunter_api_url}/api/tutorials",
                    params={"limit": limit},
                )
                if resp.status_code == 200:
                    data = resp.json()
                    return [
                        HunterTutorial(
                            id=t.get("id", ""),
                            title=t.get("title", ""),
                            url=t.get("url", ""),
                            source=t.get("source", ""),
                            author=t.get("author", ""),
                            topic=t.get("topic", ""),
                            difficulty=t.get("difficulty", "intermediate"),
                            content_type=t.get("content_type", "article"),
                            summary=t.get("summary", ""),
                            quality_score=t.get("quality_score", 0),
                            trending_score=t.get("trending_score", 0),
                            final_rank=t.get("final_rank", 0),
                            tags=t.get("tags", []),
                            engagement=t.get("engagement", {}),
                        )
                        for t in data.get("tutorials", [])
                    ]
        except Exception as e:
            logger.warning("Hunter API unavailable (%s), trying DB fallback", e)

        return self._read_from_db(limit)

    def _read_from_db(self, limit: int) -> list[HunterTutorial]:
        """Fallback: read directly from Tutorial Hunter's SQLite database."""
        db_path = Path(self._settings.hunter_db_path)
        if not db_path.exists():
            logger.error("Hunter DB not found at %s", db_path)
            return []

        import sqlite3

        conn = sqlite3.connect(str(db_path))
        conn.row_factory = sqlite3.Row
        rows = conn.execute(
            "SELECT * FROM tutorials ORDER BY final_rank DESC LIMIT ?",
            (limit,),
        ).fetchall()
        conn.close()

        tutorials = []
        for r in rows:
            tutorials.append(
                HunterTutorial(
                    id=r["id"],
                    title=r["title"],
                    url=r["url"],
                    source=r["source"],
                    author=r["author"] or "",
                    topic=r["topic"] or "",
                    difficulty=r["difficulty"] or "intermediate",
                    content_type=r["content_type"] or "article",
                    summary=r["summary"] or "",
                    quality_score=r["quality_score"] or 0,
                    trending_score=r["trending_score"] or 0,
                    final_rank=r["final_rank"] or 0,
                    tags=json.loads(r["tags_json"] or "[]"),
                    engagement=json.loads(r["engagement_json"] or "{}"),
                )
            )
        return tutorials

    async def get_trending_topics(self, limit: int = 10) -> list[str]:
        """Get the top trending topic names."""
        tutorials = await self.get_top_tutorials(limit=50)
        topics: dict[str, float] = {}
        for t in tutorials:
            if t.topic:
                topics[t.topic] = topics.get(t.topic, 0) + t.final_rank
        sorted_topics = sorted(topics.items(), key=lambda x: x[1], reverse=True)
        return [topic for topic, _ in sorted_topics[:limit]]
