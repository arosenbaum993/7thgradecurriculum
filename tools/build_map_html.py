#!/usr/bin/env python3
"""Render 7th_Grade_ELA_Curriculum_Map.md into two HTML pages.

  7th_Grade_ELA_Curriculum_Map.html        tile overview; each tile slides open a unit panel
  7th_Grade_ELA_Curriculum_Map_Print.html  the full document in reading order, for printing

Usage: python3 tools/build_map_html.py
Requires: pip install markdown
"""
import html as htmlmod
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "7th_Grade_ELA_Curriculum_Map.md"
OUT_TILES = ROOT / "7th_Grade_ELA_Curriculum_Map.html"
OUT_PRINT = ROOT / "7th_Grade_ELA_Curriculum_Map_Print.html"

FONTS = """<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Public+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">"""

TOKENS = """
:root{
  --bg:#F5F7F4; --surface:#FFFFFF; --ink:#1B2420; --muted:#5B6963; --line:#D6DDD8;
  --accent:#1B6B60; --accent-ink:#FFFFFF; --accent-soft:#DDEEE9; --accent-line:#9CCBC0;
  --gold:#9E7118; --gold-soft:#F4E9CF; --head-bg:#EAF1EE; --code-bg:#E7F0ED;
  --scrim:rgba(20,30,27,.42); --shadow:0 1px 0 rgba(27,36,32,.06);
  --tile-sat:34%; --tile-l:36%; --soft-sat:40%; --soft-l:93%;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#121917; --surface:#18221F; --ink:#E6ECE8; --muted:#A3B1AA; --line:#2B3833;
    --accent:#6FC7B5; --accent-ink:#0F1A17; --accent-soft:#173A34; --accent-line:#2F6B60;
    --gold:#D9AE4F; --gold-soft:#3A2E12; --head-bg:#1E2B27; --code-bg:#1D302B;
    --scrim:rgba(0,0,0,.55); --shadow:none;
    --tile-sat:38%; --tile-l:70%; --soft-sat:26%; --soft-l:17%;
  }
}
:root[data-theme="dark"]{
  --bg:#121917; --surface:#18221F; --ink:#E6ECE8; --muted:#A3B1AA; --line:#2B3833;
  --accent:#6FC7B5; --accent-ink:#0F1A17; --accent-soft:#173A34; --accent-line:#2F6B60;
  --gold:#D9AE4F; --gold-soft:#3A2E12; --head-bg:#1E2B27; --code-bg:#1D302B;
  --scrim:rgba(0,0,0,.55); --shadow:none;
  --tile-sat:38%; --tile-l:70%; --soft-sat:26%; --soft-l:17%;
}
"""

# Shared prose and table styling used inside panels and on the print page.
PROSE = """
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
h1,h2,h3,h4{font-family:"Newsreader","Iowan Old Style",Georgia,"Times New Roman",serif;font-weight:500;text-wrap:balance;letter-spacing:-.005em;line-height:1.15}
p{margin:0 0 14px}
p strong{font-weight:650}
a{color:var(--accent)}
code{font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;font-size:.82em;background:var(--code-bg);color:var(--ink);padding:1px 5px;border-radius:3px;white-space:nowrap}
ul,ol{margin:0 0 16px;padding-left:22px}
li{margin:0 0 6px}
li > p{margin:0}
.watch{border-left:3px solid var(--gold);background:var(--gold-soft);padding:12px 16px;border-radius:0 4px 4px 0}
.watch strong{color:var(--gold)}
.table-wrap{overflow-x:auto;margin:6px 0 22px;border:1px solid var(--line);border-radius:5px;background:var(--surface);box-shadow:var(--shadow)}
table{border-collapse:collapse;width:100%;font-size:14px;line-height:1.45;font-variant-numeric:tabular-nums}
th,td{text-align:left;vertical-align:top;padding:9px 12px;border-bottom:1px solid var(--line)}
th{background:var(--head-bg);font-weight:650;font-size:12.5px;letter-spacing:.02em;white-space:nowrap}
tbody tr:last-child td{border-bottom:0}
td:first-child{font-weight:550}
table.matrix td:not(:first-child),table.matrix th:not(:first-child){text-align:center;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:12.5px;width:48px}
table.matrix td:first-child{font-weight:450}
.meta strong{display:inline-block;font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;font-weight:500;font-size:12.5px;letter-spacing:.04em;color:var(--accent);background:var(--accent-soft);padding:4px 10px;border-radius:3px}
"""

