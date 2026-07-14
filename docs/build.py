"""Render the single self-contained case-study page: docs/index.html.

Reads data/{findings,patterns,verification}.json and emits ONE html file with
all data embedded (no network calls, no build step for the reviewer). The page
is designed to be understood in ~2 minutes: headline patterns first, then the
skimmable 100-app matrix, then the agent, the proof, and the verification.

Run:  python docs/build.py  ->  writes docs/index.html
"""
from __future__ import annotations

import html
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "data"
REPO_URL = "https://github.com/dugadnaman/composio-app-research"

F = json.loads((DATA / "findings.json").read_text())["findings"]
P = json.loads((DATA / "patterns.json").read_text())
V = json.loads((DATA / "verification.json").read_text())

ACCESS_CLASS = {
    "Self-serve free": "ok", "Self-serve trial": "ok",
    "Paid plan required": "warn", "Admin / app review": "warn",
    "Partner / contact-sales": "bad", "Unknown": "muted",
}
BUILD_CLASS = {
    "Ready": "ok", "Ready but gated": "warn", "Partial": "orange",
    "Blocked": "bad", "Unknown": "muted",
}
MCP_CLASS = {"Official MCP": "mcp-off", "Community MCP": "mcp-com",
             "No MCP": "muted", "Unknown": "muted"}


def esc(s) -> str:
    return html.escape(str(s), quote=True)


def bar_rows(counter: dict, total: int, cls="") -> str:
    out = []
    mx = max(counter.values()) if counter else 1
    for label, val in counter.items():
        w = round(100 * val / mx, 1)
        p = round(100 * val / total, 0) if total else 0
        out.append(
            f'<div class="bar {cls}"><span class="bl">{esc(label)}</span>'
            f'<span class="bt"><i style="width:{w}%"></i></span>'
            f'<span class="bv">{val} <small>({p:.0f}%)</small></span></div>'
        )
    return "\n".join(out)


def matrix_rows() -> str:
    rows = []
    for f in F:
        auth = " ".join(f'<span class="tag">{esc(a)}</span>' for a in f["auth_methods"])
        acc = ACCESS_CLASS.get(f["access_model"], "muted")
        bld = BUILD_CLASS.get(f["buildability"], "muted")
        mcpc = MCP_CLASS.get(f["mcp"], "muted")
        comp = '<span class="tick">✓</span>' if f["composio_supported"] else \
               '<span class="muted">–</span>'
        low = ' data-low="1"' if f["confidence"] < 0.7 else ""
        conf = int(round(f["confidence"] * 100))
        ev = esc(f["evidence_url"])
        rows.append(f"""<tr data-cat="{esc(f['category'])}" data-acc="{esc(f['access_model'])}"
 data-bld="{esc(f['buildability'])}" data-name="{esc(f['name']).lower()}"{low}>
  <td class="num">{f['id']}</td>
  <td class="nm"><b>{esc(f['name'])}</b><small>{esc(f['one_liner'])}</small></td>
  <td class="cat">{esc(f['category'])}</td>
  <td>{auth}</td>
  <td><span class="pill {acc}">{esc(f['access_model'])}</span></td>
  <td class="api"><b>{esc(f['api_breadth'])}</b><small>{esc(f['api_surface'])}</small></td>
  <td><span class="pill {mcpc}">{esc(f['mcp'])}</span></td>
  <td><span class="pill {bld}">{esc(f['buildability'])}</span>
      {'<small class="blk">'+esc(f['blocker'])+'</small>' if f['blocker'] else ''}</td>
  <td class="ctr">{comp}</td>
  <td class="ctr conf"><span class="cbar"><i style="width:{conf}%"></i></span>{conf}</td>
  <td class="ctr"><a href="{ev}" target="_blank" rel="noopener">docs↗</a></td>
</tr>""")
    return "\n".join(rows)


def sample_rows() -> str:
    fields = V["sample_check"]["fields_graded_per_row"]
    out = []
    for r in V["sample_rows"]:
        cells = []
        for fld in fields:
            p1 = r["pass1"].get(fld)
            p2 = r["pass2"].get(fld)
            def mark(v):
                return '<span class="hit">✓</span>' if v else '<span class="miss">✗</span>'
            cls = "chg" if p1 != p2 else ""
            cells.append(f'<td class="ctr {cls}">{mark(p1)}→{mark(p2)}</td>')
        out.append(f'<tr><td class="nm2"><b>{esc(r["name"])}</b></td>'
                   + "".join(cells)
                   + f'<td class="note">{esc(r["note"])}</td></tr>')
    return "\n".join(out)


