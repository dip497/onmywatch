"""Build a show-me page from a small JSON spec, then check it.

Usage: python3 build.py page.json [out.html] [--open-all] [--no-render]
--open-all writes every step open and every view visible, for review screenshots.
--no-render skips render.py (the measured check in Chrome and the screenshots).
A spec with "panels" builds a one-screen sheet. A spec with "views" builds a walkthrough:
tabs, one guided tour of steps per tab. A spec with "flows" builds flow pages: screens and
decisions joined by labelled links, with zoom, review marks and a full-size view (see flow.py).
Writes out.html (default: next to the JSON) with the CSS inlined, runs check.py, then render.py,
which opens the page in headless Chrome, measures it and saves screenshots in shots/ beside the
spec. Exits 1 on any ERROR.

The spec is the only source. Extra styles go in its "css" key and a part the builder lacks goes in
an "html" exhibit, so both survive a rebuild. The page records a hash of itself; if someone edits
it by hand, the next build stops instead of throwing the edit away.
"""
import hashlib
import json
import re
import subprocess
import sys
from html import escape as e
from pathlib import Path

sys.dont_write_bytecode = True
import diagrams  # noqa: E402
import flow as flow_pages  # noqa: E402
from graph_layout import columns, find_returns  # noqa: E402

HERE = Path(__file__).resolve().parent
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">')
CONFIDENCE = ("direct", "supported", "inferred", "unknown")
warnings = []


def code(text):
    """`x` in spec text becomes <code>x</code>."""
    parts = e(text).split("`")
    return "".join(f"<code>{p}</code>" if i % 2 else p for i, p in enumerate(parts))


def tree(t):
    items = "".join(f"<li>{code(i[0])}<small>{code(i[1])}</small></li>" if len(i) > 1 else f"<li>{code(i[0])}</li>"
                    for i in t["items"])
    sub = f"<small>{code(t['sub'])}</small>" if t.get("sub") else ""
    return f'<div class="tree"><div class="root"><b>{code(t["root"])}</b>{sub}</div><ul>{items}</ul></div>'


def anno(parts):
    out = []
    for p in parts:
        kind = {"note": " n", "wrong": " x"}.get(p.get("kind", "note" if p.get("why") else ""), "")
        why = f'<span class="why">{e(p["why"])}</span>' if p.get("why") else ""
        out.append(f'<span class="seg{kind}"><span class="t">{e(p["text"])}</span>{why}</span>')
    return f'<div class="anno">{"".join(out)}</div>'


def cell(c):
    for mark in ("ok", "bad"):
        if c.startswith(mark + ":"):
            return f'<td class="{mark}">{code(c[len(mark) + 1:].strip())}</td>'
    return f"<td>{code(c)}</td>"


def table(t):
    head = "".join(f"<th>{code(h)}</th>" for h in t["head"])
    rows = "".join("<tr>" + "".join(cell(c) for c in r) + "</tr>" for r in t["rows"])
    return f'<div class="scroll"><table><tr>{head}</tr>{rows}</table></div>'


def limits(ls):
    return "".join(f'<div class="limit"><div class="lab">{code(l["label"])}<b>{e(l["value"])}</b></div>'
                   f'<div class="track"><i style="width:{max(0, min(100, l["pct"]))}%"></i></div></div>' for l in ls)


def flow(steps):
    boxes = [f'<span class="box{" new" if s.get("new") else ""}">{code(s["text"])}</span>' for s in steps]
    return '<div class="flow">' + '<span class="arrow">→</span>'.join(boxes) + "</div>"


def timeline(ts):
    return '<div class="timeline">' + "".join(f"<div><b>{e(a)}</b>{e(b)}</div>" for a, b in ts) + "</div>"


def path(ps):
    """An ordered trace through a thing: where each step happens, what it does, what it passes on."""
    rows = []
    for i, p in enumerate(ps, 1):
        if not p.get("where"):
            sys.exit(f"path step {i} has no 'where'")
        passes = f'<span class="passes">passes {code(p["passes"])}</span>' if p.get("passes") else ""
        rows.append(f'<li><span class="where">{code(p["where"])}</span><span class="what">{code(p["what"])}</span>{passes}</li>')
    return f'<ol class="path">{"".join(rows)}</ol>'


