#!/usr/bin/env python3
"""Render 7th_Grade_ELA_Curriculum_Map.md into a self-contained HTML page.

Usage: python3 tools/build_map_html.py
Requires: pip install markdown
"""
import re
from pathlib import Path

import markdown

ROOT = Path(__file__).resolve().parent.parent
SRC = ROOT / "7th_Grade_ELA_Curriculum_Map.md"
OUT = ROOT / "7th_Grade_ELA_Curriculum_Map.html"

md = markdown.Markdown(extensions=["tables", "toc", "sane_lists"], extension_configs={"toc": {"toc_depth": "2"}})
body = md.convert(SRC.read_text(encoding="utf-8"))

# Tables scroll inside their own container; coverage matrices get centered cells.
def wrap_table(m):
    table = m.group(0)
    cls = "matrix" if re.search(r"<th>U1</th>", table) else ""
    return f'<div class="table-wrap"><table class="{cls}">{table[len("<table>"):]}</div>'
body = re.sub(r"<table>.*?</table>", wrap_table, body, flags=re.S)

# Watch-out paragraphs get a marked treatment.
body = re.sub(r'<p><strong>Watch-outs?\.</strong>', '<p class="watch"><strong>Watch-outs.</strong>', body)
# Unit week lines become a mono eyebrow chip.
body = re.sub(r'<p><strong>(Weeks? [^<]*)</strong></p>', r'<p class="meta"><strong>\1</strong></p>', body)

# Section index from h2 headings.
items = []
toks = md.toc_tokens
if len(toks) == 1 and toks[0].get("children"):
    toks = toks[0]["children"]
for tok in toks:
    name = tok["name"]
    short = re.sub(r"^\d+\.\s*", "", name)
    short = re.sub(r"^(Unit \d+)\. ", r"\1 · ", short)
    short = re.sub(r"^Weeks 34 to 36\. ", "Weeks 34 to 36 · ", short)
    items.append(f'<li><a href="#{tok["id"]}">{short}</a></li>')
nav = "\n".join(items)

