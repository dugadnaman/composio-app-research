"""Pluggable LLM backend.

Two backends, same interface, so the pipeline is model-agnostic:
  - GeminiBackend  : Google Gemini free tier (default in the README, needs GEMINI_API_KEY)
  - ClaudeBackend  : Anthropic (used to GENERATE this repo's committed dataset)

Both expose .complete_json(system, user) -> dict, forcing a JSON object out.
Keeping this thin is deliberate: the interviewer can read it in 60 seconds and
there is no framework magic to explain away.
"""
from __future__ import annotations

import json
import os
import re
from typing import Optional


def _extract_json(text: str) -> dict:
    """Best-effort: pull the first JSON object out of a model response."""
    text = text.strip()
    # strip ```json fences
    text = re.sub(r"^```(?:json)?", "", text).strip()
    text = re.sub(r"```$", "", text).strip()
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        start = text.find("{")
        end = text.rfind("}")
        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])
        raise


class GeminiBackend:
    name = "gemini"

    def __init__(self, model: str = "gemini-2.0-flash"):
        from google import genai  # lazy import

        self.model = model
        self.client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    def complete_json(self, system: str, user: str) -> dict:
        from google.genai import types

        resp = self.client.models.generate_content(
            model=self.model,
            contents=user,
            config=types.GenerateContentConfig(
                system_instruction=system,
                response_mime_type="application/json",
                temperature=0.2,
            ),
        )
        return _extract_json(resp.text)


class ClaudeBackend:
    name = "claude"

    def __init__(self, model: str = "claude-sonnet-4-6"):
        import anthropic  # lazy import

        self.model = model
        self.client = anthropic.Anthropic()  # reads ANTHROPIC_API_KEY

    def complete_json(self, system: str, user: str) -> dict:
        msg = self.client.messages.create(
            model=self.model,
            max_tokens=2000,
            temperature=0.2,
            system=system + "\nRespond with a single JSON object and nothing else.",
            messages=[{"role": "user", "content": user}],
        )
        return _extract_json(msg.content[0].text)


def get_backend(name: Optional[str] = None):
    name = (name or os.environ.get("LLM_BACKEND", "gemini")).lower()
    if name == "gemini":
        return GeminiBackend()
    if name == "claude":
        return ClaudeBackend()
    raise ValueError(f"unknown backend: {name}")
