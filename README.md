# onmywatch

A small stack of skills for Claude Code that makes coding agents answer straight, think before they build, and own their mistakes.

"Not on my watch": nothing half-designed, unverified or buried in filler gets past.

## Install

Inside Claude Code:

```
/plugin marketplace add dip497/onmywatch
/plugin install onmywatch@onmywatch
```

Or from a terminal:

```
claude plugin marketplace add dip497/onmywatch
claude plugin install onmywatch@onmywatch
```

Restart Claude Code after installing. To update later:

```
claude plugin marketplace update onmywatch
claude plugin update onmywatch@onmywatch
```

## Skills

| Skill | What it does | How it starts |
|---|---|---|
| `/onmywatch` | Entry point. Reads the task and picks the skills below that apply. | You or the agent |
| `/just-tell-me` | Replies lead with the answer, number the steps, say where the work stands and end with one next step. No filler. | On in every session |
| `/talk-is-cheap` | Senior-engineer lens on every code task: data structures and their invariants first, cost stated, simplest thing that holds, root-cause fixes. Adds an architecture note with a refactor shape when the structure around your change is wrong. Checks 13 quality areas and reports the top 3. | On in every session |
| `/trust-me-bro` | A test must guard behaviour against a real bug, not mirror the code. Gates every new test, rejects tests that prove nothing, audits existing ones. | You or the agent |
| `/lets-build-pyramids` | Architecture review before a feature is built: researches how others solved it, looks at it from six views, compares three real designs at today's size, 10x and 100x, and runs a pre-mortem. | You or the agent |
| `/but-why` | First-principles redesign: separates facts from inherited choices and habits, then rebuilds the design from the facts. | You or the agent |
| `/next-time-faster` | Run at the end of a long session. Finds the setup and steps that cost time and will come back, then proposes the lightest fix that holds: nothing, a doc pointer, a script, a hook, or as a last resort a skill. Builds only after approval and proves what it builds. | You |
| `/brooooo` | Press it when a reply did not land or the agent got something wrong. It restates plainly, or owns the mistake and fixes it. | You |
| `/show-me` | Shows the topic instead of explaining it: a text picture or Mermaid in the chat, or an HTML engineering sheet built from a small JSON spec and premade assets (`/show-me sheet`, `/show-me share`). | You |
| `/no-added-comments` | Keeps diffs free of comments the agent added. | You or the agent |

"You or the agent" means you can type it, and the agent also starts it on its own when the task matches.

### Turning always-on skills off

`just-tell-me` and `talk-is-cheap` start in every session.

- For one session: say "stop just-tell-me" or "stop talk-is-cheap".
- For good: fork the repo and delete `hooks/`.

### show-me sheet

![A show-me sheet explaining onmywatch](skills/show-me/examples/onmywatch.png)

## Evals

Each skill with evals has a folder under `evals/<skill>/<case>/`. A case is either `prompt.md` plus `graders/*.md`, or a `case.yaml` when it needs an earlier conversation (`history.jsonl`) or starting files (`scaffold.sh`). Write the conversation as `history.md` with `## User` and `## Assistant` sections, then convert it:

```
python3 evals/history.py evals/<skill>/<case>/history.md
```

Run one skill's cases:

```
claude plugin eval . --tag lets-build-pyramids --runs 3 --allow-tools WebSearch WebFetch
claude plugin eval . --tag just-tell-me --runs 3 --judge-model sonnet
claude plugin eval . --tag talk-is-cheap trust-me-bro --runs 3 --scaffold --allow-tools Edit Write --judge-model sonnet
claude plugin eval . --tag but-why --runs 3 --scaffold --judge-model sonnet
claude plugin eval . --tag next-time-faster --runs 3 --ablation none --judge-model sonnet
claude plugin eval . --tag brooooo --runs 3 --scaffold --allow-tools Edit Write --judge-model sonnet
```

Latest scores, 3 runs per case:

