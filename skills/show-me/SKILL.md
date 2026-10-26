---
name: show-me
description: 'Make the current topic visible instead of explaining it in prose. "/show-me" shows you: the smallest picture in the chat (pseudocode, call tree, file tree, diff, a small text box diagram); anything that needs a drawn diagram becomes a page. "/show-me sheet" or "/show-me share" makes one HTML engineering sheet from a small JSON spec and premade assets: lettered panels, mechanism diagrams, annotated examples, tables, limits and flows, to open yourself or publish for others. "/show-me flow" maps what was built as a user flow: every screen and decision, joined by labelled links (errors in red, returns dashed), with zoom, a full-size view of each screen, a light and dark switch and review marks.'
disable-model-invocation: true
argument-hint: '[sheet | flow | share] [topic]'
---

# show-me

Show the idea, do not describe it. The reader understands a picture faster than a paragraph.

Arguments: $ARGUMENTS

If the first word is `sheet`, `flow` or `share`, it picks the page (levels 4 to 6 below) and the rest is the topic. With no mode word, the arguments are the topic and you pick the level. With no arguments, the topic is the current conversation.

## Pick the level

Climb only as far as the point needs. Stop at the first level that makes it clear.

| Level | Use when | Form |
|---|---|---|
| 1. Words | One fact or one rule | Two or three sentences in Simplified Technical English (below) |
| 2. Text picture | Logic, calls, files, a change | A code block in the chat (shapes below) |
| 3. Diagram | Several parts talk to each other, or a lifecycle | Up to 4 boxes in one line: a text box diagram in a code block. More boxes, branches or loops: a one-panel sheet (level 4), opened for the reader |
| 4. Sheet | Many related parts, a comparison, or the reader asked for `sheet` or `share` | One HTML page built from a JSON spec |
| 5. Walkthrough page | Understanding how something works and why, with more than one view (usually from `/walk-me-through`) | One HTML page with tabs and a guided tour per tab |
| 6. Flow page | A user journey through UI states: success, loading, errors, retry, permission branches, or the reader asked for `flow` | One HTML page: a map of screens and decisions, a full-size view, review marks |

**Never put Mermaid, SVG or HTML in the chat.** The terminal shows them as source code, not as a picture. A text picture must read correctly in a monospace code block; if it does not, build a page.

**Start from an example.** `examples/README.md` lists one spec per kind of page: sheets, a walkthrough, and flows with mock-ups, real screenshots or no screens. Copy the closest one before you write a spec from nothing.

## Level 2: text pictures

Pick the one shape that fits. Use a second only if it shows something the first cannot.

- **Logic** as pseudocode: `on(save) / if unchanged / return cached`.
- **Runtime flow** as a call tree, indented by who calls whom.
- **UI** as a component tree, with the state and module boundaries that matter and the file of each.
- **Ownership** as a shallow file tree with one comment per folder: what it owns.
- **A change** as a `diff` of whichever shape above fits: `+` new, `-` gone.
- **The whole block** only when most of it is new or the reader needs a copyable target.

Keep only the calls, files, props and states that answer the current question. Put each picture next to the one sentence it supports.

## Level 4: the sheet

An engineering sheet: a title block, a short answer at the top, then lettered panels A, B, C in reading order. Each panel makes one point and proves it with one exhibit.

**Where it lives.** Every sheet gets its own folder, chosen once when the request starts, and reused for every fix of that sheet:

```
.show-me/<YYYY-MM-DD>-<topic-slug>/
  sheet.json     what you write
  sheet.html     what build.py makes
  shots/         desktop.png, phone.png, dark.png
```

