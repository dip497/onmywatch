"""Check a blueprint sheet before it is handed over.

Usage: python3 check.py sheet.html
Prints ERROR and WARN lines and exits 1 if there is any ERROR.
"""
import re
import sys
from html.parser import HTMLParser

EXHIBITS = {"tree", "anno", "limit", "flow", "timeline", "diagram"}
BANNED = ["utilize", "leverage", "ensure", "robust", "seamless", "in order to", "prior to", "commence", "very", "basically"]
PAIRS = [("ink", "paper"), ("muted", "paper"), ("muted", "fill"), ("note", "paper"), ("note", "note-soft"),
         ("ok", "paper"), ("bad", "paper"), ("badge-ink", "badge")]

problems = []


def report(level, msg):
    problems.append(level)
    print(f"{level} {msg}")


class Sheet(HTMLParser):
    def __init__(self):
        super().__init__()
        self.stack, self.panels, self.text, self.style = [], [], [], ""
        self.edges = self.edge_labels = 0
        self.cur = None

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        cls = set((a.get("class") or "").split())
        if tag not in ("br", "img", "meta", "link", "input", "path", "rect", "circle", "line", "polyline", "polygon"):
            self.stack.append((tag, cls))
        if tag == "section" and "panel" in cls:
            self.cur = {"title": "", "exhibits": set()}
            self.panels.append(self.cur)
        if self.cur is not None and (cls & EXHIBITS or tag == "table"):
            if not any(c & EXHIBITS or t == "table" for t, c in self.stack[:-1] if t != "section"):
                self.cur["exhibits"].add(tag if tag == "table" else min(cls & EXHIBITS))
        if tag == "path" and "edge" in cls:
            self.edges += 1
        if tag == "text" and "elbl" in cls:
            self.edge_labels += 1

    def handle_endtag(self, tag):
        while self.stack:
            t, _ = self.stack.pop()
            if t == tag:
                break
        if tag == "section":
            self.cur = None

    def handle_data(self, data):
        tags = [t for t, _ in self.stack]
        if "style" in tags:
            self.style += data
            return
        if any(t in ("script", "title", "svg", "code", "pre") for t in tags):
            return
        if self.cur is not None and "h2" in tags:
            self.cur["title"] += data
        if data.strip():
            self.text.append((tags[-1] if tags else "", data.strip()))


def luminance(hex_):
    h = hex_.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    c = [int(h[i:i + 2], 16) / 255 for i in (0, 2, 4)]
    c = [x / 12.92 if x <= 0.04045 else ((x + 0.055) / 1.055) ** 2.4 for x in c]
    return 0.2126 * c[0] + 0.7152 * c[1] + 0.0722 * c[2]


def contrast(a, b):
    la, lb = sorted((luminance(a), luminance(b)), reverse=True)
    return (la + 0.05) / (lb + 0.05)


def tokens(block):
    return dict(re.findall(r"--([\w-]+):\s*(#[0-9a-fA-F]{3,6})\b", block))


page = open(sys.argv[1], encoding="utf-8").read()
sheet = Sheet()
sheet.feed(page)
css = sheet.style

light = tokens(re.search(r":root\s*\{(.*?)\}", css, re.S).group(1))
dark_m = re.search(r':root\[data-theme="dark"\]\s*\{(.*?)\}', css, re.S)
for name, theme in (("light", light), ("dark", {**light, **tokens(dark_m.group(1))} if dark_m else None)):
    if theme is None:
        report("ERROR", "no dark theme tokens")
        continue
    for fg, bg in PAIRS:
        if fg in theme and bg in theme:
            r = contrast(theme[fg], theme[bg])
            if r < 4.5:
                report("ERROR", f"{name}: --{fg} on --{bg} contrast {r:.2f}, needs 4.5")

for rule in re.finditer(r"([^{}]+)\{([^}]*)\}", css):
    sel, body = rule.group(1).strip(), rule.group(2)
    for size in re.findall(r"font(?:-size)?:[^;]*?(\d+(?:\.\d+)?)px", body):
        floor = 13 if "diagram" in sel else 14
        if float(size) < floor:
            report("ERROR", f"font {size}px in `{sel[:50]}`, floor is {floor}px")

if not 1 <= len(sheet.panels) <= 6:
    report("ERROR", f"{len(sheet.panels)} panels, use 1 to 6")
for i, p in enumerate(sheet.panels):
    letter = chr(65 + i)
    words = p["title"].split()
    if not words:
        report("ERROR", f"panel {letter}: no title")
    elif len(words) > 12:
        report("WARN", f"panel {letter}: title has {len(words)} words, keep to 12")
    elif not p["title"].strip().endswith("."):
        report("WARN", f"panel {letter}: title '{p['title'].strip()}' reads as a label; make it a sentence")
    if len(p["exhibits"]) != 1:
        report("WARN", f"panel {letter}: {len(p['exhibits'])} kinds of exhibit ({', '.join(sorted(p['exhibits'])) or 'none'}), use exactly 1")

pieces = [t for tag, t in sheet.text if tag in ("p", "li", "figcaption", "h2", "small")]
prose = " ".join(pieces)
total = len(" ".join(t for _, t in sheet.text).split())
if total > 450:
    report("WARN", f"{total} words on the sheet, keep to 450")
for s in (s for piece in pieces for s in re.split(r"(?<=[.!?])\s+", piece)):
    if len(s.split()) > 25:
        report("WARN", f"sentence of {len(s.split())} words: '{s[:60]}…'")
low = prose.lower()
for w in BANNED:
    if re.search(rf"\b{w}\b", low):
        report("WARN", f"word to replace: '{w.strip()}'")
if sheet.edges > sheet.edge_labels:
    report("WARN", f"{sheet.edges} arrows but {sheet.edge_labels} arrow labels; label every arrow")
if "lead" not in page:
    report("ERROR", "no lead block with the answer")

print("OK" if not problems else f"{problems.count('ERROR')} errors, {problems.count('WARN')} warnings")
sys.exit(1 if "ERROR" in problems else 0)