PRINT_CSS = PROSE + """
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
.page{display:grid;grid-template-columns:248px minmax(0,1fr);max-width:1240px;margin:0 auto;padding:0 24px}
.index{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:36px 20px 36px 0;border-right:1px solid var(--line);font-size:13.5px}
.index .eyebrow{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.index ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
.index li a{display:block;padding:5px 10px;border-radius:4px;color:var(--ink);text-decoration:none;line-height:1.3}
.index li a:hover{background:var(--accent-soft)}
.index li a:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
main{padding:36px 0 96px 40px;min-width:0}
main > *{max-width:78ch}
main > .table-wrap{max-width:none}
h1{font-size:2.6rem;margin:0 0 10px}
h1 + p{font-size:.9rem;color:var(--muted);margin:0 0 18px;padding-bottom:18px;border-bottom:1px solid var(--line)}
h1 + p strong{color:var(--ink);font-weight:600}
h2{font-size:1.75rem;margin:56px 0 14px;padding-top:22px;border-top:2px solid var(--accent-line)}
h3{font-family:"Public Sans",system-ui,sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:30px 0 8px}
hr{border:0;height:0;margin:0}
.foot{margin-top:56px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
@media (max-width: 900px){
  .page{grid-template-columns:1fr;padding:0 16px}
  .index{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:24px 0 16px}
  .index ol{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
  main{padding:24px 0 72px}
  h1{font-size:2rem} h2{font-size:1.5rem}
}
@media print{
  body{background:#fff;color:#000;font-size:11pt}
  .page{display:block;max-width:none;padding:0}
  .index{display:none}
  main{padding:0} main > *{max-width:none}
  h2{break-before:page;border-top:0;margin-top:0;padding-top:0}
  h2:first-of-type{break-before:auto}
  .table-wrap{border:0;box-shadow:none;overflow:visible}
  table{font-size:9.5pt} tr,td,th{break-inside:avoid}
  .watch{border-left:3px solid #9E7118;background:#fff}
  code{background:#eee} a{color:inherit;text-decoration:none}
}
"""

