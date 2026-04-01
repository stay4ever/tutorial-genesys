"""Illustrator agent — generates procedural SVG art and diagrams matching The Pulse aesthetic."""

from __future__ import annotations

import hashlib
import math
import logging

logger = logging.getLogger(__name__)

# The Pulse color palette
COLORS = {
    "primary": "#00c853",
    "bg_deep": "#0d1a0f",
    "bg_surface": "#132116",
    "bg_elevated": "#192b1c",
    "text": "#e8f5e9",
    "text_muted": "#81c784",
    "glow": "rgba(0,200,83,0.3)",
    "accent_blue": "#5b9cf6",
    "accent_teal": "#4ecdc4",
    "accent_orange": "#ffa62b",
}


class Illustrator:
    """Generates SVG hero images and diagrams for tutorials."""

    def generate_hero_svg(self, title: str, category: str = "AI Guides") -> str:
        """Create a procedural geometric hero SVG seeded by the title."""
        seed = int(hashlib.md5(title.encode()).hexdigest()[:8], 16)
        width, height = 1200, 400

        elements = []

        # Background gradient
        elements.append(f"""
        <defs>
            <linearGradient id="bg-grad" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" style="stop-color:{COLORS['bg_deep']}" />
                <stop offset="100%" style="stop-color:{COLORS['bg_surface']}" />
            </linearGradient>
            <filter id="glow">
                <feGaussianBlur stdDeviation="3" result="coloredBlur"/>
                <feMerge>
                    <feMergeNode in="coloredBlur"/>
                    <feMergeNode in="SourceGraphic"/>
                </feMerge>
            </filter>
        </defs>
        <rect width="{width}" height="{height}" fill="url(#bg-grad)" />
        """)

        # Geometric shapes — circles, lines, polygons
        num_shapes = 8 + (seed % 6)
        for i in range(num_shapes):
            s = (seed + i * 7919) % 10000
            x = (s * 137) % width
            y = (s * 251) % height
            r = 20 + (s % 60)
            opacity = 0.05 + (s % 15) / 100

            if i % 3 == 0:
                # Circle
                color = COLORS["primary"]
                elements.append(
                    f'<circle cx="{x}" cy="{y}" r="{r}" '
                    f'fill="none" stroke="{color}" stroke-width="1.5" opacity="{opacity}" />'
                )
            elif i % 3 == 1:
                # Hexagon
                points = " ".join(
                    f"{x + r * math.cos(math.radians(60 * j))},"
                    f"{y + r * math.sin(math.radians(60 * j))}"
                    for j in range(6)
                )
                color = COLORS["accent_teal"] if i % 2 == 0 else COLORS["primary"]
                elements.append(
                    f'<polygon points="{points}" fill="none" '
                    f'stroke="{color}" stroke-width="1" opacity="{opacity}" />'
                )
            else:
                # Connecting line
                x2 = (x + 100 + (s % 200)) % width
                y2 = (y + 50 + (s % 100)) % height
                elements.append(
                    f'<line x1="{x}" y1="{y}" x2="{x2}" y2="{y2}" '
                    f'stroke="{COLORS["primary"]}" stroke-width="0.5" opacity="{opacity}" />'
                )

        # Central glowing ring
        cx, cy = width // 2, height // 2
        elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="80" fill="none" '
            f'stroke="{COLORS["primary"]}" stroke-width="2" opacity="0.2" filter="url(#glow)" />'
        )
        elements.append(
            f'<circle cx="{cx}" cy="{cy}" r="60" fill="none" '
            f'stroke="{COLORS["primary"]}" stroke-width="1.5" opacity="0.15" />'
        )

        # Subtle grid dots
        for gx in range(0, width, 40):
            for gy in range(0, height, 40):
                elements.append(
                    f'<circle cx="{gx}" cy="{gy}" r="0.5" fill="{COLORS["primary"]}" opacity="0.08" />'
                )

        svg = f"""\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" width="{width}" height="{height}">
{"".join(elements)}
</svg>"""
        return svg

    def generate_concept_diagram(
        self, concepts: list[str], title: str = "Concept Flow"
    ) -> str:
        """Generate a simple flow diagram connecting concepts."""
        width = max(800, len(concepts) * 220)
        height = 200
        box_w, box_h = 180, 60
        gap = 40

        elements = [
            f'<rect width="{width}" height="{height}" fill="{COLORS["bg_deep"]}" rx="8" />',
        ]

        total_w = len(concepts) * box_w + (len(concepts) - 1) * gap
        start_x = (width - total_w) / 2

        for i, concept in enumerate(concepts):
            x = start_x + i * (box_w + gap)
            y = (height - box_h) / 2

            # Box
            elements.append(
                f'<rect x="{x}" y="{y}" width="{box_w}" height="{box_h}" '
                f'rx="8" fill="{COLORS["bg_elevated"]}" '
                f'stroke="{COLORS["primary"]}" stroke-width="1.5" />'
            )

            # Label
            text_x = x + box_w / 2
            text_y = y + box_h / 2 + 5
            label = concept[:20]
            elements.append(
                f'<text x="{text_x}" y="{text_y}" text-anchor="middle" '
                f'fill="{COLORS["text"]}" font-family="Inter, sans-serif" '
                f'font-size="13" font-weight="600">{label}</text>'
            )

            # Arrow to next
            if i < len(concepts) - 1:
                ax1 = x + box_w
                ax2 = ax1 + gap
                ay = height / 2
                elements.append(
                    f'<line x1="{ax1}" y1="{ay}" x2="{ax2 - 8}" y2="{ay}" '
                    f'stroke="{COLORS["primary"]}" stroke-width="2" />'
                )
                elements.append(
                    f'<polygon points="{ax2 - 8},{ay - 5} {ax2},{ay} {ax2 - 8},{ay + 5}" '
                    f'fill="{COLORS["primary"]}" />'
                )

        return (
            f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" '
            f'width="{width}" height="{height}">{"".join(elements)}</svg>'
        )