| Skill | Case | With plugin | Without |
|---|---|---|---|
| `lets-build-pyramids` | Audit log for a multi-tenant SaaS | 0.90 | 0.57 |
| `lets-build-pyramids` | Daily digest email for 50k users | 1.00 | 0.67 |
| `brooooo` | Agent did the opposite of what was asked | 0.90 | n/a |
| `brooooo` | Agent claimed a test passed without running it | 0.83 | n/a |
| `brooooo` | Reply full of jargon | 0.73 | n/a |
| `just-tell-me` | Estimate for a feature, sized in agent time | 1.00 | 0.60 |
| `just-tell-me` | Explain a bug: answer first, under 200 words | 0.89 | 0.83 |
| `just-tell-me` | Unsafe command question, keeps the "no" | 1.00 | 1.00 |
| `just-tell-me` | Vague "make it faster": one short question | 0.67 | 0.33 |
| `just-tell-me` | Partial failure: no invented cause, gives the check | 1.00 | 1.00 |
| `just-tell-me` | Third "still broken": stops and asks for evidence | 0.67 | n/a |
| `just-tell-me` | "Thanks": no invented next step | 1.00 | n/a |
| `but-why` | Fourth fix after three failed: names the shared premise first | 0.73 | 0.20 |
| `but-why` | Users in two orgs: membership table, not a second column | 0.58 | 0.17 |
| `but-why` | Special cases: keeps the rate limit and cites why it exists | 1.00 | 0.44 |
| `but-why` | Small change that fits: no ceremony | 1.00 | 1.00 |
| `talk-is-cheap` | Hotfix next to a duplicated rule: small fix plus architecture note | 1.00 | 0.60 |
| `talk-is-cheap` | Review an unbounded cache: top 3 risks only | 1.00 | 0.75 |
| `talk-is-cheap` | Over-built plan for 200 users: clear verdict, simpler design | 0.89 | 0.67 |
| `talk-is-cheap` | Typo question: no lecture | 1.00 | 0.67 |
| `talk-is-cheap` | Session lookup, duplicate finder (both arms pass) | 1.00 | 1.00 |
| `trust-me-bro` | Mirror test, never-failed regression, keep a contract test, write tests | 0.90–1.00 | 0.83–1.00 |
| `next-time-faster` | Server restarted 4 times by hand: proposes a script, drops the one-off migration | 1.00 | n/a |
| `next-time-faster` | `make check` already exists: a pointer, no duplicate | 1.00 | n/a |
| `next-time-faster` | One-off rename: nothing to automate | 1.00 | n/a |
| `next-time-faster` | Weekly triage with repeated rules: a skill, rules kept out of CLAUDE.md | 1.00 | n/a |

`brooooo` has no "without" score: it is a command you type, so it does not exist without the plugin.

## Adding a skill

1. Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
2. Add a row to the table above and to `skills/onmywatch/SKILL.md`.
3. Add eval cases under `evals/<name>/<case>/` and tag them with the skill name.
4. Bump `version` in `.claude-plugin/plugin.json`.

## Credits

- `just-tell-me` adapts [i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub Ghriss (MIT), with lessons from [caveman](https://github.com/JuliusBrussee/caveman) by Julius Brussee and [caveman-micro](https://github.com/kuba-guzik/caveman-micro).
- `brooooo` adapts `bro`, and `but-why` adapts `principle-redesign-from-first-principles` and `principle-attack-the-premise`, from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT).
- `show-me` draws on [show-me](https://github.com/humanlayer/skills/tree/main/plugins/show-me) by HumanLayer (MIT), the [html-plan](https://github.com/anthropics/claude-plugins-community/tree/main/html-plan) plugin by Thariq Shihipar (MIT), [archify](https://github.com/tt-a1i/archify) by tt-a1i (MIT), Claude's artifact design and diagramming guidance, and Andrej Karpathy's note on asking for STE text, diagrams and HTML instead of prose.
- `talk-is-cheap` adapts the ladder and root-cause rule from [ponytail](https://github.com/DietrichGebert/ponytail) by Dietrich Gebert (MIT), pstack's `model-the-domain` and `foundational-thinking`, and the ISO/IEC 25010 quality model.
- `trust-me-bro` adapts [test-audit](https://github.com/openclaw/openclaw/blob/main/.agents/skills/test-audit/SKILL.md) from openclaw (MIT) and pstack's `principle-test-behavior-not-implementation`.
- `next-time-faster` draws on pstack's `reflect` (including its reviewer and synthesizer prompts), `automate-me`, `encode-lessons-in-structure` and `build-the-lever`, and Matt Pocock's `retro`.

## License

[MIT](LICENSE)
