"""Build a show-me sheet from a small JSON spec, then check it.

Usage: python3 build.py sheet.json [out.html]
Writes out.html (default: next to the JSON) with the CSS inlined, runs check.py, exits 1 on a check error.
"""
import json
import subprocess
import sys
from html import escape as e
from pathlib import Path

HERE = Path(__file__).resolve().parent
FONTS = ('<link rel="preconnect" href="https://fonts.googleapis.com">'
         '<link href="https://fonts.googleapis.com/css2?family=IBM+Plex+Mono:wght@400;500'
         '&family=IBM+Plex+Sans:wght@400;500;600&display=swap" rel="stylesheet">')


def code(text):
    """`x` in spec text becomes <code>x</code>."""
    parts = e(text).split("`")
    return "".join(f"<code>{p}</code>" if i % 2 else p for i, p in enumerate(parts))


def tree(t):
    items = "".join(f"<li>{code(i[0])}<small>{code(i[1])}</small></li>" if len(i) > 1 else f"<li>{code(i[0])}</li>"
                    for i in t["items"])
    sub = f"<small>{code(t['sub'])}</small>" if t.get("sub") else ""
    return f'<div class="body tree"><div class="root"><b>{code(t["root"])}</b>{sub}</div><ul>{items}</ul></div>'


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
    head = "".join(f"<th>{e(h)}</th>" for h in t["head"])
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


def diagram(d, claim):
    """Nodes sit on a grid (col, row). Edges go straight, or as one L bend, between box edges."""
    nodes = {n["id"]: n for n in d["nodes"]}
    char, pad, row_h, gap_x, gap_y = 9, 28, 64, 120, 70
    cols = max(n["col"] for n in nodes.values()) + 1
    rows = max(n["row"] for n in nodes.values()) + 1
    col_w = [110] * cols
    for n in nodes.values():
        col_w[n["col"]] = max(col_w[n["col"]], len(n["label"]) * char + pad, len(n.get("sub", "")) * 7.5 + pad, 110)
    for ed in d["edges"]:
        a, b = nodes[ed["from"]], nodes[ed["to"]]
        if a["row"] == b["row"] and abs(a["col"] - b["col"]) == 1:
            gap_x = max(gap_x, len(ed.get("label", "")) * 8 + 40)
    xs = [20 + sum(col_w[:c]) + gap_x * c for c in range(cols)]
    W = xs[-1] + col_w[-1] + 20
    H = 20 + rows * row_h + (rows - 1) * gap_y + 20

    def box(n):
        w = col_w[n["col"]]
        x = xs[n["col"]]
        y = 20 + n["row"] * (row_h + gap_y)
        return x, y, w, row_h

    edges, labels, shapes = [], [], []
    for ed in d["edges"]:
        a, b = nodes[ed["from"]], nodes[ed["to"]]
        ax, ay, aw, ah = box(a)
        bx, by, bw, bh = box(b)
        new = " new" if ed.get("new") else ""
        if a["row"] == b["row"]:
            y = ay + ah / 2
            x1, x2 = (ax + aw, bx) if bx > ax else (ax, bx + bw)
            path, lx, ly = f"M{x1},{y} H{x2}", (x1 + x2) / 2, y - 8
        elif a["col"] == b["col"]:
            x = ax + aw / 2
            y1, y2 = (ay + ah, by) if by > ay else (ay, by + bh)
            path, lx, ly = f"M{x},{y1} V{y2}", x + 10, (y1 + y2) / 2 + 5
        else:
            y = ay + ah / 2
            x1 = ax + aw if bx > ax else ax
            x2 = bx + bw / 2
            y2 = by if by > ay else by + bh
            path, lx, ly = f"M{x1},{y} H{x2} V{y2}", (x1 + x2) / 2, y - 8
        edges.append(f'<path class="edge{new}" d="{path}" marker-end="url(#arrow)"/>')
        if ed.get("label"):
            t = ed["label"]
            w = len(t) * 8 + 12
            anchor_x = lx - w / 2 if a["col"] != b["col"] else lx - 4
            labels.append(f'<rect class="mask" x="{anchor_x}" y="{ly - 14}" width="{w}" height="19"/>'
                          f'<text class="elbl{new}" x="{anchor_x + 6}" y="{ly}">{e(t)}</text>')
    for n in nodes.values():
        x, y, w, h = box(n)
        kinds = " ".join(k for k in ("new", "store") if n.get(k))
        cy = y + (h / 2 + 5 if not n.get("sub") else h / 2 - 3)
        shapes.append(f'<rect class="node {kinds}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
                      f'<text class="lbl" x="{x + w / 2}" y="{cy}" text-anchor="middle">{e(n["label"])}</text>')
        if n.get("sub"):
            shapes.append(f'<text class="sub" x="{x + w / 2}" y="{y + h / 2 + 16}" text-anchor="middle">{e(n["sub"])}</text>')
    marker = ('<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
              'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>')
    svg = (f'<svg viewBox="0 0 {W:.0f} {H:.0f}" role="img" aria-label="{e(claim)}" style="min-width:{min(W, 680):.0f}px">'
           f'{marker}{"".join(edges)}{"".join(labels)}{"".join(shapes)}</svg>')
    return f'<figure class="diagram"><div class="scroll">{svg}</div></figure>'


EXHIBITS = {"tree": tree, "anno": anno, "table": table, "limits": limits, "flow": flow, "timeline": timeline}


def panel(i, p):
    kinds = [k for k in (*EXHIBITS, "diagram") if k in p]
    if len(kinds) != 1:
        sys.exit(f"panel {chr(65 + i)}: needs exactly one of {', '.join((*EXHIBITS, 'diagram'))}, got {kinds}")
    k = kinds[0]
    if k == "diagram":
        inner = diagram(p[k], p["title"])
    elif k == "tree":
        inner = tree(p[k])
    else:
        inner = EXHIBITS[k](p[k])
    if k != "tree":
        cap = f'<p class="caption">{code(p["caption"])}</p>' if p.get("caption") else ""
        inner = f'<div class="body">{inner}{cap}</div>'
    ref = f'<span class="ref">{code(p["ref"])}</span>' if p.get("ref") else ""
    half = " w6" if p.get("half") else ""
    return (f'<section class="panel{half}"><header><span class="badge">{chr(65 + i)}</span>'
            f'<div><h2>{code(p["title"])}</h2>{ref}</div></header>{inner}</section>')


spec = json.loads(Path(sys.argv[1]).read_text())
out = Path(sys.argv[2]) if len(sys.argv) > 2 else Path(sys.argv[1]).with_suffix(".html")
lead = spec["lead"]
points = "".join(f"<li>{code(p)}</li>" for p in lead.get("points", []))
page = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(spec["title"])}</title>
{FONTS}
<style>
{(HERE.parent / "assets" / "sheet.css").read_text()}figure.diagram .scroll,div.scroll{{overflow-x:auto}}
</style>
</head>
<body>
<div class="sheet">
<div class="titleblock"><h1>{e(spec["title"])}</h1><span class="meta">{e(spec.get("meta", ""))}</span></div>
<div class="lead"><p>{code(lead["answer"])}</p><ul>{points}</ul></div>
<div class="grid">
{"".join(panel(i, p) for i, p in enumerate(spec["panels"]))}
</div>
</div>
</body>
</html>
"""
out.write_text(page)
print(f"wrote {out}")
sys.exit(subprocess.run([sys.executable, str(HERE / "check.py"), str(out)]).returncode)
