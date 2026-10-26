"""Three more drawn exhibits for sheets and walkthroughs: sequence, schema and schedule.

Each takes plain data and returns inline SVG that uses the sheet's colour variables, so both
themes work. Colour keeps its one meaning: ink is normal, blue dashed is new, green is done,
red is late or wrong.
"""
import sys
from datetime import date, timedelta
from html import escape as e

from graph_layout import columns, find_returns

CHAR = 7.6


def fail(msg):
    sys.exit(msg)


def svg(w, h, claim, body, cls):
    return (f'<figure class="diagram {cls}"><div class="scroll"><svg viewBox="0 0 {w:.0f} {h:.0f}" role="img" '
            f'aria-label="{e(claim)}" style="min-width:{min(w * 0.85, 680):.0f}px;max-width:{w * 1.1:.0f}px">'
            '<defs><marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" '
            'orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="context-stroke"/></marker></defs>'
            f'{body}</svg></div></figure>')


def label(x, y, text, cls="elbl", anchor="middle"):
    w = len(text) * CHAR + 12
    lx = x - w / 2 if anchor == "middle" else x
    return (f'<rect class="mask" x="{lx:.0f}" y="{y - 14:.0f}" width="{w:.0f}" height="19"/>'
            f'<text class="{cls}" x="{lx + w / 2:.0f}" y="{y:.0f}" text-anchor="middle">{e(text)}</text>')


# ---------- sequence: who sends what to whom, in time order ----------

def sequence(d, claim, warnings):
    actors = d["actors"]
    msgs = d["messages"]
    for m in msgs:
        for end in ("from", "to"):
            if m.get(end) not in actors:
                fail(f"sequence '{claim[:40]}': '{m.get(end)}' is not in actors")
    if len(actors) > 6:
        warnings.append(f"sequence '{claim[:40]}': {len(actors)} actors; more than 6 is hard to read, split it")
    if len(msgs) > 14:
        warnings.append(f"sequence '{claim[:40]}': {len(msgs)} messages; more than 14 is hard to read, split it")
    widest = max([len(m["text"]) for m in msgs] + [10]) * CHAR + 40
    gap = max(170, min(widest, 320))
    xs = {a: 90 + i * gap for i, a in enumerate(actors)}
    top, step = 70, 46
    H = top + len(msgs) * step + 60
    W = xs[actors[-1]] + 110
    body = []
    for a in actors:
        x = xs[a]
        body.append(f'<line class="life" x1="{x}" y1="{top - 14}" x2="{x}" y2="{H - 20}"/>')
        w = max(110, len(a) * 9 + 28)
        body.append(f'<rect class="node" x="{x - w / 2:.0f}" y="12" width="{w}" height="40"/>'
                    f'<text class="lbl" x="{x}" y="37" text-anchor="middle">{e(a)}</text>')
    for i, m in enumerate(msgs):
        y = top + 18 + i * step
        a, b = xs[m["from"]], xs[m["to"]]
        kind = " ".join(k for k, on in (("new", m.get("new")), ("reply", m.get("reply")), ("bad", m.get("error"))) if on)
        lcls = "elbl" + (" new" if m.get("new") else "") + (" bad" if m.get("error") else "")
        if a == b:
            body.append(f'<path class="edge {kind}" d="M{a},{y - 8} H{a + 44} V{y + 10} H{a + 4}" marker-end="url(#arrow)"/>')
            body.append(label(a + 52, y + 5, m["text"], lcls, "left"))
        else:
            end = b - 4 if b > a else b + 4
            body.append(f'<path class="edge {kind}" d="M{a},{y} H{end}" marker-end="url(#arrow)"/>')
            body.append(label((a + b) / 2, y - 7, m["text"], lcls))
    return svg(W, H, claim, "".join(body), "seq")


# ---------- schema: tables, columns, and the foreign keys between them ----------

