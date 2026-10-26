"""Flow pages: screens and decisions joined by labelled links, laid out left to right.

A flow is a graph. Each link says what the user did or what the system answered. A link that
points back to a state already on the path from the start is a return and is drawn dashed.
Layout follows the layered (Sugiyama) method: break cycles with a depth-first search, put each
state one column after its furthest parent, order each column by the mean row of its parents,
then route every link with right angles through the gaps between columns.
"""
import base64
import hashlib
import io
import json
import sys
from html import escape as e

from graph_layout import columns, find_returns

GAP_X, GAP_Y, HEAD, PAD = 170, 36, 46, 6
LANE_STEP, PORT_STEP = 22, 22
DECISION_W, DECISION_H = 180, 72
FRAMES = {"phone": (130, 260), "browser": (230, 170), "none": (230, 170)}


def fail(msg):
    sys.exit(f"flow: {msg}")


# ---------- screens ----------

def load_image(path, width):
    """Read a screenshot once. Shrink it to twice the display width if Pillow is there."""
    raw = path.read_bytes()
    try:
        from PIL import Image
        im = Image.open(io.BytesIO(raw))
        if im.width > width * 2:
            im = im.resize((width * 2, round(im.height * width * 2 / im.width)), Image.LANCZOS)
        out = io.BytesIO()
        im.save(out, "WEBP", quality=82)
        if out.tell() < len(raw):
            return "image/webp", out.getvalue()
    except ImportError:
        pass
    ext = path.suffix.lower().lstrip(".")
    return f"image/{'jpeg' if ext == 'jpg' else ext}", raw


def screen_html(s, where, spec_dir, width, images, exhibit, exhibit_keys):
    kinds = [k for k in ("image", "html", *exhibit_keys) if k in s]
    if len(kinds) != 1:
        fail(f"{where}: needs exactly one of image, html, {', '.join(exhibit_keys)}; got {kinds or 'none'}")
    if "image" in s:
        src = spec_dir / s["image"]
        if not src.is_file():
            fail(f"{where}: image {src} not found")
        mime, data = load_image(src, width)
        key = hashlib.sha1(data).hexdigest()[:12]
        images[key] = f"data:{mime};base64,{base64.b64encode(data).decode()}"
        return f'<img data-img="{key}" alt="{e(s["title"])}">'
    if "html" in s:
        return s["html"]
    return f'<div class="body">{exhibit(s, s["title"], where)}</div>'


# ---------- graph ----------

def reach(links, start):
    seen, todo = {start}, [start]
    while todo:
        v = todo.pop()
        for ln in links:
            if ln["from"] == v and ln["to"] not in seen:
                seen.add(ln["to"])
                todo.append(ln["to"])
    return seen


def read_graph(f):
    states = f.get("states") or fail(f"'{f.get('id')}' has no states")
    by_id = {}
    for s in states:
        if s.get("id") in by_id:
            fail(f"state id '{s.get('id')}' is used twice")
        if "title" not in s and "decision" not in s:
            fail(f"state '{s.get('id')}' needs a title, or a decision question")
        by_id[s["id"]] = s
    links = f.get("links", [])
    for ln in links:
        for end in ("from", "to"):
            if ln.get(end) not in by_id:
                fail(f"link {ln.get('from')} → {ln.get('to')}: '{ln.get(end)}' is not a state")
        if not ln.get("label"):
            fail(f"link {ln['from']} → {ln['to']} needs a label: what the user did or what the system answered")
    start = f.get("start", states[0]["id"])
    if start not in by_id:
        fail(f"start '{start}' is not a state")
    return states, by_id, links, start


def layout(by_id, links, back, visit, size):
    pinned = {v: {k: by_id[v][k] for k in ("col", "row") if k in by_id[v]} for v in visit}
    col, cols, parents = columns(visit, links, back, pinned)
    xs, x = {}, 40
    for c, members in cols.items():
        xs[c] = x
        x += max(size(v)[0] for v in members) + GAP_X
    box = {}
    for c, members in cols.items():
        bottom = 40
        for v in members:
            w, h = size(v)
            ps = [box[p] for p in parents[v] if p in box]
            want = (sum(p[1] + p[3] / 2 for p in ps) / len(ps) - h / 2) if ps else bottom
            y = max(bottom, want)
            box[v] = (xs[c], y, w, h)
            bottom = y + h + GAP_Y
    return box, col, xs


