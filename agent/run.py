"""Orchestrator: research all 100 apps, resumable and cached.

Usage:
  LLM_BACKEND=gemini GEMINI_API_KEY=... python -m agent.run              # all 100
  LLM_BACKEND=gemini GEMINI_API_KEY=... python -m agent.run --ids 1,2,3  # subset
  python -m agent.run --no-ground                                        # skip fetch

Writes data/findings.json after every app, so a crash or rate-limit resumes
where it left off (already-done ids are skipped unless --force).
"""
from __future__ import annotations

import argparse
import json
import sys
import time
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from schema import AppFinding  # noqa: E402
from agent.llm import get_backend  # noqa: E402
from agent.research import research_app  # noqa: E402
from agent.composio_check import composio_supported  # noqa: E402

OUT = ROOT / "data" / "findings.json"


def load_apps() -> list[tuple[dict, str]]:
    doc = yaml.safe_load((ROOT / "apps.yaml").read_text())
    rows = []
    for category, apps in doc["categories"].items():
        for app in apps:
            rows.append((app, category))
    return rows


def load_existing() -> dict[int, dict]:
    if OUT.exists():
        return {f["id"]: f for f in json.loads(OUT.read_text())["findings"]}
    return {}


def save(findings: dict[int, dict]) -> None:
    ordered = [findings[k] for k in sorted(findings)]
    OUT.write_text(json.dumps({"findings": ordered}, indent=2))


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ids", help="comma-separated app ids to (re)run")
    ap.add_argument("--no-ground", action="store_true", help="skip live doc fetch")
    ap.add_argument("--force", action="store_true", help="rerun even if already done")
    args = ap.parse_args()

    backend = get_backend()
    apps = load_apps()
    done = load_existing()
    only = {int(x) for x in args.ids.split(",")} if args.ids else None

    for app, category in apps:
        aid = app["id"]
        if only and aid not in only:
            continue
        if aid in done and not args.force:
            continue
        try:
            finding: AppFinding = research_app(app, category, backend, ground=not args.no_ground)
            finding.composio_supported = composio_supported(app["name"])
            done[aid] = finding.model_dump(mode="json")
            save(done)
            print(f"[{aid:>3}] {app['name']:<28} "
                  f"{finding.buildability.value:<15} conf={finding.confidence}")
        except Exception as e:  # keep going; a bad row should not kill the run
            print(f"[{aid:>3}] {app['name']:<28} ERROR: {e}", file=sys.stderr)
        time.sleep(0.5)  # be polite to free-tier rate limits

    print(f"\nWrote {len(done)} findings -> {OUT}")


if __name__ == "__main__":
    main()
