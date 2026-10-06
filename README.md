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
| `/lets-build-pyramids` | Architecture review before a feature is built: researches how others solved it, looks at it from six views, compares three real designs at today's size, 10x and 100x, and runs a pre-mortem. | You or the agent |
| `/but-why` | First-principles redesign: separates facts from inherited choices and habits, then rebuilds the design from the facts. | You or the agent |
| `/brooooo` | Press it when a reply did not land or the agent got something wrong. It restates plainly, or owns the mistake and fixes it. | You |
| `/no-added-comments` | Keeps diffs free of comments the agent added. | You or the agent |

"You or the agent" means you can type it, and the agent also starts it on its own when the task matches.

### Turning just-tell-me off

- For one session: say "stop just-tell-me".
- For good: fork the repo and delete `hooks/`.

## Evals

`evals/` holds cases for `claude plugin eval`. Each case runs with and without the plugin, so the score shows what the plugin adds.

```
claude plugin eval . --runs 3 --allow-tools WebSearch WebFetch
```

Latest run of `lets-build-pyramids`, 3 runs per case:

| Case | With plugin | Without |
|---|---|---|
| Audit log for a multi-tenant SaaS | 0.90 | 0.57 |
| Daily digest email for 50k users | 1.00 | 0.67 |

## Adding a skill

1. Create `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
2. Add a row to the table above and to `skills/onmywatch/SKILL.md`.
3. Add an eval case under `evals/<name>/` if the skill changes how the agent works.
4. Bump `version` in `.claude-plugin/plugin.json`.

## Credits

- `just-tell-me` adapts [i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub Ghriss (MIT).
- `brooooo` adapts `bro`, and `but-why` adapts `principle-redesign-from-first-principles` and `principle-attack-the-premise`, from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT).

## License

[MIT](LICENSE)
