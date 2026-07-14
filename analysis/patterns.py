"""Cluster the 100 findings into the patterns that are the point of the exercise.

Emits data/patterns.json: auth distribution, self-serve vs gated (overall + by
category), buildability, blockers, MCP, Composio coverage, and the easy-wins vs
needs-outreach quadrant — plus plain-English headline sentences for the page.

Run:  python analysis/patterns.py  ->  writes data/patterns.json
"""
from __future__ import annotations

import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

DATA = ROOT / "data"

SELF_SERVE = {"Self-serve free", "Self-serve trial"}
GATED = {"Paid plan required", "Admin / app review", "Partner / contact-sales", "Unknown"}


def pct(n: int, d: int) -> float:
    return round(100 * n / d, 1) if d else 0.0


def main() -> None:
    F = json.loads((DATA / "findings.json").read_text())["findings"]
    n = len(F)

    # --- auth: apps mentioning each method (lists, so presence-counted) ---
    auth = Counter()
    for f in F:
        for a in f["auth_methods"]:
            auth[a] += 1
    oauth = auth.get("OAuth2", 0)
    # distinct apps offering at least one key/token/basic path (not a sum of methods)
    apikeyish = sum(1 for f in F
                    if any(a in ("API key", "Token", "Basic") for a in f["auth_methods"]))
    both = sum(1 for f in F
               if "OAuth2" in f["auth_methods"]
               and any(a in ("API key", "Token", "Basic") for a in f["auth_methods"]))

    # --- access model ---
    access = Counter(f["access_model"] for f in F)
    self_serve_n = sum(v for k, v in access.items() if k in SELF_SERVE)
    gated_n = n - self_serve_n

    # --- self-serve vs gated by category ---
    by_cat = defaultdict(lambda: {"total": 0, "self_serve": 0, "gated": 0})
    for f in F:
        c = by_cat[f["category"]]
        c["total"] += 1
        if f["access_model"] in SELF_SERVE:
            c["self_serve"] += 1
        else:
            c["gated"] += 1
    for c in by_cat.values():
        c["self_serve_pct"] = pct(c["self_serve"], c["total"])

    # --- buildability + blockers ---
    build = Counter(f["buildability"] for f in F)
    blockers = Counter()
    for f in F:
        b = (f["blocker"] or "").lower()
        if not b:
            continue
        if any(w in b for w in ("app review", "verification", "developer token",
                                "registration", "approval", "program")):
            blockers["App review / verification"] += 1
        elif any(w in b for w in ("partner", "contact", "sales", "contract",
                                  "account manager", "reseller", "enterprise",
                                  "instance", "provision")):
            blockers["Partnership / sales / enterprise"] += 1
        elif any(w in b for w in ("paid", "credit", "plan", "subscription", "units")):
            blockers["Paid plan / credits"] += 1
        elif any(w in b for w in ("no api", "no web api", "no true public", "cli",
                                  "webhook", "narrow")):
            blockers["No/limited public API"] += 1
        else:
            blockers["Other"] += 1

    # --- MCP + Composio ---
    mcp = Counter(f["mcp"] for f in F)
    any_mcp = sum(v for k, v in mcp.items() if k in ("Official MCP", "Community MCP"))
    official_mcp = mcp.get("Official MCP", 0)
    composio_yes = sum(1 for f in F if f["composio_supported"] is True)

    # --- easy wins vs needs-outreach quadrant ---
    easy_wins = [f["name"] for f in F
                 if f["buildability"] == "Ready" and f["access_model"] in SELF_SERVE
                 and not f["composio_supported"]]
    needs_outreach = [f["name"] for f in F
                      if f["access_model"] in ("Partner / contact-sales", "Admin / app review")]
    already_covered = sum(1 for f in F
                          if f["composio_supported"] and f["buildability"] == "Ready")

    headline = [
        f"{pct(oauth, n)}% of the 100 support OAuth2 and {pct(apikeyish, n)}% offer a "
        f"key/token/basic path ({both} support both) — auth is rarely the real blocker.",
        f"{pct(self_serve_n, n)}% are self-serve (free or trial); only {pct(gated_n, n)}% "
        f"are gated behind paid plans, app review, or a partnership/sales motion.",
        f"{build['Ready']} of 100 are build-ready today. The gated {build.get('Ready but gated',0)} "
        f"are blocked by access, not by API quality.",
        f"The dominant blocker is '{blockers.most_common(1)[0][0]}' "
        f"({blockers.most_common(1)[0][1]} apps) — an approvals/partnership problem, not a technical one.",
        f"{len(easy_wins)} apps are easy wins: Ready + self-serve + not yet a Composio toolkit. "
        f"Gated/enterprise apps ({len(needs_outreach)}) are the outreach list.",
    ]

    out = {
        "n": n,
        "auth": dict(auth.most_common()),
        "auth_note": f"OAuth2 in {oauth}/{n}; API-key/token/basic in most as well (apps overlap).",
        "access": dict(access.most_common()),
        "self_serve_n": self_serve_n,
        "gated_n": gated_n,
        "by_category": dict(sorted(by_cat.items(), key=lambda kv: -kv[1]["self_serve_pct"])),
        "buildability": dict(build.most_common()),
        "blockers": dict(blockers.most_common()),
        "mcp": dict(mcp.most_common()),
        "any_mcp": any_mcp,
        "official_mcp": official_mcp,
        "composio_supported": composio_yes,
        "easy_wins": sorted(easy_wins),
        "needs_outreach": sorted(needs_outreach),
        "already_covered_ready": already_covered,
        "headline": headline,
    }
    (DATA / "patterns.json").write_text(json.dumps(out, indent=2))
    print(json.dumps({k: out[k] for k in
          ("auth", "access", "buildability", "blockers", "mcp",
           "composio_supported", "official_mcp")}, indent=2))
    print("\nEASY WINS:", len(easy_wins), "| NEEDS OUTREACH:", len(needs_outreach))
    for h in headline:
        print(" •", h)


if __name__ == "__main__":
    main()
