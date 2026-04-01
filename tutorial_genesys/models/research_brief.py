"""Research brief model — output of the Researcher agent."""

from __future__ import annotations

from pydantic import BaseModel, Field


class RealWorldExample(BaseModel):
    company_or_industry: str
    use_case: str
    impact: str


class CodeExample(BaseModel):
    language: str = "python"
    description: str
    code: str


class Concept(BaseModel):
    name: str
    explanation: str
    analogy: str = ""
    real_world_example: RealWorldExample | None = None
    code_example: CodeExample | None = None


class HandsOnProject(BaseModel):
    title: str
    description: str
    steps: list[str] = Field(default_factory=list)
    full_code: str = ""
    expected_output: str = ""


class FAQ(BaseModel):
    question: str
    answer: str


class ResearchBrief(BaseModel):
    topic: str
    title: str
    subtitle: str = ""
    difficulty: str = "intermediate"
    estimated_reading_minutes: int = 15
    prerequisites: list[str] = Field(default_factory=list)
    learning_objectives: list[str] = Field(default_factory=list)
    concepts: list[Concept] = Field(default_factory=list)
    hands_on_project: HandsOnProject | None = None
    common_mistakes: list[str] = Field(default_factory=list)
    faq: list[FAQ] = Field(default_factory=list)
    related_topics: list[str] = Field(default_factory=list)
    source_urls: list[str] = Field(default_factory=list)
