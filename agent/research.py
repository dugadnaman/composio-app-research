"""Per-app research: the core agent step.

Flow for one app (this is the "what it does" the interviewer will ask about):
  1. DRAFT   - LLM drafts a finding from its knowledge, using our controlled
               vocab, and proposes the single best evidence URL.
  2. GROUND  - we actually fetch that URL (agent/web.py). Real bytes, not vibes.
  3. CONFIRM - LLM re-reads the fetched page and either confirms or corrects the
               draft, and self-rates confidence. If the page was thin/blocked it
               says so and confidence drops -> becomes a human-review row.

Everything is coerced through the Pydantic AppFinding schema, so a malformed
field fails loudly instead of silently poisoning the dataset.
"""
from __future__ import annotations

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from schema import AppFinding  # noqa: E402
from agent.web import fetch_text  # noqa: E402

VOCAB = """
Controlled vocabularies you MUST use exactly:
- auth_methods (list): "OAuth2", "API key", "Basic", "Token", "Other", "None / n/a"
- access_model: "Self-serve free", "Self-serve trial", "Paid plan required",
  "Admin / app review", "Partner / contact-sales", "Unknown"
- api_breadth: "broad", "moderate", "narrow", "none"
- mcp: "Official MCP", "Community MCP", "No MCP", "Unknown"
- buildability: "Ready", "Ready but gated", "Partial", "Blocked", "Unknown"
"""

DRAFT_SYS = (
    "You are a developer-relations analyst for Composio, which turns apps into "
    "tools AI agents can call. For a given app, produce a precise, sourceable "
    "research finding. Be conservative: if unsure, say Unknown rather than guess."
    + VOCAB
)

DRAFT_USER = """App: {name}
Category: {category}
Starting hint: {hint}

Return JSON with keys:
one_liner, auth_methods, auth_detail, access_model, access_detail,
api_surface, api_breadth, mcp, buildability, blocker, evidence_url, confidence, notes.

evidence_url: the single best PUBLIC docs URL that proves your auth + access answer.
"""

CONFIRM_SYS = (
    "You verify a draft finding against the actual fetched documentation text. "
    "Correct any field the page contradicts. If the page is thin, blocked, or "
    "off-topic, keep your prior answer but LOWER confidence and note it needs a "
    "human/browser check. Only change fields you have evidence for." + VOCAB
)

CONFIRM_USER = """App: {name}
Your draft finding (JSON):
{draft}

Fetched page: {url}
Fetch note: {note}
Page text (truncated):
\"\"\"{page}\"\"\"

Return the FULL corrected JSON finding (same keys as the draft) plus a key
"verify_changed": a list of field names you changed (empty list if none).
"""


def _coerce(raw: dict, app: dict, category: str) -> AppFinding:
    raw = dict(raw)
    raw.update({"id": app["id"], "name": app["name"], "category": category,
                "hint": str(app.get("hint", ""))})
    return AppFinding.model_validate(raw)


def research_app(app: dict, category: str, backend, ground: bool = True) -> AppFinding:
    draft_raw = backend.complete_json(
        DRAFT_SYS,
        DRAFT_USER.format(name=app["name"], category=category, hint=app.get("hint", "")),
    )
    draft = _coerce(draft_raw, app, category)

    if not ground or not draft.evidence_url:
        return draft

    page = fetch_text(draft.evidence_url)
    confirmed_raw = backend.complete_json(
        CONFIRM_SYS,
        CONFIRM_USER.format(
            name=app["name"],
            draft=draft.model_dump_json(indent=2),
            url=page["url"],
            note=page["note"] or "ok",
            page=page["text"] or "(empty)",
        ),
    )
    confirmed = _coerce(confirmed_raw, app, category)
    confirmed.verified = True
    return confirmed