def decisions(ds):
    rows = []
    for d in ds:
        conf = d.get("confidence", "").lower()
        if conf not in CONFIDENCE:
            sys.exit(f"decision '{d.get('choice')}' needs confidence: one of {', '.join(CONFIDENCE)}")
        if conf != "unknown" and not d.get("source"):
            sys.exit(f"decision '{d.get('choice')}' needs a source, or confidence 'unknown'")
        over = "".join(f"<li>{code(o)}</li>" for o in d.get("over", []))
        over = f'<div class="over"><span>Not chosen</span><ul>{over}</ul></div>' if over else ""
        src = f'<div class="src">Source: {code(d["source"])}</div>' if d.get("source") else ""
        rows.append(f'<div class="decision"><div class="dhead"><b>{code(d["choice"])}</b>'
                    f'<span class="conf {conf}">{conf}</span></div>{over}'
                    f'<p>{code(d.get("why", "No reason found."))}</p>{src}</div>')
    return f'<div class="decisions">{"".join(rows)}</div>'


def gaps(gs):
    """What could not be found or traced, and who could answer it."""
    rows = "".join(f'<li><b>{code(g["question"])}</b>'
                   + (f'<span class="looked">Looked in: {code(g["looked"])}</span>' if g.get("looked") else "")
                   + (f'<span class="ask">Ask: {code(g["ask"])}</span>' if g.get("ask") else "") + "</li>" for g in gs)
    return f'<ul class="gaps">{rows}</ul>'


def snippet(c):
    text = c["text"].rstrip("\n")
    where = f'<div class="where">{code(c["where"])}</div>' if c.get("where") else ""
    block = f'<pre class="code"><code>{e(text)}</code></pre>'
    if text.count("\n") >= 12:
        block = f"<details><summary>Show {text.count(chr(10)) + 1} lines</summary>{block}</details>"
    return where + block


# ---------- diagram: grid layout, routes that avoid boxes ----------

def _hits(seg, r, pad=4):
    (x1, y1), (x2, y2) = seg
    rx, ry, rw, rh = r[0] - pad, r[1] - pad, r[2] + 2 * pad, r[3] + 2 * pad
    if x1 == x2:
        lo, hi = sorted((y1, y2))
        return rx < x1 < rx + rw and lo < ry + rh and hi > ry
    lo, hi = sorted((x1, x2))
    return ry < y1 < ry + rh and lo < rx + rw and hi > rx


def _clear(points, others):
    segs = list(zip(points, points[1:]))
    return not any(_hits(s, r) for s in segs for r in others)


# More columns than this do not fit a panel at full size, so the layout runs top to bottom instead.
MAX_DIAGRAM_COLS = 4


def place_nodes(d, claim):
    """Nodes without `col` and `row` get them from the layered layout; a node may pin either one."""
    ids = [n["id"] for n in d["nodes"]]
    for ed in d["edges"]:
        for end in ("from", "to"):
            if ed[end] not in ids:
                sys.exit(f"diagram '{claim[:40]}': edge end '{ed[end]}' is not a node")
    if len(ids) > 9:
        warnings.append(f"diagram '{claim[:40]}': {len(ids)} boxes; above 9 it is probably two diagrams")
    if len(d["edges"]) > 12:
        warnings.append(f"diagram '{claim[:40]}': {len(d['edges'])} arrows; above 12, split it or drop the obvious ones")
    marked = sum(1 for x in d["nodes"] + d["edges"] if x.get("new"))
    if marked > 3:
        warnings.append(f"diagram '{claim[:40]}': {marked} parts marked new; blue only works on the one or two that matter")
    if all("col" in n and "row" in n for n in d["nodes"]):
        return d["nodes"]
    back, visit = find_returns(ids, d["edges"], [])
    pinned = {n["id"]: {k: n[k] for k in ("col", "row") if k in n} for n in d["nodes"]}
    col, cols, _ = columns(visit, d["edges"], back, pinned)
    placed = [{**n, "col": col[n["id"]], "row": cols[col[n["id"]]].index(n["id"])} for n in d["nodes"]]
    widest = max(len(c) for c in cols.values())
    if len(cols) > MAX_DIAGRAM_COLS and len(cols) > widest and not any(pinned.values()):
        placed = [{**n, "col": n["row"], "row": n["col"]} for n in placed]
    return placed