CSS = r"""
:root{
  --bg:#F5F7F4; --surface:#FFFFFF; --ink:#1B2420; --muted:#5B6963; --line:#D6DDD8;
  --accent:#1B6B60; --accent-ink:#FFFFFF; --accent-soft:#DDEEE9; --accent-line:#9CCBC0;
  --gold:#9E7118; --gold-soft:#F4E9CF; --head-bg:#EAF1EE; --code-bg:#E7F0ED;
  --shadow:0 1px 0 rgba(27,36,32,.06);
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#121917; --surface:#18221F; --ink:#E6ECE8; --muted:#A3B1AA; --line:#2B3833;
    --accent:#6FC7B5; --accent-ink:#0F1A17; --accent-soft:#173A34; --accent-line:#2F6B60;
    --gold:#D9AE4F; --gold-soft:#3A2E12; --head-bg:#1E2B27; --code-bg:#1D302B;
    --shadow:none;
  }
}
:root[data-theme="dark"]{
  --bg:#121917; --surface:#18221F; --ink:#E6ECE8; --muted:#A3B1AA; --line:#2B3833;
  --accent:#6FC7B5; --accent-ink:#0F1A17; --accent-soft:#173A34; --accent-line:#2F6B60;
  --gold:#D9AE4F; --gold-soft:#3A2E12; --head-bg:#1E2B27; --code-bg:#1D302B;
  --shadow:none;
}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
@media (prefers-reduced-motion: reduce){html{scroll-behavior:auto}}
body{margin:0;background:var(--bg);color:var(--ink);font-family:"Public Sans",system-ui,-apple-system,"Segoe UI",Roboto,sans-serif;font-size:16px;line-height:1.55;-webkit-font-smoothing:antialiased}
.page{display:grid;grid-template-columns:248px minmax(0,1fr);gap:0;max-width:1240px;margin:0 auto;padding:0 24px}
.index{position:sticky;top:0;align-self:start;height:100vh;overflow-y:auto;padding:36px 20px 36px 0;border-right:1px solid var(--line);font-size:13.5px}
.index .eyebrow{font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);margin:0 0 12px}
.index ol{list-style:none;margin:0;padding:0;display:flex;flex-direction:column;gap:2px}
.index li a{display:block;padding:5px 10px;border-radius:4px;color:var(--ink);text-decoration:none;line-height:1.3}
.index li a:hover{background:var(--accent-soft)}
.index li a:focus-visible{outline:2px solid var(--accent);outline-offset:1px}
main{padding:36px 0 96px 40px;min-width:0}
main > *{max-width:78ch}
main > .table-wrap{max-width:none}
h1,h2,h3,h4{font-family:"Newsreader","Iowan Old Style",Georgia,"Times New Roman",serif;font-weight:500;text-wrap:balance;letter-spacing:-.005em;line-height:1.15}
h1{font-size:2.6rem;margin:0 0 10px;font-weight:500}
h1 + p{font-size:.9rem;color:var(--muted);margin:0 0 18px;padding-bottom:18px;border-bottom:1px solid var(--line)}
h1 + p strong{color:var(--ink);font-weight:600}
h2{font-size:1.75rem;margin:56px 0 14px;padding-top:22px;border-top:2px solid var(--accent-line)}
.meta strong{display:inline-block;font-family:"JetBrains Mono",ui-monospace,Menlo,Consolas,monospace;font-weight:500;font-size:12.5px;letter-spacing:.04em;color:var(--accent);background:var(--accent-soft);padding:4px 10px;border-radius:3px}
h3{font-family:"Public Sans",system-ui,sans-serif;font-size:.78rem;font-weight:700;letter-spacing:.09em;text-transform:uppercase;color:var(--muted);margin:30px 0 8px}
p{margin:0 0 14px}
p strong{font-weight:650}
hr{border:0;height:0;margin:0}
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
.foot{margin-top:56px;padding-top:16px;border-top:1px solid var(--line);color:var(--muted);font-size:13px}
@media (max-width: 900px){
  .page{grid-template-columns:1fr;padding:0 16px}
  .index{position:static;height:auto;border-right:0;border-bottom:1px solid var(--line);padding:24px 0 16px}
  .index ol{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr))}
  main{padding:24px 0 72px}
  h1{font-size:2rem}
  h2{font-size:1.5rem}
}
@media print{
  body{background:#fff;color:#000;font-size:11pt}
  .page{display:block;max-width:none;padding:0}
  .index{display:none}
  main{padding:0}
  main > *{max-width:none}
  h2{break-before:page;border-top:0;margin-top:0;padding-top:0}
  h1 + h2, h2:first-of-type{break-before:auto}
  .table-wrap{border:0;box-shadow:none;overflow:visible}
  table{font-size:9.5pt}
  tr,td,th{break-inside:avoid}
  .watch{border-left:3px solid #9E7118;background:#fff}
  code{background:#eee}
  a{color:inherit;text-decoration:none}
}
"""

html = f"""<title>Grade 7 ELA Writing Map</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Newsreader:opsz,wght@6..72,400;6..72,500;6..72,600&family=Public+Sans:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap">
<style>{CSS}</style>
<div class="page">
<nav class="index" aria-label="Sections">
<p class="eyebrow">Sections</p>
<ol>
{nav}
</ol>
</nav>
<main>
{body}
<p class="foot">Sources: Georgia's K-12 ELA Standards, 7th Grade (approved May 2023) and the Georgia Milestones Grade 7 ELA Achievement Level Descriptors (draft, October 2025, effective 2025-2026). Source of truth for this page is 7th_Grade_ELA_Curriculum_Map.md in the curriculum repository.</p>
</main>
</div>
"""
OUT.write_text(html, encoding="utf-8")
print(f"wrote {OUT} ({OUT.stat().st_size:,} bytes)")