Put `.show-me/` in the working directory, or where the user names. In a git repo, add `.show-me/` to `.git/info/exclude` (local only, never edit the repo's `.gitignore`) unless the user wants sheets committed. A new request gets a new folder, so earlier sheets stay intact.

You write only the content, as a small JSON file. `scripts/build.py` adds the premade layout, CSS, both themes and the diagram drawing, then runs the checks. Do not write or read HTML or CSS for a sheet.

1. **Read first.** Get the real names, numbers, paths and examples. Never invent data; label a guess as a guess. A claim about code carries its `file:line`.
2. **Write the lead and the panel titles first.** The lead is the answer in one sentence plus two or three points. Each panel title is its point as a sentence that can be true or false, at most 12 words: "Three skills can start on their own.", not "Triggers". At most 6 panels. Read the lead and titles in order; they must tell the whole story. For a plan or a change, end with a panel that says what does not change.
3. **Give each panel exactly one exhibit**:

```json
{
  "title": "Name Of The Sheet",
  "meta": "subject · source · date",
  "lead": {"answer": "One sentence.", "points": ["Point one.", "Point two."]},
  "panels": [
    {"title": "A sentence that states the point.", "ref": "where it comes from", "caption": "Optional: what to notice.",
     "half": false,

     "diagram": {"nodes": [{"id": "api", "label": "API", "sub": "owns the read", "col": 0, "row": 0, "store": false, "new": false}],
                 "edges": [{"from": "api", "to": "db", "label": "on miss: query", "new": true}]},
     "tree": {"root": "name", "sub": "role", "items": [["`child/`", "what it owns"]]},
     "anno": [{"text": "part of a real line", "why": "what to notice", "kind": "note | wrong"}],
     "table": {"head": ["Option", "Status"], "rows": [["One", "ok: Holds"], ["Two", "bad: Breaks at 10x"]]},
     "limits": [{"label": "Measured thing", "value": "14 of 20", "pct": 70}],
     "flow": [{"text": "Step"}, {"text": "New step", "new": true}],
     "timeline": [["2024", "started"], ["Now", "today"]]}
  ]
}
```

   Use one exhibit key per panel, not all of them. `` `x` `` in any text becomes code. `"half": true` sets two short panels side by side.

   Three more exhibits, mostly for walkthroughs:

```json
"path": [{"where": "`file.py:40` or 'Support desk'", "what": "What happens here.", "passes": "What goes to the next step"}],
"decisions": [{"choice": "What was chosen", "over": ["What lost"], "why": "The reason", "confidence": "direct | supported | inferred | unknown", "source": "Where it is written"}],
"gaps": [{"question": "What we could not find", "looked": "Where we looked", "ask": "Who could answer"}],
"code": {"where": "file.py:40", "text": "the snippet"}
```

   A decision without a source must be `unknown`; the builder refuses it otherwise.

   Three drawn exhibits for what boxes and arrows show badly (example: `examples/walkthroughs/exhibit-gallery.json`):

```json
"sequence": {"actors": ["Browser", "API", "DB"],
             "messages": [{"from": "Browser", "to": "API", "text": "POST /login"},
                          {"from": "API", "to": "API", "text": "check rate limit"},
                          {"from": "API", "to": "Browser", "text": "401", "reply": true, "error": true}]},
"schema": {"tables": [{"name": "users", "columns": [["id", "uuid", "pk"], ["email", "text"]]},
                      {"name": "orders", "columns": [["id", "uuid", "pk"], ["user_id", "uuid", "fk users.id"]]}]},
"schedule": {"start": "2026-10-01", "end": "2026-12-31", "today": "2026-10-26",
             "rows": [{"label": "Design", "from": "2026-10-01", "to": "2026-10-20", "status": "done"},
                      {"label": "Build", "from": "2026-10-20", "to": "2026-11-30", "status": "late"},
                      {"label": "Beta", "from": "2026-12-01", "to": "2026-12-20", "status": "new"}]}
```

   - `sequence` is for who calls whom, in time order. `reply` is dashed, `error` is red, `new` is blue, and a message to the same actor loops back.
   - `schema` is for tables and keys. Mark a column `pk` or `fk table.column`; the builder draws each foreign key from that column. Do not list links yourself.
   - `schedule` is for work over time. `status` is `done` (green), `late` (red) or `new` (blue, dashed, for planned work); no status is grey.

4. **Diagrams: draw the mechanism, not its name.** Pick `diagram` when the point is which parts talk, where data flows, or the hop being added.
   - Leave out `col` and `row` and the builder places the boxes left to right, in the order the arrows run. Set them only to fix a layout; a node can set just one of them. A state machine is a diagram whose arrows are labelled with events.
   - Keep to 9 boxes, 12 arrows and 1 or 2 parts marked `new`. The builder warns above that: it is probably two diagrams.
   - Show only the parts the point depends on. To compare options, draw the edge each option adds or removes.
   - Label every edge with what it does: `writes`, `on miss: query`, `polls every 30 s`.
   - Edges go straight or with one bend. If two edges would cross or pass through a box, move the nodes.
   - `new` is dashed blue: new, proposed, or a step the reader runs. `store` is a filled box for data at rest.
5. **Colour means something or it is not used.** Normal is ink, new is blue and dashed, `ok:` is green, `bad:` is red. No other colour.
**Walkthrough pages.** Replace `panels` with `views`. Each view is a tab with a short guided tour; each step is one point, with an optional `body` and at most one exhibit:

```json
{"title": "...", "meta": "...", "lead": {"answer": "...", "points": ["..."]},
 "views": [
   {"label": "Flow", "summary": "What happens when a person signs in.",
    "steps": [
      {"title": "A sentence that states this step's point.", "body": "One or two sentences.", "path": [...]},
      {"title": "...", "diagram": {...}}]}]}
```

   Steps open one at a time with Previous / Next (or the arrow keys); number keys switch views. To build a picture up, repeat the diagram in the next step with one more node, marked `new`. There is no word cap on a walkthrough; keep each step to one point instead. For review screenshots, build a copy with `--open-all`: every view and step open.

**Flow pages.** Use it to show what was built as a user flow, so a person can review it the way they review a design. Replace `panels` with `flows`. A flow is a graph: `states` are screens or decisions, `links` join them.

```json
{"title": "...", "meta": "...", "lead": {"answer": "...", "points": ["..."]},
 "flows": [
   {"id": "sign-in", "label": "Sign in", "platform": "iOS", "frame": "phone", "start": "form",
    "summary": "One sentence: where the flow starts and ends.",
    "states": [
      {"id": "form", "title": "Sign in", "sub": "Empty form", "note": "Shows in the full-size view.", "image": "shots/form.png"},
      {"id": "email-ok", "decision": "Email looks valid?"},
      {"id": "bad-email", "title": "Sign in", "sub": "Email is not valid", "html": "<div style='padding:24px;color:var(--ink)'>…</div>"}],
    "links": [
      {"from": "form", "to": "email-ok", "label": "Tap Sign in"},
      {"from": "email-ok", "to": "bad-email", "label": "No", "error": true},
      {"from": "bad-email", "to": "email-ok", "label": "Fix and tap again"}]}]}
```

   - **Read the real UI first.** Map the entry point, the actions, and the success, loading, error, retry and permission states that matter. Do not invent screens to fill the map.
   - **A screen** has a `title`, an optional `sub` (which variant it is) and `note`, and one picture: `image` (a real screenshot, a path from the JSON folder; prefer this), `html` (a mock-up that uses the CSS variables such as `var(--ink)` and `var(--note)` so both themes work, with no `id` attributes), or one exhibit above.
   - **A decision** is a question the app answers, such as `"Billing active?"`. Its links carry the answers: `Yes`, `No`, `Failed`.
   - **Every link has a label**: what the user did or what the system answered. Mark failure paths `"error": true`; they are red. A link back to an earlier state is found by the builder and drawn dashed. Do not mark it.
   - Every state must be reachable from `start`. The builder places states left to right and orders each column to cut crossings. When it warns about crossings, set `"row": 0, 1, …` to order a column, or `"col"` to move a state.
   - `frame` is `phone`, `browser` or `none`. `width` is the screen width in pixels (default 390 for `phone`, 720 otherwise). Screenshots are stored once, and shrunk to twice that width when Pillow is installed.
   - More than one flow adds a flow picker. Keep flow and state ids stable: review marks are stored under them in the reader's browser, and a mark clears by itself when its screen changes.

   Readers drag or scroll to move the map, use `−`, `+`, `Fit to screen`, Ctrl + wheel or the `+`, `-`, `0` keys to zoom, and click a screen or decision to see it full size. The full-size view lists where it comes from and where each link goes, with left and right arrow keys to step back and forward; the path from the start is drawn in blue on the map. `#flow-id/state-id` in the link opens that state. Flow pages need JavaScript.

6. **Build**: `python3 <this skill>/scripts/build.py .show-me/<folder>/sheet.json` writes `sheet.html` beside it and checks it. Errors fail on contrast under 4.5:1 in either theme, text under 14 px, no lead, or more than 6 panels (sheets only). Warnings flag label-style titles, unlabelled arrows, sentences over 25 words, more than 450 words and words to replace. Fix the JSON and build again.
7. **Look at it.** Take screenshots at desktop width, at phone width and in dark mode, into the folder's `shots/`, for example `chromium --headless --screenshot=.show-me/<folder>/shots/desktop.png --window-size=1400,1500 file:///full/path/sheet.html`; for dark, add `data-theme="dark"` to `<html>` in a copy. Read each one. Fix clipped text, overlaps, crossed lines and anything hard to read. At most two rounds of fixes. If you could not take screenshots, say so; never report that it looks right unseen.
8. **Need a part the builder does not have?** Build first, then add it by hand to the HTML, using the CSS variables (`--ink`, `--note`, `--ok`, `--bad`, `--muted`, `--paper`, `--fill`) so both themes work, and run `scripts/check.py sheet.html`.

Then hand it over:

- **For you** (`/show-me sheet`): give the full path of `sheet.html` and open it (`xdg-open` or `open`).
- **For others** (`/show-me share`): publish it as a private Artifact if the tool exists and give the link. Before you publish, remove anything private: hostnames, IPs, customer names, keys.

## Writing

Write prose about 80% of the way to ASD-STE100 Simplified Technical English:

- One topic per sentence. At most 20 words for an instruction, 25 for a description.
- Active voice: say who does what.
- Simple tenses. Use `must` for a rule and `can` for what is possible.
- Short common words: use, do, get, start, stop, show, before, to.
- One name for one thing, every time. Names from the code stay exact.
- No idioms, metaphors or jokes.

Code, quotes and UI labels stay as they are.

## Do not

- Write a prose explanation first and a picture after. The picture comes first.
- Use more than the point needs. One clear text picture beats a sheet.
- Draw boxes for decoration. Every line, mark and colour must carry meaning.