def diagram(d, claim):
    """Nodes sit on a grid (col, row). Each edge takes the first route that crosses no other box."""
    nodes = {n["id"]: n for n in place_nodes(d, claim)}
    char, pad, row_h, gap_x, gap_y = 9, 28, 64, 120, 80
    cols = max(n["col"] for n in nodes.values()) + 1
    rows = max(n["row"] for n in nodes.values()) + 1
    col_w = [110] * cols
    for n in nodes.values():
        col_w[n["col"]] = max(col_w[n["col"]], len(n["label"]) * char + pad, len(n.get("sub", "")) * 7.5 + pad)
    for ed in d["edges"]:
        gap_x = max(gap_x, min(len(ed.get("label", "")) * 8 + 40, 260))
    xs = [20 + sum(col_w[:c]) + gap_x * c for c in range(cols)]
    W = xs[-1] + col_w[-1] + 20
    H = 20 + rows * row_h + rows * gap_y

    def box(n):
        return xs[n["col"]], 20 + n["row"] * (row_h + gap_y), col_w[n["col"]], row_h

    pair_count, edges, labels, shapes = {}, [], [], []
    used_bottom = max(box(n)[1] + row_h for n in nodes.values())
    used_right = W
    for ed in d["edges"]:
        a, b = nodes[ed["from"]], nodes[ed["to"]]
        ax, ay, aw, ah = box(a)
        bx, by, bw, bh = box(b)
        others = [box(n) for k, n in nodes.items() if k not in (ed["from"], ed["to"])]
        key = tuple(sorted((ed["from"], ed["to"])))
        k = pair_count.get(key, 0)
        pair_count[key] = k + 1
        off = 24 * k
        acx, acy, bcx, bcy = ax + aw / 2, ay + ah / 2, bx + bw / 2, by + bh / 2
        right = bx > ax
        down = by > ay
        cands = []
        if a["row"] == b["row"]:
            y = acy + off
            cands.append([(ax + aw if right else ax, y), (bx if right else bx + bw, y)])
        if a["col"] == b["col"]:
            x = acx + off
            cands.append([(x, ay + ah if down else ay), (x, by if down else by + bh)])
        if a["row"] != b["row"] and a["col"] != b["col"]:
            cands.append([(ax + aw if right else ax, acy + off), (bcx + off, acy + off), (bcx + off, by if down else by + bh)])
            cands.append([(acx + off, ay + ah if down else ay), (acx + off, bcy + off), (bx if right else bx + bw, bcy + off)])
            gx = (bx - gap_x / 2 if right else bx + bw + gap_x / 2) + off
            cands.append([(ax + aw if right else ax, acy + off), (gx, acy + off), (gx, bcy + off), (bx if right else bx + bw, bcy + off)])
        for lane_y in (max(ay, by) + row_h + gap_y / 2 + off, min(ay, by) - gap_y / 2 + off):
            if 4 < lane_y < H - 4:
                sy = ay + ah if lane_y > ay else ay
                ey = by + bh if lane_y > by else by
                cands.append([(acx + off, sy), (acx + off, lane_y), (bcx + off, lane_y), (bcx + off, ey)])
        pts = next((c for c in cands if _clear(c, others)), None)
        if pts is None:
            pts = cands[0]
            warnings.append(f"diagram '{claim[:40]}': edge {ed['from']}→{ed['to']} crosses a box; move the nodes")
        new = " new" if ed.get("new") else ""
        dpath = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        edges.append(f'<path class="edge{new}" d="{dpath}" marker-end="url(#arrow)"/>')
        used_bottom = max([used_bottom] + [y for _, y in pts])
        if ed.get("label"):
            segs = list(zip(pts, pts[1:]))
            (x1, y1), (x2, y2) = max(segs, key=lambda s: abs(s[0][0] - s[1][0]) + abs(s[0][1] - s[1][1]))
            t = ed["label"]
            w = len(t) * 8 + 12
            if y1 == y2:
                lx, ly = (x1 + x2) / 2 - w / 2, (y1 - 6 if k == 0 else y1 + 20)
            else:
                lx, ly = (x1 + 8 if k == 0 else x1 - w - 8), (y1 + y2) / 2 + 5
            if any(_hits(((lx, ly - 7), (lx + w, ly - 7)), r, 0) for r in [box(n) for n in nodes.values()]):
                warnings.append(f"diagram '{claim[:40]}': label '{t}' overlaps a box; shorten it or move the nodes")
            used_right = max(used_right, lx + w + 12)
            labels.append(f'<rect class="mask" x="{lx:.0f}" y="{ly - 14:.0f}" width="{w}" height="19"/>'
                          f'<text class="elbl{new}" x="{lx + 6:.0f}" y="{ly:.0f}">{e(t)}</text>')
    for n in nodes.values():
        x, y, w, h = box(n)
        kinds = " ".join(k for k in ("new", "store") if n.get(k))
        cy = y + (h / 2 + 5 if not n.get("sub") else h / 2 - 3)
        shapes.append(f'<rect class="node {kinds}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
                      f'<text class="lbl" x="{x + w / 2}" y="{cy}" text-anchor="middle">{e(n["label"])}</text>')
        if n.get("sub"):
            shapes.append(f'<text class="sub" x="{x + w / 2}" y="{y + h / 2 + 16}" text-anchor="middle">{e(n["sub"])}</text>')
    H = used_bottom + 24
    W = used_right
    marker = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
              'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
    svg = (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{e(claim)}" style="min-width:{W * diagrams.MIN_SCALE:.0f}px;max-width:{W * 1.1:.0f}px">'
           f'{marker}{"".join(edges)}{"".join(labels)}{"".join(shapes)}</svg>')
    return f'<figure class="diagram"><div class="scroll">{svg}</div></figure>'