TILES_CSS = PROSE + """
body{overflow-x:hidden}
.wrap{max-width:1180px;margin:0 auto;padding:40px 28px 80px}
.mast{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:24px;align-items:end;margin-bottom:28px}
.mast h1{font-size:2.4rem;margin:0 0 8px}
.mast .sub{color:var(--muted);margin:0;max-width:64ch}
.mast .print{font-size:13px;color:var(--muted);text-decoration:none;border:1px solid var(--line);padding:8px 12px;border-radius:4px;white-space:nowrap}
.mast .print:hover{border-color:var(--accent);color:var(--accent)}
.eyebrow{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 10px}

/* Year strip: 180 days, segments proportional to unit length */
.strip{margin:0 0 34px}
.strip .bar{display:flex;gap:3px;height:44px}
.strip .seg{flex:var(--days);--tile:hsl(var(--h) var(--tile-sat) var(--tile-l));--soft:hsl(var(--h) var(--soft-sat) var(--soft-l));background:var(--soft);border:0;border-radius:4px;border-bottom:3px solid var(--tile);color:var(--ink);font:inherit;font-size:12.5px;cursor:pointer;padding:0 8px;text-align:left;overflow:hidden;white-space:nowrap;text-overflow:ellipsis;transition:transform .18s ease,box-shadow .18s ease}
.strip .seg b{font-family:"JetBrains Mono",ui-monospace,monospace;font-weight:500;margin-right:6px;color:var(--tile)}
.strip .seg:hover,.strip .seg:focus-visible{transform:translateY(-2px);outline:2px solid var(--tile);outline-offset:1px}
.strip .seg.eog{border-bottom-color:var(--gold);--tile:var(--gold);--soft:var(--gold-soft)}
.strip .ticks{position:relative;height:18px;margin-top:6px;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11px;color:var(--muted)}
.strip .ticks span{position:absolute;top:0;transform:translateX(-50%)}
.strip .ticks span:first-child{transform:none}
.strip .ticks span:last-child{transform:translateX(-100%)}

/* Tiles */
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:14px;margin-bottom:40px}
.tile{--tile:hsl(var(--h) var(--tile-sat) var(--tile-l));--soft:hsl(var(--h) var(--soft-sat) var(--soft-l));display:flex;flex-direction:column;gap:8px;min-height:190px;text-align:left;font:inherit;color:var(--ink);background:var(--surface);border:1px solid var(--line);border-top:4px solid var(--tile);border-radius:6px;padding:16px 18px 14px;cursor:pointer;transition:transform .18s ease,box-shadow .18s ease,border-color .18s ease}
.tile:hover,.tile:focus-visible{transform:translateY(-3px);box-shadow:0 10px 24px -14px rgba(20,30,27,.45);border-color:var(--tile);outline:none}
.tile:focus-visible{outline:2px solid var(--tile);outline-offset:2px}
.tile .num{font-family:"Newsreader",Georgia,serif;font-size:2.1rem;line-height:1;color:var(--tile);font-weight:500}
.tile .num.small{font-size:1.35rem;padding-top:6px}
.tile .chip{white-space:nowrap;font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11.5px;letter-spacing:.03em;color:var(--tile);background:var(--soft);padding:3px 8px;border-radius:3px;align-self:flex-start}
.tile .top{display:flex;justify-content:space-between;align-items:flex-start;gap:8px}
.tile h2{font-size:1.15rem;margin:0;line-height:1.2}
.tile .mode{font-size:11.5px;letter-spacing:.07em;text-transform:uppercase;color:var(--muted);font-weight:600}
.tile .sum{font-size:13.5px;color:var(--muted);margin:0;display:-webkit-box;-webkit-line-clamp:3;-webkit-box-orient:vertical;overflow:hidden}
.tile .open{margin-top:auto;font-size:12.5px;color:var(--tile);font-weight:600}
.tile .open::after{content:" \\2192"}

.refs{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:10px}
.ref{display:flex;flex-direction:column;gap:4px;text-align:left;font:inherit;color:var(--ink);background:transparent;border:1px solid var(--line);border-radius:5px;padding:12px 14px;cursor:pointer;transition:border-color .18s ease,background .18s ease}
.ref:hover,.ref:focus-visible{border-color:var(--accent);background:var(--accent-soft);outline:none}
.ref:focus-visible{outline:2px solid var(--accent);outline-offset:2px}
.ref b{font-weight:600;font-size:14px}
.ref span{font-size:12.5px;color:var(--muted)}

/* Drawer */
.scrim{position:fixed;inset:0;background:var(--scrim);opacity:0;pointer-events:none;transition:opacity .28s ease;z-index:40}
.scrim.on{opacity:1;pointer-events:auto}
.drawer{position:fixed;top:0;right:0;height:100dvh;width:min(820px,94vw);background:var(--bg);border-left:1px solid var(--line);box-shadow:-24px 0 48px -32px rgba(0,0,0,.5);transform:translateX(104%);transition:transform .32s cubic-bezier(.2,.7,.2,1);z-index:50;display:flex;flex-direction:column;--tile:var(--accent);--soft:var(--accent-soft)}
.drawer.on{transform:none}
.drawer-head{display:flex;align-items:flex-start;gap:14px;padding:22px 26px 16px;border-bottom:1px solid var(--line);border-top:5px solid var(--tile);background:var(--surface)}
.drawer-head .chip{font-family:"JetBrains Mono",ui-monospace,monospace;font-size:11.5px;letter-spacing:.03em;color:var(--tile);background:var(--soft);padding:3px 8px;border-radius:3px;display:inline-block;margin-bottom:8px}
.drawer-head h2{font-size:1.5rem;margin:0}
.drawer-head .grow{flex:1;min-width:0}
.close{font:inherit;font-size:13px;color:var(--muted);background:transparent;border:1px solid var(--line);border-radius:4px;padding:7px 11px;cursor:pointer}
.close:hover,.close:focus-visible{border-color:var(--accent);color:var(--accent);outline:none}
.drawer-body{flex:1;overflow-y:auto;padding:22px 26px 32px}
.drawer-body > *{max-width:74ch}
.drawer-body > .table-wrap,.drawer-body > details{max-width:none}
.drawer-body h3{font-family:"Public Sans",system-ui,sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:26px 0 8px}
.drawer-body .meta{display:none}
details.grp{border:1px solid var(--line);border-radius:5px;background:var(--surface);margin:0 0 10px}
details.grp summary{cursor:pointer;list-style:none;padding:12px 16px;font-weight:600;font-size:14.5px;display:flex;align-items:center;gap:10px}
details.grp summary::-webkit-details-marker{display:none}
details.grp summary::before{content:"";width:8px;height:8px;border-right:2px solid var(--tile);border-bottom:2px solid var(--tile);transform:rotate(-45deg);transition:transform .2s ease;flex:none}
details.grp[open] summary::before{transform:rotate(45deg)}
details.grp summary:focus-visible{outline:2px solid var(--tile);outline-offset:-2px;border-radius:5px}
details.grp .inner{padding:2px 16px 12px;border-top:1px solid var(--line)}
details.grp .inner > *{max-width:74ch}
details.grp .inner > .table-wrap{max-width:none;border:0;border-radius:0;box-shadow:none;background:transparent;margin:8px 0 14px}
.drawer-nav{display:flex;justify-content:space-between;gap:10px;padding:12px 26px;border-top:1px solid var(--line);background:var(--surface)}
.drawer-nav button{font:inherit;font-size:13px;color:var(--ink);background:transparent;border:1px solid var(--line);border-radius:4px;padding:8px 12px;cursor:pointer;max-width:48%;text-align:left;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}
.drawer-nav button:hover,.drawer-nav button:focus-visible{border-color:var(--tile);color:var(--tile);outline:none}
.drawer-nav button:disabled{opacity:.35;cursor:default}
body.locked{overflow:hidden}
@media (prefers-reduced-motion: reduce){
  .drawer,.scrim,.tile,.strip .seg{transition:none}
}
@media (max-width: 640px){
  .wrap{padding:24px 16px 60px}
  .mast{grid-template-columns:1fr}
  .mast h1{font-size:1.9rem}
  .strip .seg{font-size:0;padding:0}
  .strip .seg b{font-size:12px;margin:0 6px}
  .drawer{width:100vw}
  .drawer-head,.drawer-body,.drawer-nav{padding-left:16px;padding-right:16px}
}
"""

