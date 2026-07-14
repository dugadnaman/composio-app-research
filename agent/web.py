"""Web fetch helper for the agent's evidence step.

Plain requests + BeautifulSoup, no headless browser. This is a deliberate,
honest limitation: JS-heavy / login-walled docs (Notion-hosted pages, some
dashboards) return little text, and the agent DOWNGRADES its confidence when a
fetch is thin. Those become the human-in-the-loop rows on the case-study page.
"""
from __future__ import annotations

import requests
from bs4 import BeautifulSoup

UA = "composio-app-research/1.0 (+take-home research agent)"


def fetch_text(url: str, max_chars: int = 6000, timeout: int = 15) -> dict:
    """Return {'ok', 'url', 'status', 'text', 'note'} for a docs URL."""
    if not url.startswith(("http://", "https://")):
        url = "https://" + url
    try:
        r = requests.get(url, headers={"User-Agent": UA}, timeout=timeout)
    except requests.RequestException as e:
        return {"ok": False, "url": url, "status": None, "text": "", "note": f"fetch error: {e}"}

    soup = BeautifulSoup(r.text, "html.parser")
    for tag in soup(["script", "style", "nav", "footer", "svg"]):
        tag.decompose()
    text = " ".join(soup.get_text(" ").split())
    thin = len(text) < 400
    return {
        "ok": r.ok and not thin,
        "url": url,
        "status": r.status_code,
        "text": text[:max_chars],
        "note": "thin/JS-rendered page (likely needs a browser)" if thin else "",
    }