EXHIBITS = {"diagram": None, "tree": tree, "anno": anno, "table": table, "limits": limits, "flow": flow,
            "timeline": timeline, "path": path, "decisions": decisions, "gaps": gaps, "code": snippet,
            "sequence": None, "schema": None, "schedule": None,
            "html": lambda h: f'<div class="custom">{h}</div>'}


def exhibit(item, claim, where, required=True):
    kinds = [k for k in EXHIBITS if k in item]
    if len(kinds) > 1 or (required and not kinds):
        sys.exit(f"{where}: needs {'exactly' if required else 'at most'} one of {', '.join(EXHIBITS)}, got {kinds}")
    if not kinds:
        return ""
    k = kinds[0]
    if k == "diagram":
        inner = diagram(item[k], claim)
    elif EXHIBITS[k] is None:
        inner = getattr(diagrams, k)(item[k], claim, warnings)
    else:
        inner = EXHIBITS[k](item[k])
    cap = f'<p class="caption">{code(item["caption"])}</p>' if item.get("caption") else ""
    return inner + cap


def panel(i, p):
    ref = f'<span class="ref">{code(p["ref"])}</span>' if p.get("ref") else ""
    half = " w6" if p.get("half") else ""
    body = exhibit(p, p["title"], f"panel {chr(65 + i)}")
    return (f'<section class="panel{half}"><header><span class="badge">{chr(65 + i)}</span>'
            f'<div><h2>{code(p["title"])}</h2>{ref}</div></header><div class="body">{body}</div></section>')


def view(vi, v):
    steps = []
    for si, s in enumerate(v["steps"]):
        body = f'<p>{code(s["body"])}</p>' if s.get("body") else ""
        body += exhibit(s, s["title"], f"view '{v['label']}' step {si + 1}", required=False)
        open_ = " open" if si == 0 or OPEN_ALL else ""
        steps.append(f'<details class="step"{open_} data-step="{si}"><summary><span class="num">{si + 1}</span>'
                     f'<h3>{code(s["title"])}</h3></summary><div class="body">{body}</div></details>')
    summary = f'<p class="vsum">{code(v["summary"])}</p>' if v.get("summary") else ""
    nav = (f'<div class="tour"><button type="button" data-go="-1">Previous step</button>'
           f'<span class="pos">Step 1 / {len(steps)}</span><button type="button" data-go="1">Next step</button></div>')
    return (f'<section class="view" id="view-{vi}" data-view="{vi}"><h2 class="vtitle">{code(v["label"])}</h2>'
            f'{summary}{nav}{"".join(steps)}</section>')