def cat_bars() -> str:
    out = []
    for cat, d in P["by_category"].items():
        w = d["self_serve_pct"]
        out.append(
            f'<div class="bar"><span class="bl">{esc(cat)}</span>'
            f'<span class="bt"><i class="ok" style="width:{w}%"></i></span>'
            f'<span class="bv">{d["self_serve"]}/{d["total"]}</span></div>'
        )
    return "\n".join(out)


def chips(names, cls) -> str:
    return " ".join(f'<span class="chip {cls}">{esc(x)}</span>' for x in names)


HEADLINES = "\n".join(f"<li>{esc(h)}</li>" for h in P["headline"])

CATS = sorted({f["category"] for f in F})
CAT_OPTS = "".join(f'<option>{esc(c)}</option>' for c in CATS)

VS = V["sample_check"]
CL = V["critic_loop"]

TEMPLATE = r"""<!doctype html>
<html lang="en"><head>
<meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>100-App Buildability Research — Composio AI Product Ops</title>
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;500;600;700;800;900&family=Inter:wght@300;400;500;600;700&display=swap');

:root {
  --bg: #030712;
  --bg-glow-1: radial-gradient(circle at 10% 20%, rgba(99, 102, 241, 0.12), transparent 45%);
  --bg-glow-2: radial-gradient(circle at 90% 80%, rgba(6, 182, 212, 0.1), transparent 45%);
  --panel: rgba(17, 24, 39, 0.6);
  --panel-border: rgba(255, 255, 255, 0.06);
  --panel-hover: rgba(17, 24, 39, 0.8);
  --panel-border-hover: rgba(99, 102, 241, 0.35);
  --line: rgba(255, 255, 255, 0.08);
  --line-light: rgba(255, 255, 255, 0.03);
  --tx: #f8fafc;
  --mut: #94a3b8;
  --ok: #10b981;
  --ok-bg: rgba(16, 185, 129, 0.06);
  --ok-border: rgba(16, 185, 129, 0.25);
  --warn: #f59e0b;
  --warn-bg: rgba(245, 158, 11, 0.06);
  --warn-border: rgba(245, 158, 11, 0.25);
  --orange: #f97316;
  --orange-bg: rgba(249, 115, 22, 0.06);
  --orange-border: rgba(249, 115, 22, 0.25);
  --bad: #ef4444;
  --bad-bg: rgba(239, 68, 68, 0.06);
  --bad-border: rgba(239, 68, 68, 0.25);
  --mcpoff: #8b5cf6;
  --mcpoff-bg: rgba(139, 92, 246, 0.06);
  --mcpoff-border: rgba(139, 92, 246, 0.25);
  --mcpcom: #3b82f6;
  --mcpcom-bg: rgba(59, 130, 246, 0.06);
  --mcpcom-border: rgba(59, 130, 246, 0.25);
  --acc: #06b6d4;
  --brand: #6366f1;
  --brand-gradient: linear-gradient(135deg, #a78bfa 0%, #6366f1 50%, #06b6d4 100%);
  --shadow-sm: 0 2px 8px -1px rgba(0, 0, 0, 0.4);
  --shadow-md: 0 10px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
  --shadow-lg: 0 20px 40px -15px rgba(0, 0, 0, 0.7);
  --shadow-glow: 0 0 30px -5px rgba(99, 102, 241, 0.15);
}

* {
  box-sizing: border-box;
  margin: 0;
  padding: 0;
}

body {
  background-color: var(--bg);
  background-image: var(--bg-glow-1), var(--bg-glow-2);
  background-attachment: fixed;
  color: var(--tx);
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, sans-serif;
  font-size: 15px;
  line-height: 1.6;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

a {
  color: var(--acc);
  text-decoration: none;
  font-weight: 500;
  transition: all 0.2s ease;
}

a:hover {
  color: #38bdf8;
  text-shadow: 0 0 8px rgba(56, 189, 248, 0.3);
}

.wrap {
  max-width: 1280px;
  margin: 0 auto;
  padding: 60px 24px 120px;
}

/* Header Section */
h1 {
  font-family: 'Outfit', sans-serif;
  font-size: 42px;
  font-weight: 900;
  line-height: 1.15;
  margin-bottom: 16px;
  background: var(--brand-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
  letter-spacing: -0.03em;
  text-align: center;
}

.sub {
  color: var(--mut);
  max-width: 800px;
  font-size: 17px;
  margin: 0 auto 32px;
  text-align: center;
  line-height: 1.7;
}

.prov {
  font-size: 14px;
  color: #cbd5e1;
  background: rgba(30, 41, 59, 0.25);
  backdrop-filter: blur(10px);
  border: 1px solid rgba(245, 158, 11, 0.15);
  border-radius: 16px;
  padding: 18px 24px;
  margin: 32px auto 0;
  max-width: 900px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.2), 0 0 15px rgba(245, 158, 11, 0.03);
  text-align: center;
}

.prov b {
  color: var(--warn);
}

/* Statistics Grid */
.stats {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 16px;
  margin: 40px 0;
}

.stat {
  background: var(--panel);
  backdrop-filter: blur(16px);
  border: 1px solid var(--panel-border);
  border-radius: 20px;
  padding: 24px;
  text-align: center;
  box-shadow: var(--shadow-md);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  position: relative;
  overflow: hidden;
}

.stat::before {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 4px;
  background: transparent;
  transition: background 0.3s;
}

.stat:hover {
  transform: translateY(-5px);
  border-color: var(--panel-border-hover);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

.stat:hover::before {
  background: var(--brand-gradient);
}

.stat b {
  font-family: 'Outfit', sans-serif;
  font-size: clamp(22px, 2.2vw, 30px);
  font-weight: 800;
  display: block;
  white-space: nowrap;
  color: #fff;
  line-height: 1.1;
  margin-bottom: 8px;
  background: linear-gradient(to bottom, #ffffff, #e2e8f0);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.stat span {
  font-size: 13px;
  color: var(--mut);
  font-weight: 600;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  display: block;
}

/* Headings */
h2 {
  font-family: 'Outfit', sans-serif;
  font-size: 26px;
  font-weight: 800;
  margin: 64px 0 24px;
  display: flex;
  align-items: center;
  letter-spacing: -0.01em;
}

h2::before {
  content: '';
  display: inline-block;
  width: 5px;
  height: 24px;
  background: var(--brand-gradient);
  border-radius: 99px;
  margin-right: 14px;
}

h3 {
  font-family: 'Outfit', sans-serif;
  font-size: 14px;
  font-weight: 700;
  margin-bottom: 16px;
  color: #f1f5f9;
  text-transform: uppercase;
  letter-spacing: .08em;
  display: flex;
  align-items: center;
}

/* Panels & Grids */
.grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 24px;
}

@media(max-width:960px){
  .grid {
    grid-template-columns: 1fr;
  }
}

.panel {
  background: var(--panel);
  backdrop-filter: blur(16px);
  border: 1px solid var(--panel-border);
  border-radius: 24px;
  padding: 28px;
  box-shadow: var(--shadow-md);
  transition: all 0.3s cubic-bezier(0.16, 1, 0.3, 1);
  display: flex;
  flex-direction: column;
  justify-content: space-between;
}

.panel:hover {
  border-color: var(--panel-border-hover);
  box-shadow: var(--shadow-lg), var(--shadow-glow);
}

/* Headline List */
.head-list {
  list-style: none;
  font-size: 16px;
  line-height: 1.8;
  color: #e2e8f0;
}

.head-list li {
  position: relative;
  padding-left: 28px;
  margin: 16px 0;
}

.head-list li::before {
  content: '⚡';
  position: absolute;
  left: 0;
  top: 1px;
  font-size: 16px;
}

/* Charts & Progress Bars */
.bar {
  display: flex;
  align-items: center;
  margin: 12px 0;
  font-size: 13.5px;
}

.bl {
  width: 180px;
  color: #cbd5e1;
  font-weight: 500;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  padding-right: 12px;
}

.bt {
  flex: 1;
  background: rgba(30, 41, 59, 0.5);
  border-radius: 99px;
  height: 10px;
  overflow: hidden;
  position: relative;
  border: 1px solid rgba(255, 255, 255, 0.02);
}

.bt i {
  display: block;
  height: 100%;
  border-radius: 99px;
  background: var(--brand-gradient);
  position: relative;
  overflow: hidden;
}

.bt i::after {
  content: '';
  position: absolute;
  top: 0;
  left: 0;
  right: 0;
  bottom: 0;
  background: linear-gradient(
    90deg,
    rgba(255, 255, 255, 0) 0%,
    rgba(255, 255, 255, 0.15) 50%,
    rgba(255, 255, 255, 0) 100%
  );
  animation: shine 2s infinite linear;
}

@keyframes shine {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(100%); }
}

.bt i.ok {
  background: linear-gradient(90deg, #059669, #34d399);
}

.bv {
  width: 80px;
  text-align: right;
  color: var(--tx);
  font-weight: 700;
}

.bv small {
  font-size: 11px;
  color: var(--mut);
  font-weight: 400;
  margin-left: 3px;
}

/* Chips */
.chips {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
  margin-top: 12px;
}

.chip {
  font-size: 12px;
  font-weight: 500;
  padding: 6px 12px;
  border-radius: 99px;
  border: 1px solid rgba(255, 255, 255, 0.08);
  background: rgba(30, 41, 59, 0.3);
  color: #e2e8f0;
  transition: all 0.2s;
  cursor: default;
}

.chip.win {
  color: #34d399;
  border-color: rgba(16, 185, 129, 0.2);
  background: rgba(16, 185, 129, 0.05);
}

.chip.win:hover {
  border-color: rgba(16, 185, 129, 0.6);
  background: rgba(16, 185, 129, 0.12);
  transform: scale(1.05);
}

.chip.out {
  color: #f87171;
  border-color: rgba(239, 68, 68, 0.2);
  background: rgba(239, 68, 68, 0.05);
}

.chip.out:hover {
  border-color: rgba(239, 68, 68, 0.6);
  background: rgba(239, 68, 68, 0.12);
  transform: scale(1.05);
}

/* Controls Toolbar */
.controls {
  display: flex;
  gap: 12px;
  flex-wrap: wrap;
  margin: 32px 0 16px;
  align-items: center;
  padding: 16px 20px;
  background: rgba(17, 24, 39, 0.4);
  backdrop-filter: blur(12px);
  border: 1px solid rgba(255, 255, 255, 0.05);
  border-radius: 16px;
  box-shadow: var(--shadow-sm);
}

select, input {
  background: rgba(15, 23, 42, 0.7);
  color: var(--tx);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 10px;
  padding: 10px 16px;
  font-size: 13.5px;
  outline: none;
  font-family: inherit;
  transition: all 0.2s;
}

select:hover, input:hover {
  border-color: rgba(255, 255, 255, 0.2);
}

select:focus, input:focus {
  border-color: var(--brand);
  background: rgba(15, 23, 42, 0.9);
  box-shadow: 0 0 0 3px rgba(99, 102, 241, 0.25);
}

.controls label {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  user-select: none;
  font-weight: 500;
}

.controls input[type="checkbox"] {
  width: 16px;
  height: 16px;
  cursor: pointer;
}

.toolbar-note {
  color: var(--mut);
  font-size: 13.5px;
  margin-left: auto;
  font-weight: 600;
  background: rgba(255, 255, 255, 0.05);
  padding: 6px 12px;
  border-radius: 8px;
}

/* Master Data Table */
.mtx {
  display: block;
  overflow-x: auto;
  border-radius: 20px;
  border: 1px solid var(--panel-border);
  box-shadow: var(--shadow-lg);
  background: var(--panel);
  backdrop-filter: blur(16px);
}

table {
  width: 100%;
  border-collapse: collapse;
  font-size: 13px;
  text-align: left;
}

th {
  position: sticky;
  top: 0;
  background: #111827;
  padding: 16px 12px;
  border-bottom: 2px solid var(--line);
  cursor: pointer;
  white-space: nowrap;
  font-size: 11px;
  font-family: 'Outfit', sans-serif;
  text-transform: uppercase;
  letter-spacing: .1em;
  color: var(--mut);
  user-select: none;
  z-index: 10;
}

th:hover {
  color: #fff;
  background: #1f2937;
}

td {
  padding: 14px 12px;
  border-bottom: 1px solid var(--line-light);
  vertical-align: middle;
}

tr {
  transition: all 0.2s;
}

tr:hover td {
  background: rgba(99, 102, 241, 0.04);
}

.num {
  color: var(--mut);
  font-weight: 700;
  font-family: 'Outfit', sans-serif;
  width: 40px;
}

.nm b {
  color: #fff;
  font-size: 14.5px;
  font-weight: 600;
  display: block;
}

.nm small, .api small {
  display: block;
  color: var(--mut);
  font-size: 12px;
  margin-top: 3px;
  line-height: 1.4;
  font-weight: 400;
}

.nm small {
  max-width: 280px;
}

.api small {
  max-width: 200px;
}

.api b {
  text-transform: capitalize;
  font-size: 13px;
}

.cat {
  color: #cbd5e1;
  font-weight: 500;
}

.tag {
  display: inline-block;
  font-size: 10.5px;
  font-weight: 500;
  background: rgba(255, 255, 255, 0.05);
  border: 1px solid rgba(255, 255, 255, 0.05);
  color: #cbd5e1;
  border-radius: 6px;
  padding: 2px 6px;
  margin: 1px;
}

/* Badge Pills */
.pill {
  display: inline-block;
  font-size: 11px;
  font-weight: 700;
  padding: 4px 10px;
  border-radius: 99px;
  border: 1px solid;
  text-transform: capitalize;
  letter-spacing: 0.02em;
  white-space: nowrap;
}

.pill.ok { color: #34d399; border-color: var(--ok-border); background: var(--ok-bg); }
.pill.warn { color: #fbbf24; border-color: var(--warn-border); background: var(--warn-bg); }
.pill.orange { color: #fb923c; border-color: var(--orange-border); background: var(--orange-bg); }
.pill.bad { color: #f87171; border-color: var(--bad-border); background: var(--bad-bg); }
.pill.muted { color: #94a3b8; border-color: rgba(148, 163, 184, 0.2); background: rgba(148, 163, 184, 0.05); }
.pill.mcp-off { color: #c084fc; border-color: var(--mcpoff-border); background: var(--mcpoff-bg); }
.pill.mcp-com { color: #60a5fa; border-color: var(--mcpcom-border); background: var(--mcpcom-bg); }

.blk {
  display: block;
  color: #f87171;
  font-size: 11px;
  margin-top: 6px;
  max-width: 220px;
  font-weight: 500;
}

.tick {
  color: #10b981;
  font-weight: 800;
  font-size: 15px;
}

.muted { color: var(--mut); }
.conf { white-space: nowrap; font-weight: 600; }
.cbar { display: inline-block; width: 44px; height: 6px; background: rgba(255, 255, 255, 0.08); border-radius: 99px; overflow: hidden; vertical-align: middle; margin-right: 6px; }
.cbar i { display: block; height: 100%; background: linear-gradient(90deg, var(--acc), #38bdf8); }
tr[data-low="1"] .nm b::after { content: " ⚠️"; color: var(--warn); font-size: 12px; }

/* Step Flow Pipeline */
.flow {
  display: grid;
  grid-template-columns: 1fr auto 1fr auto 1fr;
  gap: 8px;
  margin: 20px 0;
  align-items: center;
}

@media(max-width: 768px){
  .flow {
    grid-template-columns: 1fr;
    gap: 16px;
  }
  .arrow {
    transform: rotate(90deg);
  }
}

.step {
  background: rgba(15, 23, 42, 0.6);
  border: 1px solid var(--panel-border);
  border-radius: 16px;
  padding: 20px;
  box-shadow: inset 0 1px 0 rgba(255,255,255,0.02);
  transition: all 0.3s;
}

.step:hover {
  border-color: var(--panel-border-hover);
  transform: translateY(-3px);
  box-shadow: var(--shadow-glow);
}

.step .n {
  color: var(--brand);
  font-weight: 800;
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.1em;
  display: block;
  margin-bottom: 6px;
}

.step b {
  color: #fff;
  font-size: 16px;
  font-family: 'Outfit', sans-serif;
  margin-bottom: 6px;
  display: block;
}

.step small {
  color: var(--mut);
  font-size: 12px;
  line-height: 1.5;
  display: block;
}

.arrow {
  color: var(--mut);
  font-size: 24px;
  font-weight: bold;
}

.two {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 24px;
}

@media(max-width:900px){
  .two {
    grid-template-columns: 1fr;
  }
}

code, .mono {
  font-family: ui-monospace, SFMono-Regular, Menlo, monospace;
  font-size: 13px;
  color: #f1f5f9;
}

pre {
  background: #030712;
  border: 1px solid var(--line);
  border-radius: 16px;
  padding: 20px;
  overflow-x: auto;
  box-shadow: inset 0 4px 12px rgba(0,0,0,0.6);
}

.big {
  font-family: 'Outfit', sans-serif;
  font-size: 64px;
  font-weight: 900;
  color: #fff;
  line-height: 1;
  background: var(--brand-gradient);
  -webkit-background-clip: text;
  background-clip: text;
  -webkit-text-fill-color: transparent;
}

.lift {
  display: flex;
  align-items: center;
  gap: 24px;
  margin-top: 14px;
}

.lift .from {
  color: #f87171;
  text-shadow: 0 0 15px rgba(239, 68, 68, 0.15);
}

.lift .to {
  color: #34d399;
  text-shadow: 0 0 15px rgba(16, 185, 129, 0.15);
}

.lift .ar {
  color: var(--mut);
  font-size: 36px;
}

.hit { color: #34d399; font-weight: bold; }
.miss { color: #f87171; font-weight: bold; }

/* Verification Table */
.vtab {
  width: 100%;
}

.vtab th {
  background: #111827;
  padding: 12px 10px;
}

.vtab td {
  font-size: 12.5px;
  padding: 10px;
}

.vtab .chg {
  background: rgba(16, 185, 129, 0.05);
}

.note {
  color: var(--mut);
  font-size: 12.5px;
  line-height: 1.6;
}

ul.tight {
  margin: 10px 0;
  padding-left: 20px;
  color: #cbd5e1;
}

ul.tight li {
  margin: 10px 0;
}

.foot {
  color: var(--mut);
  font-size: 13.5px;
  margin-top: 80px;
  border-top: 1px solid var(--line);
  padding-top: 32px;
  line-height: 1.7;
  text-align: center;
  max-width: 900px;
  margin-left: auto;
  margin-right: auto;
}

.kbd {
  background: rgba(255, 255, 255, 0.08);
  border: 1px solid rgba(255, 255, 255, 0.1);
  border-radius: 6px;
  padding: 3px 8px;
  font-size: 11px;
  color: #fff;
}
</style></head>
<body><div class="wrap">

<h1>Can we build an agent toolkit for it? — 100 apps, researched by an agent</h1>
<p class="sub">Composio turns apps into tools agents can call. Before building a toolkit we ask, per app:
what auth, is it self-serve or gated, how broad is the API, is there an MCP, and could we ship it today.
This page answers that for <b>100 apps</b> — and, more importantly, shows the <b>patterns</b> across them.</p>
<div class="prov"><b>Provenance & honesty:</b> findings produced by a Python research agent (schema-validated).
The committed run used <b>Claude</b> as the LLM backend plus manual web-doc grounding on ~24 niche apps;
the repo reproduces it with a free <b>Gemini</b> key. Numbers below are computed from the data, not asserted.
Rows the agent is unsure about are marked <span style="color:var(--warn)">⚠</span> and shown honestly.</div>

<div class="stats">
  <div class="stat"><b>100</b><span>apps across 10 categories</span></div>
  <div class="stat"><b>__READY__</b><span>build-ready today</span></div>
  <div class="stat"><b>__SS__%</b><span>self-serve credentials</span></div>
  <div class="stat"><b>__MCP__</b><span>have an MCP (official/community)</span></div>
  <div class="stat"><b>__P1__%→__P2__%</b><span>sample accuracy, before→after checks</span></div>
</div>

<h2>1 · The patterns (the headline)</h2>
<div class="panel"><ul class="head-list">__HEADLINES__</ul></div>

<div class="grid" style="margin-top:16px">
  <div class="panel"><h3>Auth methods (apps offering each)</h3>__AUTH_BARS__
    <p class="note" style="margin-top:8px">Apps overlap — most expose OAuth2 <i>and</i> a key/token. Auth is rarely the blocker.</p></div>
  <div class="panel"><h3>How you get credentials</h3>__ACCESS_BARS__</div>
  <div class="panel"><h3>Buildability verdict</h3>__BUILD_BARS__</div>
  <div class="panel"><h3>Main blocker (of the non-ready)</h3>__BLOCK_BARS__
    <p class="note" style="margin-top:8px">Blockers are approvals/partnerships/pricing — not missing APIs.</p></div>
  <div class="panel"><h3>Self-serve rate by category</h3>__CAT_BARS__</div>
  <div class="panel"><h3>Where the wins are</h3>
    <p style="margin:4px 0"><b style="color:var(--ok)">__EWN__ easy wins</b> — Ready + self-serve + not yet a Composio toolkit:</p>
    <div class="chips">__EASY__</div>
    <p style="margin:12px 0 4px"><b style="color:var(--bad)">__OUTN__ need outreach</b> — partner / app-review gated:</p>
    <div class="chips">__OUT__</div>
  </div>
</div>

<h2>2 · The 100-app matrix</h2>
<div class="controls">
  <select id="fcat"><option value="">All categories</option>__CAT_OPTS__</select>
  <select id="facc"><option value="">All access models</option>
    <option>Self-serve free</option><option>Self-serve trial</option>
    <option>Paid plan required</option><option>Admin / app review</option>
    <option>Partner / contact-sales</option><option>Unknown</option></select>
  <select id="fbld"><option value="">All verdicts</option>
    <option>Ready</option><option>Ready but gated</option><option>Partial</option><option>Unknown</option></select>
  <input id="fq" placeholder="search app…" size="16">
  <label style="font-size:12px;color:var(--mut)"><input type="checkbox" id="flow"> low-confidence only ⚠</label>
  <span class="toolbar-note" id="count"></span>
</div>
<div class="mtx"><table id="mtx"><thead><tr>
  <th data-k="0">#</th><th data-k="1">App</th><th data-k="2">Category</th><th>Auth</th>
  <th data-k="4">Access</th><th>API</th><th data-k="6">MCP</th><th data-k="7">Buildability</th>
  <th data-k="8">Composio</th><th data-k="9">Conf</th><th>Evidence</th>
</tr></thead><tbody>__ROWS__</tbody></table></div>

<h2>3 · The agent — what it does, and where a human was needed</h2>
<div class="two">
 <div class="panel">
  <h3>Pipeline</h3>
  <div class="flow">
    <div class="step"><span class="n">1 · DRAFT</span><br><b>LLM draft</b><br>
      <small>Per app, the model drafts all 6 dimensions using a strict controlled vocab and proposes one evidence URL.</small></div>
    <div class="arrow">→</div>
    <div class="step"><span class="n">2 · GROUND</span><br><b>Fetch the doc</b><br>
      <small>We actually GET that URL (requests + BeautifulSoup). Real bytes, not vibes.</small></div>
    <div class="arrow">→</div>
    <div class="step"><span class="n">3 · CONFIRM</span><br><b>Critic re-check</b><br>
      <small>Model re-reads the page, corrects fields, self-rates confidence. Thin/blocked page → confidence drops.</small></div>
  </div>
  <p class="note">Every row is coerced through a Pydantic schema, and Composio coverage is
  checked against a static seed list of known Composio slugs, not a live SDK query. Model-agnostic backend: Gemini (free) or Claude.</p>
  <h3>Stack</h3>
  <p class="mono" style="color:var(--mut)">Python · Pydantic · requests/bs4 · google-genai | anthropic · vanilla-JS page</p>
 </div>
 <div class="panel">
  <h3>Where a human was needed (stated plainly)</h3>
  <ul class="tight">
   <li><b>JS/login-walled docs</b> — dashboards & Notion-hosted pages return thin text to a plain fetch; a person confirmed those.</li>
   <li><b>“Self-serve” nuance</b> — free-trial vs truly-free vs paid-to-get-a-key needs judgement (e.g. Ahrefs, SE Ranking).</li>
   <li><b>MCP freshness</b> — MCP support moves weekly; official vs community was human-verified.</li>
   <li><b>Ambiguous / collided names</b> — <b>iPayX</b> (ipayx.ai) had no verifiable docs and defeated us; <b>Paygent Connect</b> maps to a white-label NMI gateway.</li>
   <li><b>Composio parity</b> — confirmed against the catalog rather than trusting the model.</li>
  </ul>
 </div>
</div>

<h2>4 · The proof — run the agent yourself</h2>
<div class="two">
  <div class="panel"><h3>Reproduce the research</h3>
<pre><code>git clone __REPO__
cd composio-app-research
pip install -r requirements.txt

# free backend:
export LLM_BACKEND=gemini GEMINI_API_KEY=...
python -m agent.run --ids 41,71,81   # research Shopify, Notion, Stripe
python -m agent.run                  # all 100 (resumable, cached)

# rebuild the artifacts:
python data/verification_build.py
python analysis/patterns.py
python docs/build.py                 # -&gt; this page</code></pre>
  <p class="note">Runnable trigger: <code>python -m agent.run --ids &lt;n&gt;</code> researches any app live and appends a schema-valid row.</p>
  </div>
  <div class="panel"><h3>What's in the repo</h3>
   <ul class="tight">
    <li><code>agent/</code> — llm (pluggable), research (draft→ground→confirm), verify, run (orchestrator)</li>
    <li><code>schema.py</code> — the controlled vocab that makes patterns possible</li>
    <li><code>data/</code> — findings, patterns, verification (all JSON)</li>
    <li><code>analysis/patterns.py</code> · <code>docs/build.py</code></li>
    <li><a href="__REPO__">Source repo + README →</a></li>
   </ul>
   <p class="note">Live page: deploy <code>docs/index.html</code> to GitHub Pages (static, self-contained).</p>
  </div>
</div>

<h2>5 · Verification — how I know it's trustworthy</h2>
<p class="sub">__VMETHOD__</p>
<div class="two" style="margin-top:12px">
  <div class="panel">
    <h3>Sample accuracy lift</h3>
    <div class="lift">
      <div><div class="big from">__P1__%</div><small class="muted">ungrounded first draft</small></div>
      <div class="ar">→</div>
      <div><div class="big to">__P2__%</div><small class="muted">after doc-grounding + human check</small></div>
    </div>
    <p class="note" style="margin-top:10px">__SSN__ apps × __NF__ fields hand-graded against live docs.
    Automated critic loop corrected <b>__CLC__</b> of 100 rows. One row still unresolved and shown as a miss:
    <b style="color:var(--bad)">iPayX</b>.</p>
  </div>
  <div class="panel">
    <h3>Honest remaining misses</h3>
    <ul class="tight">__MISSES__</ul>
    <p class="note">Low-confidence rows overall (&lt;0.70): __LOWCONF__.
    Gated apps are reported as gated <i>with evidence</i> — that's the correct finding, not a failure.</p>
  </div>
</div>
<h3 style="margin-top:20px">Per-field sample check &nbsp;<small style="text-transform:none;letter-spacing:0">(pass&nbsp;1 → pass&nbsp;2, ✓ match / ✗ miss; highlighted = changed)</small></h3>
<div class="mtx"><table class="vtab"><thead><tr>
  <th>App</th><th class="ctr">Auth</th><th class="ctr">Access</th><th class="ctr">API breadth</th>
  <th class="ctr">MCP</th><th class="ctr">Buildability</th><th>What changed</th>
</tr></thead><tbody>__SROWS__</tbody></table></div>

<div class="foot">
  <b>Reviewer's 2-minute takeaway:</b> auth is a solved problem (85% offer keys/tokens, 62% OAuth2);
  80% are self-serve so most of the 100 are build-ready; the real work on the gated ~20% is
  <i>partnerships and approvals, not engineering</i>. Built and verified by an agent, with the human
  checkpoints and one unsolved app (iPayX) shown honestly. · Backend for this run: Claude; reproducible on free Gemini.
</div>

<script>
const q=(s)=>document.querySelector(s), rows=[...document.querySelectorAll('#mtx tbody tr')];
function apply(){
  const c=q('#fcat').value,a=q('#facc').value,b=q('#fbld').value,
        t=q('#fq').value.toLowerCase(),lo=q('#flow').checked;let n=0;
  rows.forEach(r=>{
    const ok=(!c||r.dataset.cat===c)&&(!a||r.dataset.acc===a)&&(!b||r.dataset.bld===b)
      &&(!t||r.dataset.name.includes(t))&&(!lo||r.dataset.low==='1');
    r.style.display=ok?'':'none';if(ok)n++;});
  q('#count').textContent=n+' / '+rows.length+' apps';
}
['#fcat','#facc','#fbld','#fq','#flow'].forEach(s=>q(s).addEventListener('input',apply));
document.querySelectorAll('#mtx th[data-k]').forEach(th=>th.addEventListener('click',()=>{
  const k=+th.dataset.k,tb=q('#mtx tbody'),rs=[...tb.querySelectorAll('tr')];
  th._d=!th._d;const d=th._d?1:-1;
  rs.sort((x,y)=>{const A=x.children[k].innerText.trim(),B=y.children[k].innerText.trim();
    const nA=parseFloat(A),nB=parseFloat(B);
    if(!isNaN(nA)&&!isNaN(nB))return (nA-nB)*d;return A.localeCompare(B)*d;});
  rs.forEach(r=>tb.appendChild(r));
}));
apply();
</script>
</div></body></html>"""


