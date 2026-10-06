---
name: blueprint
description: 'Make the current topic visible instead of explaining it in prose. "/blueprint" shows you: the smallest picture in the chat (pseudocode, call tree, file tree, diff, Mermaid). "/blueprint sheet" or "/blueprint share" makes one HTML engineering sheet from a small JSON spec and premade assets: lettered panels, mechanism diagrams, annotated examples, tables, limits and flows, to open yourself or publish for others.'
disable-model-invocation: true
---

# blueprint

Show the idea, do not describe it. The reader understands a picture faster than a paragraph.

Topic: the current conversation, or $ARGUMENTS if given.

## Pick the level

Climb only as far as the point needs. Stop at the first level that makes it clear.

| Level | Use when | Form |
|---|---|---|
| 1. Words | One fact or one rule | Two or three sentences in Simplified Technical English (below) |
| 2. Text picture | Logic, calls, files, a change | A code block in the chat (shapes below) |
| 3. Diagram | Several parts talk to each other, or a lifecycle | Mermaid in the chat |
| 4. Sheet | Many related parts, a comparison, or the reader asked for `sheet` or `share` | One HTML file built from a JSON spec |

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

4. **Diagrams: draw the mechanism, not its name.** Pick `diagram` when the point is which parts talk, where data flows, or the hop being added.
   - Place nodes on a grid with `col` and `row`. Main path left to right on row 0; stores and branches directly below their owner. At most 3 columns.
   - Show only the parts the point depends on. To compare options, draw the edge each option adds or removes.
   - Label every edge with what it does: `writes`, `on miss: query`, `polls every 30 s`.
   - Edges go straight or with one bend. If two edges would cross or pass through a box, move the nodes.
   - `new` is dashed blue: new, proposed, or a step the reader runs. `store` is a filled box for data at rest.
5. **Colour means something or it is not used.** Normal is ink, new is blue and dashed, `ok:` is green, `bad:` is red. No other colour.
6. **Build**: `python3 <this skill>/scripts/build.py sheet.json` writes `sheet.html` and checks it. Errors fail on contrast under 4.5:1 in either theme, text under 14 px, no lead, or more than 6 panels. Warnings flag label-style titles, unlabelled arrows, sentences over 25 words, more than 450 words and words to replace. Fix the JSON and build again.
7. **Look at it.** Take screenshots at desktop width, at phone width and in dark mode, for example `chromium --headless --screenshot=out.png --window-size=1400,1500 file:///full/path/sheet.html`; for dark, add `data-theme="dark"` to `<html>` in a copy. Read each one. Fix clipped text, overlaps, crossed lines and anything hard to read. At most two rounds of fixes. If you could not take screenshots, say so; never report that it looks right unseen.
8. **Need a part the builder does not have?** Build first, then add it by hand to the HTML, using the CSS variables (`--ink`, `--note`, `--ok`, `--bad`, `--muted`, `--paper`, `--fill`) so both themes work, and run `scripts/check.py sheet.html`.

Then hand it over:

- **For you** (`/blueprint sheet`): save it in the scratch folder, or where the project keeps docs, and open it (`xdg-open` or `open`).
- **For others** (`/blueprint share`): publish it as a private Artifact if the tool exists and give the link. Before you publish, remove anything private: hostnames, IPs, customer names, keys.

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