TOUR_JS = """<script>
(()=>{document.documentElement.classList.add('js');
const views=[...document.querySelectorAll('.view')],tabs=[...document.querySelectorAll('.tabs button')];
function show(i){views.forEach((v,j)=>v.hidden=j!==i);tabs.forEach((t,j)=>t.setAttribute('aria-selected',j===i));}
tabs.forEach((t,i)=>t.addEventListener('click',()=>show(i)));
views.forEach(v=>{const s=[...v.querySelectorAll('.step')],pos=v.querySelector('.pos');let cur=0;
function go(n){cur=Math.max(0,Math.min(s.length-1,n));s.forEach((d,j)=>d.open=j===cur);
pos.textContent='Step '+(cur+1)+' / '+s.length;s[cur].scrollIntoView({block:'nearest'});}
v.querySelectorAll('[data-go]').forEach(b=>b.addEventListener('click',()=>go(cur+Number(b.dataset.go))));
s.forEach((d,j)=>d.querySelector('summary').addEventListener('click',()=>{cur=j;pos.textContent='Step '+(j+1)+' / '+s.length;}));});
document.addEventListener('keydown',ev=>{if(ev.target.closest('input,textarea'))return;
const v=views.find(x=>!x.hidden);if(!v)return;if(ev.key==='ArrowRight'||ev.key==='n')v.querySelector('[data-go="1"]').click();
if(ev.key==='ArrowLeft'||ev.key==='p')v.querySelector('[data-go="-1"]').click();
const k=Number(ev.key);if(k>=1&&k<=views.length)show(k-1);});
if(views.length)show(0);})();
</script>"""

args = [a for a in sys.argv[1:] if not a.startswith("--")]
OPEN_ALL = "--open-all" in sys.argv
RENDER = "--no-render" not in sys.argv
MARK = re.compile(r"<!-- built by show-me build\.py from (.+?); edit the spec, not this file\. sha256:([0-9a-f]{64}) -->\n")


def mark(spec_name, page):
    """The line that records which spec made the page and the hash of everything else in it."""
    return (f"<!-- built by show-me build.py from {spec_name}; edit the spec, not this file. "
            f"sha256:{hashlib.sha256(page.encode()).hexdigest()} -->\n")
spec = json.loads(Path(args[0]).read_text())
SPEC_DIR = Path(args[0]).resolve().parent
out = Path(args[1]) if len(args) > 1 else Path(args[0]).with_suffix(".html")
lead = spec["lead"]
points = "".join(f"<li>{code(p)}</li>" for p in lead.get("points", []))
if "views" in spec:
    tabs = "".join(f'<button type="button" role="tab">{code(v["label"])}</button>' for v in spec["views"])
    main = (f'<nav class="tabs" role="tablist">{tabs}</nav>'
            f'<div class="views">{"".join(view(i, v) for i, v in enumerate(spec["views"]))}</div>')
    kind, script = "walkthrough", ("" if OPEN_ALL else TOUR_JS)
elif "flows" in spec:
    flow_js = f"<script>{(HERE.parent / 'assets' / 'flow.js').read_text()}</script>"
    main, script = flow_pages.flow_page(spec, SPEC_DIR, exhibit, list(EXHIBITS), code, warnings, flow_js)
    kind = "flowpage"
else:
    main = f'<div class="grid">{"".join(panel(i, p) for i, p in enumerate(spec["panels"]))}</div>'
    kind, script = "sheet", ""
css = (HERE.parent / "assets" / "sheet.css").read_text()
extra = f"\n<style>\n{spec['css']}\n</style>" if spec.get("css") else ""
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(spec["title"])}</title>
{FONTS}
<style>
{css}
</style>{extra}
</head>
<body>
<div class="sheet {kind}">
<div class="titleblock"><h1>{e(spec["title"])}</h1><span class="meta">{e(spec.get("meta", ""))}</span></div>
<div class="lead"><p>{code(lead["answer"])}</p><ul>{points}</ul></div>
{main}
</div>
{script}
</body>
</html>
"""
if out.exists():
    old = out.read_text()
    m = MARK.search(old)
    if m and hashlib.sha256(MARK.sub("", old, count=1).encode()).hexdigest() != m.group(2):
        sys.exit(f"{out} was edited by hand after it was built; building again would lose that edit.\n"
                 f"Move the change into {Path(args[0]).name}: styles go in its \"css\" key, a missing part goes "
                 f"in an \"html\" exhibit. Then delete {out.name} and build again.")
page = page.replace("<!doctype html>\n", "<!doctype html>\n" + mark(Path(args[0]).name, page), 1)
out.write_text(page)
print(f"wrote {out}")
for w in warnings:
    print(f"WARN {w}")
status = subprocess.run([sys.executable, str(HERE / "check.py"), str(out)]).returncode
if RENDER:
    status |= subprocess.run([sys.executable, str(HERE / "render.py"), str(out), str(SPEC_DIR / "shots")]).returncode
sys.exit(status)
