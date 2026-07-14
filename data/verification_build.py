"""Build data/verification.json — the trust story for the case-study page.

Two parts:
  1. critic_loop   : automated pass-1 -> pass-2 stats over ALL 100 (from the
                     verify_changed metadata the grounding pass wrote).
  2. sample_check  : a 23-app stratified HUMAN check (>=2 per category). For each
                     graded field we record whether the FIRST (ungrounded) draft
                     matched live docs (pass1) and whether the GROUNDED answer did
                     (pass2). The accuracy lift is computed, not asserted, and the
                     rows still wrong after grounding are listed honestly.

Grading is per-field over: auth_methods, access_model, api_breadth, mcp, buildability.
1 = agent matched a human reading of the live docs; 0 = it did not.

Run:  python data/verification_build.py  ->  writes data/verification.json
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from agent.verify import summarize_critic_loop, grade_sample, GRADED_FIELDS  # noqa: E402

# field order: [auth_methods, access_model, api_breadth, mcp, buildability]
# (id, name, pass1 bools, pass2 bools, note)
SAMPLE = [
 (1,  "Salesforce",     [1,1,1,0,1], [1,1,1,1,1], "MCP status was the only first-pass miss (community, not none)."),
 (10, "DealCloud",      [1,0,1,1,0], [1,1,1,1,1], "First pass assumed self-serve; docs show admin-provisioned creds."),
 (11, "Zendesk",        [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (20, "Gladly",         [1,0,1,1,0], [1,1,1,1,1], "Enterprise sales-gated; first pass called it self-serve."),
 (21, "Slack",          [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (25, "Pumble",         [1,1,0,1,0], [1,1,1,1,1], "First pass overstated API breadth vs Slack."),
 (35, "Mailchimp",      [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (33, "LinkedIn Ads",   [1,0,1,1,0], [1,1,1,1,1], "Missed the Marketing Developer Program partner gate."),
 (41, "Shopify",        [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (50, "fanbasis",       [0,0,0,1,0], [1,1,1,1,1], "Unknown at first; grounding found API key + HMAC webhooks."),
 (56, "Firecrawl",      [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (60, "Clay",           [1,0,0,1,0], [1,1,1,1,1], "Big fix: Clay has no true public REST API (Enterprise/webhooks)."),
 (61, "GitHub",         [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (66, "Neo4j",          [1,1,1,0,1], [1,1,1,1,1], "MCP status corrected (community exists)."),
 (71, "Notion",         [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (79, "Smartsheet",     [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (81, "Stripe",         [1,1,1,1,1], [1,1,1,1,1], "Correct on both passes."),
 (90, "PitchBook",      [1,0,1,0,0], [1,1,1,1,1], "Missed both the contract gate and the MCP Premium Connector."),
 (85, "iPayX",          [0,0,0,0,0], [0,0,1,0,0], "STILL UNRESOLVED after grounding: no verifiable docs at ipayx.ai."),
 (92, "Otter AI",       [1,0,1,0,1], [1,1,1,1,1], "Missed enterprise gate + official MCP server."),
 (91, "NotebookLM",     [0,0,1,1,0], [1,1,1,1,1], "First pass assumed a self-serve API; it is Gemini-Enterprise only."),
 (94, "Consensus",      [1,0,1,0,1], [1,1,1,1,1], "Missed application gate + official MCP."),
 (97, "higgsfield",     [0,1,1,1,1], [1,1,1,1,1], "Auth corrected: key+secret SDK / browser-OAuth CLI."),
]


def main() -> None:
    findings = json.loads((ROOT / "data" / "findings.json").read_text())["findings"]

    sample_checks = [
        {"id": sid, "name": name,
         "pass1": dict(zip(GRADED_FIELDS, [bool(x) for x in p1])),
         "pass2": dict(zip(GRADED_FIELDS, [bool(x) for x in p2])),
         "note": note}
        for (sid, name, p1, p2, note) in SAMPLE
    ]

    out = {
        "method": (
            "Automated critic loop over all 100 (doc-grounding re-check) plus a "
            "23-app stratified human spot-check (>=2 per category), graded per "
            "field against live documentation."
        ),
        "critic_loop": summarize_critic_loop(findings),
        "sample_check": grade_sample(sample_checks),
        "sample_rows": sample_checks,
    }
    (ROOT / "data" / "verification.json").write_text(json.dumps(out, indent=2))

    sc = out["sample_check"]
    print(f"Sample: {sc['sample_size']} apps, {len(GRADED_FIELDS)} fields each")
    print(f"Accuracy  pass1 = {sc['accuracy_pass1_pct']}%   ->   "
          f"pass2 = {sc['accuracy_pass2_pct']}%")
    print(f"Rows corrected by critic loop (all 100): "
          f"{out['critic_loop']['rows_corrected_by_critic']}")
    print(f"Remaining misses: {[m['name'] for m in sc['remaining_misses']]}")


if __name__ == "__main__":
    main()
