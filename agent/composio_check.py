"""Composio coverage cross-check.

'buildability' is more trustworthy if we know whether Composio already ships a
toolkit for the app. If a COMPOSIO_API_KEY is present we ask the SDK; otherwise
we fall back to a small, hand-maintained seed set of slugs known to exist in
Composio's public catalog (kept intentionally short and honest -> unknown=None).
"""
from __future__ import annotations

import os
from functools import lru_cache

# Known-present Composio toolkits relevant to this 100-app set (public catalog +
# the demand ranking in the internal parity note). Absence here means "unknown",
# NOT "unsupported" — we never assert a negative we did not check.
KNOWN_SLUGS = {
    "salesforce", "hubspot", "pipedrive", "attio", "zoho", "close",
    "zendesk", "intercom", "freshdesk", "front", "helpscout", "gorgias",
    "slack", "twilio", "discord", "telegram", "whatsapp",
    "googleads", "mailchimp", "klaviyo", "pinterest", "sendgrid",
    "shopify", "woocommerce", "bigcommerce", "squarespace", "gumroad",
    "apify", "firecrawl",
    "github", "vercel", "netlify", "cloudflare", "supabase", "snowflake",
    "mongodb", "datadog", "sentry",
    "notion", "airtable", "linear", "jira", "asana", "monday", "clickup",
    "coda", "smartsheet",
    "stripe", "plaid", "quickbooks", "xero", "brex", "ramp",
}


def _normalize(name: str) -> str:
    return "".join(c for c in name.lower() if c.isalnum())


@lru_cache(maxsize=1)
def _live_slugs() -> frozenset:
    if not os.environ.get("COMPOSIO_API_KEY"):
        return frozenset()
    try:
        from composio import Composio  # lazy

        c = Composio()
        toolkits = c.toolkits.get()  # SDK surface; wrapped in try for version drift
        return frozenset(_normalize(getattr(t, "slug", "") or "") for t in toolkits)
    except Exception:
        return frozenset()


def composio_supported(name: str) -> bool | None:
    live = _live_slugs()
    norm = _normalize(name)
    if live:
        return any(norm in s or s in norm for s in live if s)
    # offline seed fallback
    for slug in KNOWN_SLUGS:
        if slug in norm or norm.startswith(slug):
            return True
    return None  # unknown, not False