def hits(seg, r, pad=6):
    (x1, y1), (x2, y2) = seg
    rx, ry, rw, rh = r[0] - pad, r[1] - pad, r[2] + 2 * pad, r[3] + 2 * pad
    if x1 == x2:
        lo, hi = sorted((y1, y2))
        return rx < x1 < rx + rw and lo < ry + rh and hi > ry
    lo, hi = sorted((x1, x2))
    return ry < y1 < ry + rh and lo < rx + rw and hi > rx


def route(links, back, box, col, xs, warnings, fid):
    """Right-angle routes. Ports fan out along each side so labels do not sit on each other."""
    top = min(b[1] for b in box.values())
    bottom = max(b[1] + b[3] for b in box.values())
    outs, ins = {}, {}
    for n, ln in enumerate(links):
        outs.setdefault(ln["from"], []).append(n)
        ins.setdefault(ln["to"], []).append(n)
    middle = {k: b[1] + b[3] / 2 for k, b in box.items()}
    for v, lst in outs.items():
        lst.sort(key=lambda n: middle[links[n]["to"]])
    for v, lst in ins.items():
        lst.sort(key=lambda n: middle[links[n]["from"]])

    def port(group, v, n):
        lst = group[v]
        x, y, w, h = box[v]
        k = lst.index(n)
        return y + h / 2 + (k - (len(lst) - 1) / 2) * min(PORT_STEP, (h - 12) / max(1, len(lst)))

    lane_top = lane_bottom = 0
    gap_use = {}
    paths = []
    for n, ln in enumerate(links):
        a, b = ln["from"], ln["to"]
        ax, ay, aw, ah = box[a]
        bx, by, bw, bh = box[b]
        y1, y2 = port(outs, a, n), port(ins, b, n)
        others = [r for k, r in box.items() if k not in (a, b)]
        if n in back or col[b] <= col[a]:
            right = ax + aw + 24 + LANE_STEP * gap_use.setdefault(("r", col[a]), 0)
            gap_use[("r", col[a])] += 1
            left = bx - 24 - LANE_STEP * gap_use.setdefault(("l", col[b]), 0)
            gap_use[("l", col[b])] += 1
            if (ay + by) / 2 > (top + bottom) / 2:
                lane_bottom += 1
                lane = bottom + 20 + LANE_STEP * lane_bottom
            else:
                lane_top += 1
                lane = top - 20 - LANE_STEP * lane_top
            pts = [(ax + aw, y1), (right, y1), (right, lane), (left, lane), (left, y2), (bx, y2)]
        else:
            k = gap_use.setdefault(("l", col[b]), 0)
            gap_use[("l", col[b])] += 1
            cx = bx - 28 - LANE_STEP * k
            if abs(y1 - y2) < 1:
                cands = [[(ax + aw, y1), (bx, y1)]]
            else:
                cands = [[(ax + aw, y1), (cx, y1), (cx, y2), (bx, y2)]]
            near = ax + aw + 28 + LANE_STEP * k
            cands.append([(ax + aw, y1), (near, y1), (near, y2), (bx, y2)])
            for lane in (top - 20 - LANE_STEP * (lane_top + 1), bottom + 20 + LANE_STEP * (lane_bottom + 1)):
                cands.append([(ax + aw, y1), (near, y1), (near, lane), (cx, lane), (cx, y2), (bx, y2)])
            pts = next((c for c in cands if not any(hits(s, r) for s in zip(c, c[1:]) for r in others)), None)
            if pts is None:
                pts = cands[0]
                warnings.append(f"flow '{fid}': link {a} → {b} crosses a box; set 'row' or 'col' on a state to move it")
            elif len(pts) == 6 and pts[2][1] < top:
                lane_top += 1
            elif len(pts) == 6:
                lane_bottom += 1
        paths.append(pts)
    return paths


def label_spot(pts, text):
    """Centre of the longest horizontal piece; a return labels its lane."""
    w = len(text) * 7.6 + 14
    horiz = [(p, q) for p, q in zip(pts, pts[1:]) if p[1] == q[1]]
    (x1, y), (x2, _) = max(horiz, key=lambda s: abs(s[0][0] - s[1][0]))
    return (x1 + x2) / 2 - w / 2, y - 10, w


def count_crossings(paths):
    segs = [(i, s) for i, p in enumerate(paths) for s in zip(p, p[1:])]
    n = 0
    for i, ((ax, ay), (bx, by)) in segs:
        if ay != by:
            continue
        for j, ((cx, cy), (dx, dy)) in segs:
            if j == i or cx != dx:
                continue
            if min(ax, bx) + 1 < cx < max(ax, bx) - 1 and min(cy, dy) + 1 < ay < max(cy, dy) - 1:
                n += 1
    return n


# ---------- page ----------

