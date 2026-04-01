# Tutorial Genesys

## Project Overview

**Tutorial Genesys** is an agentic AI content-generation engine that transforms trending AI topic intelligence from [AI Tutorial Hunter](../ai-tutorial-hunter/) into fully realized, publication-ready tutorials for [ai-evolution.com.au](https://ai-evolution.com.au) (branded as **The Pulse**).

It doesn't just summarize — it **researches, writes, illustrates, and deploys** complete, engaging tutorials with real-world application examples, hands-on code, and interactive elements, all styled to match The Pulse's dark-forest design system.

---

## How It Works

```
┌──────────────────┐     ┌──────────────────┐     ┌──────────────────┐
│  TUTORIAL HUNTER  │────▶│ TUTORIAL GENESYS  │────▶│  AI-EVOLUTION    │
│                  │     │                  │     │  .COM.AU          │
│ • Trending topics│     │ • Research       │     │                  │
│ • Ranked content │     │ • Write          │     │ • Published      │
│ • Gap analysis   │     │ • Illustrate     │     │ • Styled         │
│ • Quality scores │     │ • Review         │     │ • SEO-optimized  │
│                  │     │ • Deploy         │     │ • Engaging       │
└──────────────────┘     └──────────────────┘     └──────────────────┘
```

---

## Core Agents

### 1. Researcher Agent
- Ingests top-ranked tutorials from Tutorial Hunter's pipeline output
- Deep-dives into the topic: reads source material, documentation, papers
- Extracts key concepts, prerequisites, and learning objectives
- Identifies **real-world application examples** for each concept
- Produces a structured research brief with teaching outline

### 2. Writer Agent
- Transforms the research brief into a complete tutorial
- Writing style: professional, empowering, accessible (matches The Pulse tone)
- Structure: Hook → Context → Step-by-step → Real-world application → Summary
- Includes hands-on code examples with explanations
- Creates "Try It Yourself" challenges
- Generates FAQ sections from common questions
- Targets 2,000–5,000 words per tutorial

### 3. Illustrator Agent
- Generates procedural SVG diagrams matching The Pulse aesthetic
- Creates architecture diagrams, flowcharts, concept maps
- Color-coded by category (green primary, blue/teal/orange accents)
- Produces code syntax-highlighted blocks with the dark theme
- Generates hero images with geometric/abstract AI-themed art

### 4. Reviewer Agent
- Technical accuracy check against source material
- Readability scoring (Flesch-Kincaid, target: Grade 10–12)
- Code validation: syntax check, completeness, correctness
- SEO optimization: meta tags, headings, keyword density
- Accessibility audit: alt text, heading hierarchy, contrast
- Engagement scoring: hooks, examples, interactivity

### 5. Publisher Agent
- Renders final HTML using The Pulse design templates
- Generates SEO metadata (title, description, OG tags, structured data)
- Creates table of contents with anchor links
- Packages assets (SVGs, code blocks, images)
- Deploys to ai-evolution.com.au via API or static file output
- Generates social sharing cards

---

## Design System — The Pulse

All generated tutorials follow The Pulse's design language:

### Colors
| Token | Value | Usage |
|-------|-------|-------|
| `--pulse-green` | `#00c853` | Primary accent, CTAs, highlights |
| `--pulse-bg-deep` | `#0d1a0f` | Page background |
| `--pulse-bg-surface` | `#132116` | Card backgrounds |
| `--pulse-bg-elevated` | `#192b1c` | Elevated surfaces |
| `--pulse-text` | `#e8f5e9` | Body text |
| `--pulse-text-muted` | `#81c784` | Secondary text |
| `--pulse-border` | `rgba(0,200,83,0.15)` | Card borders |
| `--pulse-glow` | `rgba(0,200,83,0.3)` | Glow effects |
| `--cat-government` | `#5b9cf6` | Government category |
| `--cat-personal` | `#4ecdc4` | Personal category |
| `--cat-business` | `#ffa62b` | Business category |

### Typography
- **Font:** Inter, system-ui, sans-serif
- **Headings:** 700–900 weight, letter-spacing: 0.04em
- **Body:** 400 weight, 1.7 line-height
- **Code:** JetBrains Mono, monospace

### Components
- **Glassmorphic cards** — backdrop-filter blur, semi-transparent backgrounds
- **Neon green accents** — borders, links, code highlights
- **Procedural SVG hero art** — geometric shapes seeded by article data
- **Smooth animations** — fade-in on scroll, hover glows
- **Dark code blocks** — syntax highlighting on deep-green backgrounds

---

## Tutorial Structure

Each generated tutorial follows this structure:

```
1. HERO SECTION
   - Procedural SVG hero image
   - Title + subtitle
   - Category badge + reading time + difficulty
   - Author attribution (AI-generated, human-reviewed)

2. TABLE OF CONTENTS
   - Anchor-linked section list
   - Progress indicator

3. INTRODUCTION
   - Hook: Why this matters NOW
   - Context: Where this fits in the AI landscape
   - Prerequisites
   - What you'll learn (bullet list)

4. CONCEPT SECTIONS (2–5 per tutorial)
   - Clear explanation with analogies
   - Diagram or visual (SVG)
   - Code example (syntax highlighted)
   - Real-world application example
   - "Try It Yourself" mini-challenge

5. HANDS-ON PROJECT
   - Complete working example
   - Step-by-step build
   - Full source code
   - Expected output

6. REAL-WORLD APPLICATIONS
   - 3–5 industry use cases
   - Case studies with concrete numbers
   - "How [Company] uses this" examples

7. COMMON PITFALLS & FAQ
   - Top 5 mistakes beginners make
   - Frequently asked questions
   - Troubleshooting guide

8. SUMMARY & NEXT STEPS
   - Key takeaways (bullet list)
   - Related tutorials (from Tutorial Hunter)
   - Resources for further learning
   - Call to action
```

---

## Architecture

```
tutorial-genesys/
├── tutorial_genesys/
│   ├── agents/                  # Content generation agents
│   │   ├── researcher.py        # Deep-dive research from Hunter data
│   │   ├── writer.py            # Tutorial content writer
│   │   ├── illustrator.py       # SVG and visual generation
│   │   ├── reviewer.py          # Quality, accuracy, SEO review
│   │   ├── publisher.py         # Final rendering and deployment
│   │   └── orchestrator.py      # Pipeline coordination
│   ├── models/                  # Data models
│   │   ├── tutorial_content.py  # Full tutorial structure
│   │   ├── research_brief.py    # Research output model
│   │   ├── review_report.py     # Review results
│   │   └── publish_manifest.py  # Deployment manifest
│   ├── templates/               # HTML/CSS/SVG templates
│   │   ├── tutorial.html        # Main tutorial template
│   │   ├── components/          # Reusable components
│   │   │   ├── hero.html
│   │   │   ├── code_block.html
│   │   │   ├── callout.html
│   │   │   ├── toc.html
│   │   │   └── challenge.html
│   │   ├── styles/
│   │   │   └── pulse.css        # The Pulse design system
│   │   └── svg/
│   │       └── hero_generator.py
│   ├── integration/             # Tutorial Hunter integration
│   │   ├── hunter_client.py     # Reads Hunter pipeline output
│   │   └── topic_selector.py    # Selects best topics for tutorials
│   ├── delivery/                # Output and deployment
│   │   ├── renderer.py          # Jinja2 HTML rendering
│   │   ├── seo.py               # SEO metadata generation
│   │   └── deployer.py          # Deploy to ai-evolution.com.au
│   ├── config/
│   │   ├── settings.py          # Environment configuration
│   │   └── prompts.py           # LLM prompt templates
│   └── cli.py                   # CLI entry point
├── tests/
├── output/                      # Generated tutorials (local preview)
├── .env.example
├── pyproject.toml
├── Dockerfile
└── TUTORIAL-GENESYS.md
```

---

## Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.12+ |
| **LLM** | Claude API (Anthropic) — Opus for writing, Haiku for classification |
| **Templates** | Jinja2 |
| **SVG Generation** | Custom Python SVG builder |
| **Code Highlighting** | Pygments |
| **Markdown** | markdown-it / mistune |
| **SEO** | Custom metadata generator |
| **Deployment** | API push to ai-evolution.com.au or static HTML output |
| **Testing** | pytest |

---

## CLI Commands

```bash
# Generate a tutorial from Tutorial Hunter's latest results
genesys generate --from-hunter

# Generate a tutorial for a specific topic
genesys generate --topic "AI Agents with MCP"

# Preview a generated tutorial locally
genesys preview --tutorial-id abc123

# Deploy to ai-evolution.com.au
genesys deploy --tutorial-id abc123

# Run the full pipeline: select topic → research → write → review → publish
genesys pipeline --auto

# List generated tutorials
genesys list
```

---

## Roadmap

### Phase 1 — Core Engine (Weeks 1–2)
- [ ] Project scaffolding
- [ ] Tutorial Hunter integration client
- [ ] Researcher agent with Claude API
- [ ] Writer agent with structured output
- [ ] Basic HTML template with Pulse styling

### Phase 2 — Visual & Quality (Weeks 3–4)
- [ ] Illustrator agent (SVG diagrams, hero art)
- [ ] Reviewer agent (accuracy, readability, SEO)
- [ ] Code syntax highlighting
- [ ] Interactive "Try It Yourself" components
- [ ] Full Pulse design system CSS

### Phase 3 — Deployment (Weeks 5–6)
- [ ] Publisher agent
- [ ] SEO metadata and structured data
- [ ] API deployment to ai-evolution.com.au
- [ ] Social sharing card generation
- [ ] Tutorial management dashboard

### Phase 4 — Automation (Weeks 7–8)
- [ ] Automated pipeline: Hunter → Genesys → Publish
- [ ] Scheduled generation (weekly)
- [ ] A/B testing tutorial structures
- [ ] Analytics feedback loop
- [ ] Multi-format output (blog, email, social)

---

## License

MIT
