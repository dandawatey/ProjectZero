"""PRD Agent — interactive product requirements generation.

Drives a multi-turn conversation with Claude to extract a full PRD
from a user's rough idea. Used by the /products/prd-chat endpoint.

Stages:
  1. gather   — Claude asks clarifying questions (3-5 rounds)
  2. draft    — Claude produces structured PRD markdown
  3. refine   — user edits; Claude incorporates feedback
"""

from __future__ import annotations

import os
import logging
from typing import AsyncIterator

logger = logging.getLogger(__name__)

_SYSTEM = """You are a senior product manager at a world-class AI software factory.
Your job: turn a rough product idea into a precise, actionable PRD.

CONVERSATION PHASES:
1. GATHER — Ask the user focused clarifying questions (max 4 questions at a time).
   Topics to cover: target users, core problem, key features, success metrics,
   constraints (budget/timeline/tech), out-of-scope.
   Ask only what you don't know yet. Be concise.

2. DRAFT — Once you have enough context, say "I have enough to write the PRD."
   Then produce the full PRD in this exact structure:

   # PRD: {Product Name}

   ## Problem Statement
   ## Target Users
   ## Goals & Success Metrics
   ## Features (MoSCoW)
   ### Must Have
   ### Should Have
   ### Could Have
   ### Won't Have (this release)
   ## Technical Constraints
   ## Out of Scope
   ## Timeline (3-sprint estimate)
   ## Risks & Mitigations
   ## Definition of Done

3. REFINE — If the user asks for changes, incorporate them and output an updated PRD.

RULES:
- Never invent requirements the user hasn't mentioned or implied.
- Keep PRD language precise: "The system shall..." not "We could maybe...".
- Flag ambiguity explicitly rather than guessing.
- If the user's idea is too vague to write a PRD, keep asking."""


async def stream_prd_chat(
    messages: list[dict],  # [{role: user|assistant, content: str}]
) -> AsyncIterator[str]:
    """Stream Claude's response token by token."""
    try:
        import anthropic
    except ImportError:
        raise RuntimeError("anthropic package not installed")

    api_key = os.getenv("ANTHROPIC_API_KEY", "")
    if not api_key:
        raise RuntimeError("ANTHROPIC_API_KEY not set")

    model = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-6")
    client = anthropic.AsyncAnthropic(api_key=api_key)

    async with client.messages.stream(
        model=model,
        max_tokens=4096,
        system=_SYSTEM,
        messages=messages,
    ) as stream:
        async for text in stream.text_stream:
            yield text


def extract_prd_from_conversation(messages: list[dict]) -> str | None:
    """Find the last assistant message that contains a full PRD (has '# PRD:')."""
    for msg in reversed(messages):
        if msg["role"] == "assistant" and "# PRD:" in msg["content"]:
            # Extract from the PRD heading onward
            idx = msg["content"].index("# PRD:")
            return msg["content"][idx:]
    return None