# Descriptions shown on the reference tiles, keyed by section number.
REF_BLURBS = {
    1: "Calendar assumptions, priority versus supporting standards, what to do if the year is underway",
    2: "Every unit in one table: weeks, mode, summative, Milestones connection, GUM focus",
    3: "What the ALDs say: the 3-trait rubric, section-level tasks, tested GUM skills, the DOK ladder",
    4: "The daily and weekly writing spine that runs through every unit",
    5: "Every scored writing task in the year, week by week",
    14: "Every grade 7 expectation and the unit that carries it",
    15: "Each GUM skill with its code at grade 7, where it is taught, and whether it is tested",
    16: "What each unit plan needs under backward design, reading and writing, and rigor",
    17: "The short list that matters most",
}

UNIT_HUES = [168, 22, 205, 95, 350, 275, 40, 300]


def render_markdown():
    md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"], extension_configs={"toc": {"toc_depth": "2"}})
    body = md.convert(SRC.read_text(encoding="utf-8"))

    def wrap_table(m):
        table = m.group(0)
        cls = "matrix" if re.search(r"<th>U1</th>", table) else ""
        return f'<div class="table-wrap"><table class="{cls}">{table[len("<table>"):]}</div>'

    body = re.sub(r"<table>.*?</table>", wrap_table, body, flags=re.S)
    body = re.sub(r"<p><strong>Watch-outs?\.</strong>", '<p class="watch"><strong>Watch-outs.</strong>', body)
    body = re.sub(r"<p><strong>(Weeks? [^<]*)</strong></p>", r'<p class="meta"><strong>\1</strong></p>', body)
    toks = md.toc_tokens
    if len(toks) == 1 and toks[0].get("children"):
        toks = toks[0]["children"]
    return body, toks