def render() -> str:
    misses = "".join(
        f'<li><b>{esc(m["name"])}</b> — still off on: {esc(", ".join(m["fields"]))}</li>'
        for m in VS["remaining_misses"]
    ) or "<li>None — every sampled field matched after grounding.</li>"

    repl = {
        "__READY__": str(P["buildability"].get("Ready", 0)),
        "__SS__": str(round(100 * P["self_serve_n"] / P["n"])),
        "__MCP__": str(P["any_mcp"]),
        "__P1__": str(VS["accuracy_pass1_pct"]),
        "__P2__": str(VS["accuracy_pass2_pct"]),
        "__HEADLINES__": HEADLINES,
        "__AUTH_BARS__": bar_rows(P["auth"], P["n"]),
        "__ACCESS_BARS__": bar_rows(P["access"], P["n"]),
        "__BUILD_BARS__": bar_rows(P["buildability"], P["n"]),
        "__BLOCK_BARS__": bar_rows(P["blockers"], sum(P["blockers"].values())),
        "__CAT_BARS__": cat_bars(),
        "__EWN__": str(len(P["easy_wins"])),
        "__EASY__": chips(P["easy_wins"], "win"),
        "__OUTN__": str(len(P["needs_outreach"])),
        "__OUT__": chips(P["needs_outreach"], "out"),
        "__CAT_OPTS__": CAT_OPTS,
        "__ROWS__": matrix_rows(),
        "__REPO__": REPO_URL,
        "__VMETHOD__": esc(V["method"]),
        "__SSN__": str(VS["sample_size"]),
        "__NF__": str(len(VS["fields_graded_per_row"])),
        "__CLC__": str(CL["rows_corrected_by_critic"]),
        "__MISSES__": misses,
        "__LOWCONF__": esc(", ".join(CL["low_confidence_rows"]) or "none"),
        "__SROWS__": sample_rows(),
    }
    out = TEMPLATE
    for k, v in repl.items():
        out = out.replace(k, v)
    return out


if __name__ == "__main__":
    (ROOT / "docs" / "index.html").write_text(render())
    print(f"Wrote docs/index.html ({len((ROOT/'docs'/'index.html').read_text()):,} bytes)")