def schema(d, claim, warnings):
    """Links come from the columns: a column marked `fk table.column` draws an arrow to that table."""
    tables = {t["name"]: t for t in d["tables"]}
    links = []
    for t in d["tables"]:
        for r, col in enumerate(t["columns"]):
            note = col[2] if len(col) > 2 else ""
            if note.startswith("fk "):
                target = note[3:].split(".")[0]
                if target not in tables:
                    fail(f"schema '{claim[:40]}': {t['name']}.{col[0]} points at '{target}', which is not a table")
                links.append({"from": t["name"], "to": target, "row": r})
    if len(tables) > 8:
        warnings.append(f"schema '{claim[:40]}': {len(tables)} tables; show the 8 that matter and name the rest in the caption")
    names = list(tables)
    back, visit = find_returns(names, links, [])
    col, cols, _ = columns(visit, links, back, {})
    head, row_h, gap_x, gap_y = 34, 26, 130, 30
    width = {n: max([len(n) * 9 + 30] + [(len(c[0]) + len(c[1]) + (5 if len(c) > 2 else 0)) * CHAR + 72 for c in tables[n]["columns"]]) for n in names}
    col_w = {c: max(width[n] for n in members) for c, members in cols.items()}
    box, x = {}, 20
    for c, members in cols.items():
        y = 20
        for n in members:
            h = head + row_h * len(tables[n]["columns"])
            box[n] = (x, y, col_w[c], h)
            y += h + gap_y
        x += col_w[c] + gap_x
    W, H = x - gap_x + 20, max(b[1] + b[3] for b in box.values()) + 20
    edges, used = [], {}
    for ln in links:
        sx, sy, sw, sh = box[ln["from"]]
        tx, ty, tw, th = box[ln["to"]]
        y1 = sy + head + row_h * ln["row"] + row_h / 2
        y2 = ty + head / 2
        k = used.setdefault(ln["to"], 0)
        used[ln["to"]] += 1
        if ln["from"] == ln["to"]:
            d_ = f"M{sx + sw},{y1} H{sx + sw + 24} V{y2} H{sx + sw}"
        elif tx > sx:
            cx = tx - 24 - 12 * k
            d_ = f"M{sx + sw},{y1} H{cx} V{y2} H{tx}"
        else:
            cx = sx + sw + 24 + 12 * k
            lane = max(b[1] + b[3] for b in box.values()) + 14 + 12 * k
            H = max(H, lane + 20)
            d_ = f"M{sx + sw},{y1} H{cx} V{lane} H{tx - 24 - 12 * k} V{y2} H{tx}"
        edges.append(f'<path class="edge fk" d="{d_}" marker-end="url(#arrow)"/>')
    shapes = []
    for n, (x, y, w, h) in box.items():
        t = tables[n]
        kind = " new" if t.get("new") else ""
        shapes.append(f'<rect class="node{kind}" x="{x}" y="{y}" width="{w}" height="{h}"/>'
                      f'<rect class="thead" x="{x}" y="{y}" width="{w}" height="{head}"/>'
                      f'<text class="lbl" x="{x + 12}" y="{y + 22}">{e(n)}</text>')
        for r, c in enumerate(t["columns"]):
            cy = y + head + row_h * r
            note = c[2] if len(c) > 2 else ""
            mark = "PK" if note == "pk" else "FK" if note.startswith("fk ") else ""
            shapes.append(f'<line class="trow" x1="{x}" y1="{cy}" x2="{x + w}" y2="{cy}"/>'
                          f'<text class="cname{" key" if mark else ""}" x="{x + 12}" y="{cy + 18}">{e(c[0])}</text>'
                          f'<text class="ctype" x="{x + w - 12}" y="{cy + 18}" text-anchor="end">{e(c[1])}{" · " + mark if mark else ""}</text>')
    return svg(W, H, claim, "".join(edges) + "".join(shapes), "schema")


# ---------- schedule: work over time ----------

def schedule(d, claim, warnings):
    rows = d["rows"]
    day = date.fromisoformat
    start = day(d.get("start") or min(r["from"] for r in rows))
    end = day(d.get("end") or max(r["to"] for r in rows))
    if end <= start:
        fail(f"schedule '{claim[:40]}': end must come after start")
    if len(rows) > 12:
        warnings.append(f"schedule '{claim[:40]}': {len(rows)} rows; more than 12 is hard to read, group them")
    label_w = max(len(r["label"]) for r in rows) * CHAR + 30
    plot_w, row_h, top = 640, 34, 40
    span = (end - start).days
    x_of = lambda dd: label_w + (dd - start).days / span * plot_w
    H = top + len(rows) * row_h + 16
    W = label_w + plot_w + 20
    body = []
    m = date(start.year, start.month, 1)
    while m <= end:
        if m >= start:
            x = x_of(m)
            body.append(f'<line class="grid" x1="{x:.0f}" y1="{top - 6}" x2="{x:.0f}" y2="{H - 10}"/>'
                        f'<text class="elbl" x="{x + 4:.0f}" y="{top - 14}">{m.strftime("%b %Y" if m.month == 1 or m == date(start.year, start.month, 1) else "%b")}</text>')
        m = (m.replace(day=28) + timedelta(days=4)).replace(day=1)
    for i, r in enumerate(rows):
        y = top + i * row_h
        a, b = day(r["from"]), day(r["to"])
        status = r.get("status", "")
        if status not in ("", "done", "late", "new"):
            fail(f"schedule '{claim[:40]}': status '{status}' must be done, late or new")
        x1, x2 = x_of(max(a, start)), x_of(min(b, end))
        body.append(f'<text class="rlbl" x="10" y="{y + 22}">{e(r["label"])}</text>'
                    f'<rect class="bar {status}" x="{x1:.0f}" y="{y + 8}" width="{max(4, x2 - x1):.0f}" height="{row_h - 14}" rx="3"/>')
    if d.get("today"):
        t = day(d["today"])
        if start <= t <= end:
            x = x_of(t)
            body.append(f'<line class="today" x1="{x:.0f}" y1="{top - 6}" x2="{x:.0f}" y2="{H - 10}"/>'
                        f'{label(x, H - 2, "today", "elbl new")}')
            H += 10
    return svg(W, H + 6, claim, "".join(body), "sched")
