"""Verification: how we show the findings are trustworthy.

Two mechanisms, matching the assignment:

1. CRITIC LOOP (machine, all 100): research.py already re-grounds each draft
   against the fetched page. verify.py aggregates how many rows changed and how
   confidence moved. This is the automated first-pass -> second-pass lift.

2. SAMPLE HAND-CHECK (human, ~18 rows): a stratified sample across all 10
   categories is checked against live docs by a person. We record, per field,
   whether the agent was right, and compute accuracy BEFORE and AFTER the critic
   loop so the improvement is a real, auditable number — including honest misses.

verification.json (produced here + hand-filled) is what the case-study page reads.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import List

DATA = Path(__file__).resolve().parent.parent / "data"

# Fields we grade in the human sample check.
GRADED_FIELDS = ["auth_methods", "access_model", "api_breadth", "mcp", "buildability"]


def summarize_critic_loop(findings: List[dict]) -> dict:
    """Automated pass-1 vs pass-2 stats from the critic re-grounding."""
    total = len(findings)
    changed = [f for f in findings if f.get("verify_changed")]
    field_changes: dict[str, int] = {}
    for f in changed:
        for fld in f.get("verify_changed") or []:
            field_changes[fld] = field_changes.get(fld, 0) + 1
    grounded = [f for f in findings if f.get("verified")]
    avg_conf = round(sum(f.get("confidence", 0) for f in findings) / max(total, 1), 3)
    return {
        "total": total,
        "grounded_against_live_docs": len(grounded),
        "rows_corrected_by_critic": len(changed),
        "field_change_counts": dict(sorted(field_changes.items(), key=lambda x: -x[1])),
        "avg_confidence": avg_conf,
        "low_confidence_rows": [f["name"] for f in findings if f.get("confidence", 1) < 0.5],
    }


def stratified_sample(findings: List[dict], per_category: int = 2) -> List[int]:
    """Pick ~2 apps per category for the human check (deterministic, no RNG)."""
    by_cat: dict[str, list] = {}
    for f in findings:
        by_cat.setdefault(f["category"], []).append(f)
    ids: list[int] = []
    for cat, items in by_cat.items():
        items = sorted(items, key=lambda x: x["id"])
        ids += [items[0]["id"]]
        if len(items) > 1:
            ids.append(items[len(items) // 2]["id"])
    return sorted(ids)[: per_category * len(by_cat)]


def grade_sample(sample_checks: List[dict]) -> dict:
    """
    sample_checks: list of {id, name, pass1: {field: bool}, pass2: {field: bool}}
    where bool = agent matched the human's reading of live docs.
    Returns per-pass accuracy and the honest miss list.
    """
    def acc(pass_key: str) -> float:
        hits = tot = 0
        for row in sample_checks:
            for fld in GRADED_FIELDS:
                v = row.get(pass_key, {}).get(fld)
                if v is None:
                    continue
                tot += 1
                hits += 1 if v else 0
        return round(100 * hits / tot, 1) if tot else 0.0

    misses = [
        {"id": r["id"], "name": r["name"],
         "fields": [f for f in GRADED_FIELDS if r.get("pass2", {}).get(f) is False]}
        for r in sample_checks
        if any(r.get("pass2", {}).get(f) is False for f in GRADED_FIELDS)
    ]
    return {
        "sample_size": len(sample_checks),
        "fields_graded_per_row": GRADED_FIELDS,
        "accuracy_pass1_pct": acc("pass1"),
        "accuracy_pass2_pct": acc("pass2"),
        "remaining_misses": misses,
    }


if __name__ == "__main__":
    findings = json.loads((DATA / "findings.json").read_text())["findings"]
    out = {"critic_loop": summarize_critic_loop(findings),
           "suggested_sample_ids": stratified_sample(findings)}
    (DATA / "verification_auto.json").write_text(json.dumps(out, indent=2))
    print(json.dumps(out["critic_loop"], indent=2))
