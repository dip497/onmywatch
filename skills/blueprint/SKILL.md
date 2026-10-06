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

An engineering drawing sheet: a frame with zone numbers and letters, a title block, and lettered panels A, B, C. Each panel answers one question and holds one exhibit.

1. **Read first.** Get the real names, numbers, paths and examples. Never invent data for a sheet; if a value is a guess, label it as one.
2. **List the panels**, at most 6. Write each panel's question as its title: "Document structure", "What breaks at 10x". Read the titles in order; together they must tell the whole story.
3. **Pick one exhibit per panel** from the template's parts:

   | Part | Shows |
   |---|---|
   | `.tree` | Structure, ownership, a hierarchy |
   | `.anno` | One real line (code, a sentence, a command) with each part bracketed and named |
   | `table` with `.ok` / `.bad` | A comparison, options, allowed against not allowed |
   | `.limit` | A value against its maximum |
   | `.flow` | Steps or data flow; dashed `.new` boxes are proposed |
   | `.timeline` | Order in time, versions, phases |
   | Inline SVG | Anything the parts above cannot draw |

4. **Copy `assets/sheet.html`**, keep its tokens and CSS, and replace the example panels. Size panels with `w6`, `w8`, `w12` so each row adds up to 12. Delete parts you do not use.
5. **Words on the sheet** follow the writing rules below. A caption is one sentence: what to notice. A note under an `.anno` bracket is a few words.
6. **Check it.** Open it in a browser if you can, at desktop and phone width. Nothing clipped, no horizontal scroll, labels do not overlap.

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
