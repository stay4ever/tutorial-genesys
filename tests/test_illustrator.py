"""Tests for the illustrator agent."""

from tutorial_genesys.agents.illustrator import Illustrator


class TestIllustrator:
    def setup_method(self):
        self.illustrator = Illustrator()

    def test_hero_svg_generation(self):
        svg = self.illustrator.generate_hero_svg("Building AI Agents")
        assert svg.startswith("<svg")
        assert "xmlns" in svg
        assert "#00c853" in svg  # Pulse green
        assert "</svg>" in svg

    def test_hero_svg_deterministic(self):
        svg1 = self.illustrator.generate_hero_svg("Same Title")
        svg2 = self.illustrator.generate_hero_svg("Same Title")
        assert svg1 == svg2

    def test_hero_svg_unique_per_title(self):
        svg1 = self.illustrator.generate_hero_svg("Title One")
        svg2 = self.illustrator.generate_hero_svg("Title Two")
        assert svg1 != svg2

    def test_concept_diagram(self):
        concepts = ["Retrieval", "Augmentation", "Generation"]
        svg = self.illustrator.generate_concept_diagram(concepts)
        assert "<svg" in svg
        assert "Retrieval" in svg
        assert "Generation" in svg

    def test_concept_diagram_has_arrows(self):
        concepts = ["A", "B", "C"]
        svg = self.illustrator.generate_concept_diagram(concepts)
        assert "polygon" in svg  # Arrow heads