def split_sections(body):
    """Return (preamble, [ {num, id, title, html} ]) split on h2."""
    parts = re.split(r'(?=<h2 id=")', body)
    pre = parts[0]
    secs = []
    for chunk in parts[1:]:
        m = re.match(r'<h2 id="([^"]+)">(.*?)</h2>(.*)', chunk, flags=re.S)
        sid, title, inner = m.group(1), m.group(2), m.group(3)
        inner = re.sub(r"<hr />\s*$", "", inner.strip())
        num = int(re.match(r"(\d+)\.", title).group(1))
        secs.append({"num": num, "id": sid, "title": re.sub(r"^\d+\.\s*", "", title), "html": inner})
    return pre, secs


def year_rows():
    """Rows of the year-at-a-glance table from the markdown source."""
    text = SRC.read_text(encoding="utf-8")
    sec = text.split("## 2. Year at a glance", 1)[1].split("\n## ", 1)[0]
    rows = []
    for line in sec.splitlines():
        if line.startswith("|") and not line.startswith("|---") and not line.startswith("| Unit"):
            cells = [c.strip() for c in line.strip().strip("|").split("|")]
            rows.append(dict(zip(["unit", "weeks", "days", "mode", "summative", "gm", "gum"], cells)))
    return rows


def group_unit_html(inner):
    """Intro paragraphs, the watch-out callout, then one collapsible group per h3."""
    watch = ""
    m = re.search(r'<p class="watch">.*?</p>', inner, flags=re.S)
    if m:
        watch = m.group(0)
        inner = inner.replace(watch, "")
    pieces = re.split(r'(?=<h3 id=")', inner)
    intro = pieces[0]
    groups = []
    for i, chunk in enumerate(pieces[1:]):
        m = re.match(r'<h3 id="[^"]+">(.*?)</h3>(.*)', chunk, flags=re.S)
        title, content = m.group(1), m.group(2).strip()
        opened = " open" if i == 0 else ""
        groups.append(f'<details class="grp"{opened}><summary>{title}</summary><div class="inner">{content}</div></details>')
    return intro + watch + "".join(groups)


def build_print(pre, toks, body):
    items = []
    for tok in toks:
        short = re.sub(r"^\d+\.\s*", "", tok["name"])
        short = re.sub(r"^(Unit \d+)\. ", r"\1 · ", short)
        short = re.sub(r"^Weeks 34 to 36\. ", "Weeks 34 to 36 · ", short)
        items.append(f'<li><a href="#{tok["id"]}">{short}</a></li>')
    return f"""<title>Grade 7 ELA Writing Map, print edition</title>
{FONTS}
<style>{TOKENS}{PRINT_CSS}</style>
<div class="page">
<nav class="index" aria-label="Sections"><p class="eyebrow">Sections</p><ol>{''.join(items)}</ol></nav>
<main>
{body}
<p class="foot">Sources: Georgia's K-12 ELA Standards, 7th Grade (approved May 2023) and the Georgia Milestones Grade 7 ELA Achievement Level Descriptors (draft, October 2025, effective 2025-2026). Source of truth is 7th_Grade_ELA_Curriculum_Map.md in the curriculum repository.</p>
</main>
</div>
"""


