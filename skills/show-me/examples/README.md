# show-me examples

Each example is a JSON spec and the HTML page built from it, grouped by the key that picks the kind of page. Copy the spec closest to what you need, change the content, and build it.

Start with [`sheets/pick-a-page`](sheets/pick-a-page.json): it says which page fits which question.

## `sheets/`: one page of lettered panels (`panels`)

| Example | Shows how to |
|---|---|
| [`pick-a-page`](sheets/pick-a-page.json) | choose between the chat, a sheet, a walkthrough and a flow page |
| [`how-onmywatch-works`](sheets/how-onmywatch-works.json) | explain a codebase with a tree, an annotated line, a table, limits and a diagram |
| [`flow-layout-choice`](sheets/flow-layout-choice.json) | record a design choice: the options, the mechanism and the numbers behind it |

## `walkthroughs/`: tabs with guided steps (`views`)

| Example | Shows how to |
|---|---|
| [`how-build-works`](walkthroughs/how-build-works.json) | explain how code works, step by step, with `file:line`, decisions and gaps |
| [`exhibit-gallery`](walkthroughs/exhibit-gallery.json) | use each of the 14 exhibits; copy a step to start your own |

## `flows/`: a map of screens and decisions (`flows`)

| Example | Shows how to |
|---|---|
| [`sign-in-flow`](flows/sign-in-flow.json) | map an app with HTML mock-ups, phone frames, two flows and a picker |
| [`review-a-flow`](flows/review-a-flow.json) | map real screenshots (`image`) in a browser frame; the shots are in `flows/review-shots/` |
| [`plugin-release`](flows/plugin-release.json) | map a process with no screens, using `code` and `table` as states |

## Build one

```bash
python3 skills/show-me/scripts/build.py skills/show-me/examples/flows/sign-in-flow.json
xdg-open skills/show-me/examples/flows/sign-in-flow.html
```

The build writes the HTML next to the spec and runs `check.py` on it.
