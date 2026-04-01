"""Tests for tutorial-genesys data models."""

from tutorial_genesys.models.tutorial_content import TutorialContent, TutorialSection
from tutorial_genesys.models.research_brief import ResearchBrief, Concept, RealWorldExample
from tutorial_genesys.models.review_report import ReviewReport, ReviewIssue
from tutorial_genesys.models.publish_manifest import PublishManifest


class TestTutorialContent:
    def test_auto_slug(self):
        t = TutorialContent(topic="RAG", title="Building RAG Systems: A Complete Guide")
        assert "building-rag-systems" in t.slug
        assert "'" not in t.slug

    def test_word_count_from_body(self):
        t = TutorialContent(
            topic="test",
            title="Test",
            markdown_body="word " * 500,
        )
        assert t.word_count == 500

    def test_auto_id(self):
        t1 = TutorialContent(topic="a", title="A")
        t2 = TutorialContent(topic="b", title="B")
        assert t1.id != t2.id


class TestTutorialSection:
    def test_auto_anchor(self):
        s = TutorialSection(heading="What You'll Learn", content_markdown="stuff")
        assert s.anchor == "what-youll-learn"

    def test_has_code_detection(self):
        s = TutorialSection(
            heading="Code",
            content_markdown="```python\nprint('hi')\n```",
            has_code=True,
        )
        assert s.has_code is True


class TestResearchBrief:
    def test_with_concepts(self):
        brief = ResearchBrief(
            topic="RAG",
            title="Understanding RAG",
            concepts=[
                Concept(
                    name="Retrieval",
                    explanation="Finding relevant docs",
                    real_world_example=RealWorldExample(
                        company_or_industry="Healthcare",
                        use_case="Medical record search",
                        impact="50% faster diagnosis",
                    ),
                )
            ],
        )
        assert len(brief.concepts) == 1
        assert brief.concepts[0].real_world_example.company_or_industry == "Healthcare"

    def test_defaults(self):
        brief = ResearchBrief(topic="test", title="Test")
        assert brief.difficulty == "intermediate"
        assert brief.prerequisites == []


class TestReviewReport:
    def test_critical_issues(self):
        report = ReviewReport(
            tutorial_id="abc",
            issues=[
                ReviewIssue(severity="critical", location="intro", issue="Missing", fix="Add it"),
                ReviewIssue(severity="warning", location="code", issue="Outdated", fix="Update"),
            ],
        )
        assert len(report.critical_issues) == 1
        assert report.has_blockers is True

    def test_no_blockers(self):
        report = ReviewReport(
            tutorial_id="abc",
            overall_score=85,
            issues=[
                ReviewIssue(severity="suggestion", location="seo", issue="Add keywords", fix="Add"),
            ],
        )
        assert report.has_blockers is False


class TestPublishManifest:
    def test_default_status(self):
        m = PublishManifest(tutorial_id="abc", slug="test", title="Test")
        assert m.deploy_status == "pending"