def build_tiles(pre, secs):
    rows = year_rows()
    units = [s for s in secs if re.match(r"^(Unit \d+\.|Weeks )", s["title"])]
    refs = [s for s in secs if s not in units]
    assert len(units) == len(rows) == 8, (len(units), len(rows))

    seg_html, tile_html, panel_html, nav_labels = [], [], [], []
    for i, (u, r) in enumerate(zip(units, rows)):
        hue = UNIT_HUES[i]
        is_unit = u["title"].startswith("Unit")
        num = re.match(r"Unit (\d+)", u["title"]).group(1) if is_unit else "EOG"
        title = re.sub(r"^Unit \d+\.\s*|^Weeks 34 to 36\.\s*", "", u["title"])
        chip = f"Weeks {r['weeks']} · {r['days']} days"
        pid = f"unit-{num.lower()}"
        eog = " eog" if not is_unit else ""
        seg_label = "Capstone" if not is_unit else title.split(":")[0]
        seg_html.append(f'<button class="seg{eog}" style="--h:{hue};--days:{r["days"]}" data-open="{pid}" title="{htmlmod.escape(u["title"])}"><b>{num}</b>{htmlmod.escape(seg_label)}</button>')
        tile_html.append(f"""<button class="tile" style="--h:{hue}" data-open="{pid}" id="tile-{pid}">
<div class="top"><span class="num{' small' if not is_unit else ''}">{num}</span><span class="chip">{chip}</span></div>
<h2>{htmlmod.escape(title)}</h2>
<span class="mode">{htmlmod.escape(r['mode'])}</span>
<p class="sum">{htmlmod.escape(r['summative'])}</p>
<span class="open">Open unit</span>
</button>""")
        grouped = group_unit_html(u["html"]) if is_unit else u["html"]
        panel_html.append(f'<template id="panel-{pid}" data-title="{htmlmod.escape(u["title"])}" data-chip="{chip}" data-hue="{hue}" data-kind="unit">{grouped}</template>')
        nav_labels.append((pid, u["title"]))

    ref_html = []
    for s in refs:
        pid = f"ref-{s['num']}"
        blurb = REF_BLURBS.get(s["num"], "")
        ref_html.append(f'<button class="ref" data-open="{pid}" id="tile-{pid}"><b>{htmlmod.escape(s["title"])}</b><span>{htmlmod.escape(blurb)}</span></button>')
        panel_html.append(f'<template id="panel-{pid}" data-title="{htmlmod.escape(s["title"])}" data-chip="Reference" data-kind="ref">{s["html"]}</template>')

    order = [p for p, _ in nav_labels]
    titles = {p: t for p, t in nav_labels}
    ticks = '<span>Aug · Q1</span><span style="left:25%">Q2</span><span style="left:50%">Q3</span><span style="left:75%">Q4</span><span style="left:100%">May</span>'

    js = r"""
(function(){
  var order = ORDER, titles = TITLES;
  var drawer = document.getElementById('drawer'), scrim = document.getElementById('scrim');
  var body = document.getElementById('drawer-body'), head = document.getElementById('drawer-title');
  var chip = document.getElementById('drawer-chip'), prev = document.getElementById('prev'), next = document.getElementById('next');
  var current = null, lastFocus = null;
  function open(id, push){
    var t = document.getElementById('panel-' + id); if(!t) return;
    current = id;
    body.innerHTML = ''; body.appendChild(t.content.cloneNode(true)); body.scrollTop = 0;
    head.textContent = t.dataset.title; chip.textContent = t.dataset.chip;
    if(t.dataset.hue){ drawer.style.setProperty('--tile','hsl(' + t.dataset.hue + ' var(--tile-sat) var(--tile-l))'); drawer.style.setProperty('--soft','hsl(' + t.dataset.hue + ' var(--soft-sat) var(--soft-l))'); }
    else { drawer.style.removeProperty('--tile'); drawer.style.removeProperty('--soft'); }
    var i = order.indexOf(id);
    prev.disabled = i <= 0; next.disabled = i < 0 || i >= order.length - 1;
    prev.textContent = i > 0 ? '← ' + titles[order[i-1]] : '←';
    next.textContent = (i >= 0 && i < order.length - 1) ? titles[order[i+1]] + ' →' : '→';
    drawer.classList.add('on'); scrim.classList.add('on'); document.body.classList.add('locked');
    drawer.setAttribute('aria-hidden','false');
    if(push !== false){ try{ history.pushState({id:id}, '', '#' + id); }catch(e){} }
    document.getElementById('close').focus();
  }
  function close(push){
    drawer.classList.remove('on'); scrim.classList.remove('on'); document.body.classList.remove('locked');
    drawer.setAttribute('aria-hidden','true'); current = null;
    if(push !== false){ try{ history.pushState({}, '', location.pathname + location.search); }catch(e){} }
    if(lastFocus){ lastFocus.focus(); lastFocus = null; }
  }
  document.querySelectorAll('[data-open]').forEach(function(b){
    b.addEventListener('click', function(){ lastFocus = b; open(b.dataset.open); });
  });
  document.getElementById('close').addEventListener('click', function(){ close(); });
  scrim.addEventListener('click', function(){ close(); });
  prev.addEventListener('click', function(){ var i = order.indexOf(current); if(i > 0) open(order[i-1]); });
  next.addEventListener('click', function(){ var i = order.indexOf(current); if(i >= 0 && i < order.length-1) open(order[i+1]); });
  document.addEventListener('keydown', function(e){
    if(!current) return;
    if(e.key === 'Escape') close();
    if(e.key === 'ArrowRight' && !next.disabled && e.target === document.body) next.click();
    if(e.key === 'ArrowLeft' && !prev.disabled && e.target === document.body) prev.click();
  });
  window.addEventListener('popstate', function(e){
    var id = (e.state && e.state.id) || (location.hash ? location.hash.slice(1) : null);
    if(id && document.getElementById('panel-' + id)) open(id, false); else if(current) close(false);
  });
  var h = location.hash ? location.hash.slice(1) : null;
  if(h && document.getElementById('panel-' + h)){ var b = document.getElementById('tile-' + h); lastFocus = b; open(h, false); }
})();
"""
    import json
    js = js.replace("ORDER", json.dumps(order)).replace("TITLES", json.dumps(titles))

    return f"""<title>Grade 7 ELA Writing Map</title>
{FONTS}
<style>{TOKENS}{TILES_CSS}</style>
<div class="wrap">
<header class="mast">
<div>
<p class="eyebrow">McIntosh County · Georgia's 2023 ELA Standards · Grade 7 Milestones ALDs</p>
<h1>Grade 7 ELA Writing Map</h1>
<p class="sub">A writing-centered year in eight blocks. Open a tile for that unit's standards, success-criteria ladder, assessments, mentor texts, and weekly arc. The reference tiles below hold the Milestones target, the routines, and the coverage tables.</p>
</div>
<a class="print" href="7th_Grade_ELA_Curriculum_Map.pdf">Print edition (PDF)</a>
</header>

<section class="strip" aria-label="Year at a glance">
<p class="eyebrow">The year, 180 days, drawn to scale</p>
<div class="bar">{''.join(seg_html)}</div>
<div class="ticks">{ticks}</div>
</section>

<section aria-label="Units">
<p class="eyebrow">Units</p>
<div class="grid">{''.join(tile_html)}</div>
</section>

<section aria-label="Reference">
<p class="eyebrow">Reference</p>
<div class="refs">{''.join(ref_html)}</div>
</section>
</div>

<div class="scrim" id="scrim"></div>
<aside class="drawer" id="drawer" role="dialog" aria-modal="true" aria-labelledby="drawer-title" aria-hidden="true">
<div class="drawer-head"><div class="grow"><span class="chip" id="drawer-chip"></span><h2 id="drawer-title"></h2></div><button class="close" id="close" type="button">Close</button></div>
<div class="drawer-body" id="drawer-body"></div>
<div class="drawer-nav"><button id="prev" type="button">←</button><button id="next" type="button">→</button></div>
</aside>
{''.join(panel_html)}
<script>{js}</script>
"""


if __name__ == "__main__":
    body, toks = render_markdown()
    pre, secs = split_sections(body)
    OUT_PRINT.write_text(build_print(pre, toks, body), encoding="utf-8")
    OUT_TILES.write_text(build_tiles(pre, secs), encoding="utf-8")
    for p in (OUT_TILES, OUT_PRINT):
        print(f"wrote {p.name} ({p.stat().st_size:,} bytes)")
