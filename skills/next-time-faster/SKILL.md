---
name: next-time-faster
description: 'Run at the end of a long session. Finds the work that cost time and will come back (setting up the environment, starting servers, logins, repeated commands, manual checks, things the user had to explain) and turns only what earns it into the lightest fix: nothing, a doc pointer, a script, a hook, or as a last resort a skill. Proposes first, builds only after approval, proves what it builds.'
disable-model-invocation: true
---

# next-time-faster

Make the next session on this work faster than this one. Most findings are not skills; a new skill is the last resort.

Session: the current one, or $ARGUMENTS if given.

## 1. Mine the session

You already have this session in context; read it from there. List each item with its evidence (the turns or commands, and how many times):

- Commands run more than once with small changes: start, stop, restart, health check, build, seed, login.
- Environment setup: venvs, env vars, ports, tokens, containers, paths.
- Failed attempts and retries before something worked.
- Things the user had to tell the agent: where a file is, how to run something, a rule.
- Long searches for a file, a command or a fact.
- Checks done by hand that a script could do.

To see if a pain recurs, grep (do not read in full) the last 10 transcripts in `~/.claude/projects/<this project's folder>/`, where the folder is the working directory with `/` replaced by `-`, for the same commands or corrections. Never read other projects' folders.

## 2. Gate each candidate

Answer all three. A "no" drops it.

1. **Will it come back?** Seen in 2 or more sessions, or certain to recur (a server you start every session). A one-off is dropped.
2. **Is it covered already?** Check the repo's scripts, Makefile, `package.json`, AGENTS.md, CLAUDE.md, docs, and installed skills. If something covers it, the finding is "it exists but was not found or not used": fix the pointer or the existing item. Never build a second copy.
3. **Is it worth it?** Estimate time lost per session against the time to build it, in agent minutes.

## 3. Pick the lightest fix that holds

| Fix | Use when |
|---|---|
| Nothing | One-off, or saves under a minute |
| Edit an existing skill, script or doc | It exists but is wrong, incomplete or hard to find |
| One line in AGENTS.md or CLAUDE.md | A fact every session in this repo needs, usually a pointer: "run `make check` before committing". These files load into every session, so keep them short |
| A script in the repo | Exact steps, the same every time: `scripts/dev-up.sh`, `scripts/reset-db.sh` |
| A check (lint, test, CI) | A mistake a machine can catch |
| A hook | It must happen at a fixed moment without anyone asking |
| A new skill | A recurring workflow that needs judgement plus a procedure, or its own rules the user keeps repeating. Its rules belong in the skill, which loads only when that work comes up, not in AGENTS.md or CLAUDE.md |

Put it in the right place:

- Used only in this repo: in the repo (`scripts/`, `.claude/skills/`), committed, so every worktree gets it.
- Used across one employer's repos: that employer's private plugin.
- General and personal: the personal plugin.

Never put secrets in a script; read them from the environment or a secrets tool by name.

## 4. Propose, then stop

Show one table and wait:

| # | Pain (evidence) | Seen | Lost per session | Fix | Where | Verdict |
|---|---|---|---|---|---|---|
| 1 | Server restarted by hand 4 times | 3 sessions | ~6 min | `scripts/dev-up.sh` with health check | repo | Build |
| 2 | Column rename migration | once | n/a | none | n/a | Drop: one-off |

Verdicts: **Build**, **Park** (real but not yet worth it; write it to the backlog), or **Drop**, each with a one-line reason. Expect 0 to 2 builds. Zero is a valid answer: say "nothing worth automating" and stop.

Parked items go to `docs/agent-backlog.md` in the repo (personal ones to `~/.claude/next-time-faster-backlog.md`) with the date and evidence. On the next run, read the backlog first: a parked item seen again moves up to Build.

## 5. Build what was approved, and prove it

- A script: run it once and show the output. Make it safe to rerun.
- A doc or AGENTS.md line: one line, a pointer, not a manual.
- A hook: show the event, the command, and that it ran.
- A new skill: follow `/skill-creator` or `/writing-for-agents`, add an eval case under the plugin's `evals/<skill>/`, and run it with and without the skill. No gain means it is not kept.

Report what was built, where, and the proof. Commit only when the user asks.
