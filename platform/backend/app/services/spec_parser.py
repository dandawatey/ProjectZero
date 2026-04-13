"""Spec parser service — PRJ0-40.

Uses Claude API to parse PRD text into structured user stories with acceptance criteria.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass, field


@dataclass
class AcceptanceCriterion:
    given: str
    when: str
    then: str


@dataclass
class UserStory:
    title: str
    role: str               # "As a <role>"
    action: str             # "I want to <action>"
    benefit: str            # "so that <benefit>"
    priority: int           # 1=highest
    acceptance_criteria: list[AcceptanceCriterion]
    estimate_sp: int        # story point estimate


@dataclass
class SpecResult:
    feature_title: str
    feature_summary: str
    stories: list[UserStory]
    risks: list[str]
    dependencies: list[str]


_SYSTEM_PROMPT = """\
You are a specification agent. Given a PRD or feature description, you extract structured user stories.

Output ONLY valid JSON — no markdown fences, no explanation — matching exactly this schema:

{
  "feature_title": "<short title>",
  "feature_summary": "<1-2 sentence summary>",
  "risks": ["<risk>", ...],
  "dependencies": ["<dependency>", ...],
  "stories": [
    {
      "title": "<story title>",
      "role": "<role, e.g. developer>",
      "action": "<what they want to do>",
      "benefit": "<business value>",
      "priority": <1-5 integer, 1=highest>,
      "estimate_sp": <fibonacci: 1|2|3|5|8|13>,
      "acceptance_criteria": [
        {
          "given": "<precondition>",
          "when": "<action>",
          "then": "<expected outcome>"
        }
      ]
    }
  ]
}

Rules:
- Generate 3-8 user stories that cover the full scope of the PRD.
- Each story must have 2-4 acceptance criteria.
- Priority 1 = highest urgency. Estimate using Fibonacci sequence.
- Output JSON only. No extra text.
"""


def _parse_response(raw: str) -> SpecResult:
    """Parse Claude JSON response into SpecResult dataclass."""
    # Strip any accidental markdown fences
    text = raw.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        text = "\n".join(lines[1:-1] if lines[-1].strip() == "```" else lines[1:])

    data = json.loads(text)

    stories: list[UserStory] = []
    for s in data.get("stories", []):
        criteria = [
            AcceptanceCriterion(
                given=ac["given"],
                when=ac["when"],
                then=ac["then"],
            )
            for ac in s.get("acceptance_criteria", [])
        ]
        stories.append(
            UserStory(
                title=s["title"],
                role=s["role"],
                action=s["action"],
                benefit=s["benefit"],
                priority=int(s.get("priority", 3)),
                acceptance_criteria=criteria,
                estimate_sp=int(s.get("estimate_sp", 3)),
            )
        )

    return SpecResult(
        feature_title=data["feature_title"],
        feature_summary=data["feature_summary"],
        stories=stories,
        risks=data.get("risks", []),
        dependencies=data.get("dependencies", []),
    )


async def parse_prd_to_stories(prd_text: str, project_key: str) -> SpecResult:
    """Call Claude API to parse PRD into structured user stories.

    Args:
        prd_text: Raw PRD / feature description text.
        project_key: JIRA project key (e.g. 'PRJ0') — included in prompt for context.

    Returns:
        SpecResult with feature metadata and list of UserStory objects.
    """
    import anthropic  # lazy import — optional dep at module level

    client = anthropic.AsyncAnthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

    user_message = (
        f"JIRA project key: {project_key}\n\n"
        f"PRD / Feature Description:\n{prd_text}"
    )

    message = await client.messages.create(
        model="claude-sonnet-4-6",
        max_tokens=4096,
        system=_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": user_message}],
    )

    raw = message.content[0].text
    return _parse_response(raw)
