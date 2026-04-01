"""Review report model — output of the Reviewer agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class ReviewIssue(BaseModel):
    severity: str  # critical, warning, suggestion
    location: str
    issue: str
    fix: str


class ReviewReport(BaseModel):
    tutorial_id: str
    overall_score: float = 0.0
    accuracy_score: float = 0.0
    clarity_score: float = 0.0
    engagement_score: float = 0.0
    completeness_score: float = 0.0
    seo_score: float = 0.0
    issues: list[ReviewIssue] = Field(default_factory=list)
    strengths: list[str] = Field(default_factory=list)
    suggested_title: str = ""
    suggested_meta_description: str = ""
    keywords: list[str] = Field(default_factory=list)
    ready_to_publish: bool = False

    @property
    def critical_issues(self) -> list[ReviewIssue]:
        return [i for i in self.issues if i.severity == "critical"]

    @property
    def has_blockers(self) -> bool:
        return len(self.critical_issues) > 0