def flow_section(fi, f, spec_dir, images, exhibit, exhibit_keys, code, warnings):
    fid = f.get("id") or fail("every flow needs an 'id'; reviews are stored under it")
    frame = f.get("frame", "none")
    if frame not in FRAMES:
        fail(f"'{fid}': frame must be one of {', '.join(FRAMES)}")
    width = f.get("width", 390 if frame == "phone" else 720)
    tw, th = FRAMES[frame]
    states, by_id, links, start = read_graph(f)
    reached = reach(links, start)
    lost = [s["id"] for s in states if s["id"] not in reached]
    if lost:
        fail(f"no path from '{start}' to: {', '.join(lost)}. Add a link or remove the state")
    back, visit = find_returns([s["id"] for s in states], links, [start])

    def size(v):
        if by_id[v].get("decision"):
            return DECISION_W, DECISION_H
        return tw + 2 * PAD, HEAD + th + 3 * PAD

    box, col, xs = layout(by_id, links, back, visit, size)
    paths = route(links, back, box, col, xs, warnings, fid)
    crossings = count_crossings([p for n, p in enumerate(paths) if n not in back])
    if crossings:
        warnings.append(f"flow '{fid}': {crossings} line crossings; set 'row' on states to untangle")
    min_x = min(min(x for x, _ in p) for p in paths) if paths else 0
    min_y = min([b[1] for b in box.values()] + [y for p in paths for _, y in p]) - 40
    shift_x, shift_y = 40 - min(40, min_x), -min_y
    W = max([b[0] + b[2] for b in box.values()] + [x for p in paths for x, _ in p]) + shift_x + 40
    H = max([b[1] + b[3] for b in box.values()] + [y for p in paths for _, y in p]) + shift_y + 40

    def check(i, title):
        return f'<input type="checkbox" class="review" data-review="{e(i)}" aria-label="Reviewed: {e(title)}">'

    nodes, screens = [], {}
    for v in visit:
        s = by_id[v]
        x, y, w, h = box[v]
        x, y = x + shift_x, y + shift_y
        if s.get("decision"):
            nodes.append(f'<button type="button" class="fdec" data-id="{e(v)}" style="left:{x:.0f}px;top:{y:.0f}px;'
                         f'width:{w}px;height:{h}px">{code(s["decision"])}</button>')
            continue
        shot = screen_html(s, f"state '{v}'", spec_dir, width, images, exhibit, exhibit_keys)
        screens[v] = shot
        sub = f'<span class="fsub">{code(s["sub"])}</span>' if s.get("sub") else ""
        nodes.append(f'<div class="fnode" data-id="{e(v)}" tabindex="0" role="button" aria-label="Open {e(s["title"])}" '
                     f'style="left:{x:.0f}px;top:{y:.0f}px;width:{w}px">'
                     f'<div class="fhead"><span class="ftitle" title="{e(s["title"])}">{code(s["title"])}{sub}</span>{check(v, s["title"])}</div>'
                     f'<div class="thumb frame-{frame}" style="width:{tw}px;height:{th}px"><div class="scale" inert '
                     f'style="width:{width}px;transform:scale({tw / width:.4f})">{shot}</div></div></div>')

    edges, labels = [], []
    for n, (ln, pts) in enumerate(zip(links, paths)):
        pts = [(x + shift_x, y + shift_y) for x, y in pts]
        kind = " ".join(k for k, on in (("error", ln.get("error")), ("return", n in back)) if on)
        d = "M" + " L".join(f"{x:.0f},{y:.0f}" for x, y in pts)
        edges.append(f'<path class="link {kind}" data-from="{e(ln["from"])}" data-to="{e(ln["to"])}" d="{d}" '
                     f'marker-end="url(#fa-{fi}{"-err" if ln.get("error") else ""})"/>')
        lx, ly, lw = label_spot(pts, ln["label"])
        labels.append(f'<g class="llbl {kind}" data-from="{e(ln["from"])}" data-to="{e(ln["to"])}">'
                      f'<rect x="{lx:.0f}" y="{ly - 13:.0f}" width="{lw}" height="19" rx="4"/>'
                      f'<text x="{lx + 7:.0f}" y="{ly:.0f}">{e(ln["label"])}</text></g>')
    marker = "".join(f'<marker id="fa-{fi}{sfx}" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" '
                     f'orient="auto"><path d="M0,0 L10,5 L0,10 z" class="{cls}"/></marker>' for sfx, cls in (("", "ah"), ("-err", "ah err")))

    data = {"id": fid, "start": start, "states": {}, "links": []}
    for v in visit:
        s = by_id[v]
        data["states"][v] = {"title": s.get("title") or s["decision"], "decision": bool(s.get("decision")),
                             "note": s.get("note", ""), "sub": s.get("sub", ""),
                             "fp": hashlib.sha1(screens.get(v, s.get("decision", "")).encode()).hexdigest()[:12]}
    for n, ln in enumerate(links):
        data["links"].append({"from": ln["from"], "to": ln["to"], "label": ln["label"],
                              "error": bool(ln.get("error")), "back": n in back})

    kinds = {"return": any(n in back for n in range(len(links))), "error": any(ln.get("error") for ln in links),
             "decision": any(s.get("decision") for s in states)}
    legend = ('<span class="lg"><i class="lg-screen"></i>Screen</span>'
              + ('<span class="lg"><i class="lg-dec"></i>Decision</span>' if kinds["decision"] else "")
              + '<span class="lg"><i class="lg-link"></i>User action or answer</span>'
              + ('<span class="lg"><i class="lg-link error"></i>Error path</span>' if kinds["error"] else "")
              + ('<span class="lg"><i class="lg-link return"></i>Goes back</span>' if kinds["return"] else ""))
    platform = f'<span class="fplat">{e(f["platform"])}</span>' if f.get("platform") else ""
    outline = "".join(f'<li><button type="button" data-open="{e(v)}">{code(by_id[v]["title"])}</button>{check(v, by_id[v]["title"])}</li>'
                      for v in visit if not by_id[v].get("decision"))
    summary = f'<p class="fsum">{code(f["summary"])}</p>' if f.get("summary") else ""
    blob = json.dumps(data).replace("</", "<\\/")
    return (f'<section class="flowsec" data-flow="{fi}" data-frame="{frame}" data-width="{width}">'
            f'<div class="ftool"><span class="fname">{code(f.get("label", fid))}</span>{platform}'
            f'<span class="fcount" aria-live="polite"></span><span class="spacer"></span>'
            f'<span class="zoom"><button type="button" data-zoom="-1" aria-label="Zoom out">−</button>'
            f'<output>100%</output><button type="button" data-zoom="1" aria-label="Zoom in">+</button>'
            f'<button type="button" data-zoom="fit">Fit to screen</button></span></div>'
            f'{summary}<div class="legend">{legend}</div>'
            f'<div class="fmap" tabindex="-1"><div class="fsize" style="width:{W:.0f}px;height:{H:.0f}px">'
            f'<div class="stage" style="width:{W:.0f}px;height:{H:.0f}px">'
            f'<svg width="{W:.0f}" height="{H:.0f}" aria-hidden="true"><defs>{marker}</defs>{"".join(edges)}{"".join(labels)}</svg>'
            f'{"".join(nodes)}</div></div></div>'
            f'<details class="foutline"><summary>All screens, in path order</summary><ul>{outline}</ul></details>'
            f'<script type="application/json" class="fdata">{blob}</script></section>')


