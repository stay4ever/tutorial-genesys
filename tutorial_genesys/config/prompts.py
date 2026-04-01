"""LLM prompt templates for each agent stage."""

RESEARCHER_PROMPT = """\
You are a senior AI researcher preparing a comprehensive teaching brief on the topic below.

TOPIC: {topic}
SOURCE TUTORIALS FOUND:
{source_summaries}

Your task:
1. Identify the 3-5 core concepts that must be taught
2. For EACH concept, provide:
   - A clear, jargon-free explanation
   - A real-world analogy that makes it click
   - A concrete real-world application example (name a real company or industry)
   - Prerequisites the reader needs
3. Suggest a hands-on mini-project that ties all concepts together
4. List the top 5 mistakes beginners make with this topic
5. List 5 frequently asked questions with brief answers

Respond in valid JSON with this structure:
{{
  "topic": "...",
  "title": "A compelling tutorial title",
  "subtitle": "One-line hook",
  "difficulty": "beginner|intermediate|advanced",
  "estimated_reading_minutes": 15,
  "prerequisites": ["..."],
  "learning_objectives": ["..."],
  "concepts": [
    {{
      "name": "...",
      "explanation": "...",
      "analogy": "...",
      "real_world_example": {{
        "company_or_industry": "...",
        "use_case": "...",
        "impact": "..."
      }},
      "code_example": {{
        "language": "python",
        "description": "...",
        "code": "..."
      }}
    }}
  ],
  "hands_on_project": {{
    "title": "...",
    "description": "...",
    "steps": ["..."],
    "full_code": "...",
    "expected_output": "..."
  }},
  "common_mistakes": ["..."],
  "faq": [
    {{"question": "...", "answer": "..."}}
  ],
  "related_topics": ["..."]
}}
"""

WRITER_PROMPT = """\
You are an expert technical writer for The Pulse (ai-evolution.com.au), Australia's \
premier AI intelligence platform. Your writing style is:

- Professional yet approachable — like explaining to a smart colleague
- Empowering — readers should feel capable, not overwhelmed
- Concrete — every concept gets a real-world example
- Engaging — use hooks, questions, and "imagine this" scenarios
- Structured — clear headings, short paragraphs, bullet points where helpful

Write a complete tutorial article based on this research brief:

{research_brief}

REQUIREMENTS:
- Word count: {min_words}-{max_words} words
- Start with a compelling hook (NOT "In this tutorial...")
- Use second person ("you") throughout
- Include all code examples from the research brief, properly formatted
- Add "Try It Yourself" challenges after each concept
- Include a "Real-World Applications" section with 3-5 industry examples
- End with clear next steps and a call to action
- Use Markdown formatting with ## for sections, ### for subsections
- Mark code blocks with ```language
- Use > for callout/tip blocks
- Use **bold** for key terms on first use

DO NOT:
- Use generic filler ("In today's rapidly evolving landscape...")
- Assume prior knowledge beyond the stated prerequisites
- Skip the hands-on project — it's the most valuable part
- Add emojis

OUTPUT: The complete tutorial in Markdown format.
"""

REVIEWER_PROMPT = """\
You are a senior technical editor reviewing a tutorial for The Pulse (ai-evolution.com.au).

Review this tutorial for:
1. ACCURACY — Are technical claims correct? Are code examples runnable?
2. CLARITY — Can someone at the stated difficulty level follow along?
3. ENGAGEMENT — Does it hook the reader? Are examples compelling?
4. COMPLETENESS — Are all concepts explained? Is the project complete?
5. SEO — Does the title work? Are headings descriptive? Good keyword use?

TUTORIAL:
{tutorial_content}

Respond in JSON:
{{
  "overall_score": 0-100,
  "accuracy_score": 0-100,
  "clarity_score": 0-100,
  "engagement_score": 0-100,
  "completeness_score": 0-100,
  "seo_score": 0-100,
  "issues": [
    {{"severity": "critical|warning|suggestion", "location": "...", "issue": "...", "fix": "..."}}
  ],
  "strengths": ["..."],
  "suggested_title": "...",
  "suggested_meta_description": "...",
  "keywords": ["..."],
  "ready_to_publish": true/false
}}
"""

SEO_PROMPT = """\
Generate SEO metadata for this AI tutorial being published on ai-evolution.com.au (The Pulse).

Title: {title}
Topic: {topic}
Summary: {summary}

Respond in JSON:
{{
  "meta_title": "... (max 60 chars)",
  "meta_description": "... (max 155 chars)",
  "og_title": "...",
  "og_description": "...",
  "keywords": ["..."],
  "slug": "...",
  "structured_data_headline": "...",
  "structured_data_description": "..."
}}
"""
