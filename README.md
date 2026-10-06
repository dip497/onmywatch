# onmywatch

How I work with coding agents, as a plugin. Generic on purpose: nothing here names a company, product, host or tenant.

## Install

```
/plugin marketplace add <github-user>/onmywatch
/plugin install onmywatch@onmywatch
```

## Use

Start a task with `/onmywatch`. It routes to the other skills.

## Skills

| Skill | Use it when |
|---|---|
| `/onmywatch` | Start of any non-trivial task. |
| `/just-tell-me` | On in every session. Replies lead with the action, number steps, say where we are, end with one next step. |
| `/first-principles` | Separates what must be true from what is inherited, then rebuilds the design from the facts. |
| `/brooooo` | Restates a reply that did not land, or owns a mistake and fixes it. |
| `/no-added-comments` | You write or change code. |

## Adding a skill

1. `skills/<name>/SKILL.md` with `name` and `description` frontmatter.
2. One row here and one row in `skills/onmywatch/SKILL.md`.
3. Before pushing: grep the repo for your employer's name, internal hostnames and private IPs. It must print nothing.

## Credits

`just-tell-me` adapts [i-have-adhd](https://github.com/ayghri/i-have-adhd) by Ayoub Ghriss (MIT). `brooooo` adapts `bro` from [pstack](https://github.com/cursor/plugins/tree/main/pstack) by Lauren Tan (MIT). `first-principles` adapts `principle-redesign-from-first-principles` and `principle-attack-the-premise` from the same.

## License

MIT