def flow_page(spec, spec_dir, exhibit, exhibit_keys, code, warnings, js):
    flows = spec["flows"]
    images = {}
    sections = [flow_section(i, f, spec_dir, images, exhibit, exhibit_keys, code, warnings) for i, f in enumerate(flows)]
    size = sum(len(v) for v in images.values())
    if size > 12_000_000:
        warnings.append(f"screenshots add {size / 1e6:.1f} MB; a shared page must stay under 16 MB. "
                        "Install Pillow to shrink them, or split the flows")
    picker = ""
    if len(flows) > 1:
        opts = "".join(f'<option value="{i}">{e(f.get("label", f["id"]))}</option>' for i, f in enumerate(flows))
        picker = f'<label class="fpick">Flow <select>{opts}</select></label>'
    toolbar = (f'<div class="fbar">{picker}<span class="spacer"></span>'
               f'<button type="button" class="ftheme" aria-pressed="false">Dark</button></div>')
    overlay = ('<dialog class="fover" aria-labelledby="fover-title"><div class="fobar">'
               '<h2 id="fover-title"></h2><input type="checkbox" class="review" aria-label="Reviewed">'
               '<span class="spacer"></span><button type="button" class="ftheme" aria-pressed="false">Dark</button>'
               '<button type="button" class="fclose">Close</button></div>'
               '<p class="fosub"></p><p class="fonote"></p><div class="foin"></div><div class="foout"></div>'
               '<div class="fostage"><div class="foscreen"></div></div></dialog>')
    imgs = f'<script type="application/json" id="flow-images">{json.dumps(images)}</script>'
    return f'{toolbar}<div class="flows">{"".join(sections)}</div>{overlay}', imgs + js
