---
name: blueprint
description: 'Make the current topic visible instead of explaining it in prose. "/blueprint" shows you: the smallest picture in the chat (pseudocode, call tree, file tree, diff, Mermaid). "/blueprint sheet" or "/blueprint share" makes one HTML engineering sheet: lettered panels, annotated examples, tables, limits and flows, to open yourself or publish for others.'
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
| 4. Sheet | Many related parts, a comparison, a UI, or the reader asked for `sheet` or `share` | One HTML file from `assets/sheet.html` |

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

1. **Read first.** Get the real names, numbers, paths and examples. Never invent data for a sheet; if a value is a guess, label it as one.
2. **Write the lead**: the answer in one sentence, then two or three supporting points. A reader who stops here must still have the answer.
3. **List the panels**, at most 6. Each panel title is its point as a sentence that can be true or false: "Three skills can start on their own." Not a label like "Triggers". Read the lead and the titles in order; together they must tell the whole story.
4. **Pick one exhibit per panel** from the template's parts:

   | Part | Shows |
   |---|---|
   | `.tree` | Structure, ownership, a hierarchy (at most 6 children) |
   | `.anno` | One real line (code, a sentence, a command) with each part bracketed and named |
   | `table` with `.ok` / `.bad` | A comparison or allowed against not allowed (at most 7 rows, 4 columns) |
   | `.limit` | A value against its maximum |
   | `.flow` | Steps or data flow; dashed `.new` boxes are new or are steps the reader runs |
   | `.timeline` | Order in time, versions, phases |
   | Inline SVG | Anything the parts above cannot draw |

5. **Copy `assets/sheet.html`.** Keep its tokens and CSS. Replace the example lead and panels. Panels are full width; use `w6` only for two short panels that belong side by side. Delete parts you do not use.
6. **Keep it readable.** Body text 17px; no text under 14px; no grey italic; text contrast 4.5:1 or more in both themes. Do not add CSS that breaks these.
7. **Words on the sheet** follow the writing rules below. A caption is one sentence. A note under an `.anno` bracket is at most 6 words.
8. **Look at it before you hand it over.** Take screenshots at desktop width, at phone width and in dark mode, for example `chromium --headless --screenshot=out.png --window-size=1400,1500 file:///full/path/sheet.html` (add `data-theme="dark"` on `<html>` for dark). Read each one. Fix any clipped text, overlap, horizontal scroll or text you have to squint at.

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
