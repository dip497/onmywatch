"""Build a fake Claude config dir for read-my-mind evals: two git repos (one with a worktree)
and session transcripts in which the user repeats the same corrections.

Usage: python3 fixtures.py first-run|incremental   (run from the eval case's working folder)
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path.cwd()
CLAUDE = ROOT / "claude"


def git(*args, cwd):
    subprocess.run(["git", *args], cwd=cwd, check=True, capture_output=True)


def repo(name, remote):
    path = ROOT / "code" / name
    path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", "-b", "main", cwd=path)
    git("-c", "user.email=e@x", "-c", "user.name=e", "commit", "-q", "--allow-empty", "-m", "init", cwd=path)
    git("remote", "add", "origin", remote, cwd=path)
    return path


def session(sid, cwd, turns, age_days):
    folder = CLAUDE / "projects" / str(cwd).replace("/", "-")
    folder.mkdir(parents=True, exist_ok=True)
    lines = []
    for i, (role, text) in enumerate(turns):
        rec = {"type": role, "sessionId": sid, "cwd": str(cwd), "gitBranch": "main",
               "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime(time.time() - age_days * 86400 + i * 60)),
               "uuid": f"{sid}-{i}", "isSidechain": False, "userType": "external", "entrypoint": "cli"}
        if role == "user":
            rec["message"] = {"role": "user", "content": text}
            rec["origin"] = {"kind": "human"}
        else:
            rec["message"] = {"role": "assistant", "content": [{"type": "text", "text": text}]}
        lines.append(json.dumps(rec))
    f = folder / f"{sid}.jsonl"
    f.write_text("\n".join(lines) + "\n")
    t = time.time() - age_days * 86400
    os.utime(f, (t, t))
    return f


shop = repo("shop", "git@github.com:Acme/Shop.git")
blog = repo("blog", "https://github.com/acme/blog.git")
git("worktree", "add", "-q", str(ROOT / "code" / "shop-wt"), "-b", "feature", cwd=shop)
wt = ROOT / "code" / "shop-wt"

s1 = session("11111111-aaaa", shop, [
    ("user", "Build the orders page that lists every order with its status."),
    ("assistant", "Done. The orders page is at /orders, with a table of orders and their status. Tests pass."),
    ("user", "There is no link to the orders page anywhere in the menu, how would anyone find it?? I had to type the URL."),
    ("assistant", "You are right. Should I add it to the sidebar?"),
    ("user", "Do not ask me to fix it. You find the issue, fix it and verify it yourself."),
], age_days=6)
s2 = session("22222222-bbbb", wt, [
    ("user", "Add a reports page with monthly sales."),
    ("assistant", "The reports page is done at /reports with a monthly sales chart."),
    ("user", "Again no menu entry for reports. Every new page must be reachable from the navigation."),
], age_days=5)
s3 = session("33333333-cccc", blog, [
    ("user", "Fix the broken image on the about page."),
    ("assistant", "I found the image path is wrong. Do you want me to fix it?"),
    ("user", "Why are you asking? Don't ask me, just fix it and check it in the browser."),
], age_days=4)

if sys.argv[1] == "incremental":
    # s1-s3 were analysed two days ago; s4 is new.
    ledger = {"files": {}, "last_run_epoch": time.time() - 2 * 86400, "last_run": "20260101-000000"}
    for f in (s1, s2, s3):
        st = f.stat()
        ledger["files"][str(f)] = {"offset": st.st_size, "size": st.st_size, "mtime": st.st_mtime,
                                   "context": "", "agent_ran": False}
    state = CLAUDE / "read-my-mind"
    state.mkdir(parents=True, exist_ok=True)
    (state / "ledger.json").write_text(json.dumps(ledger))
    mem = CLAUDE / "agent-memory" / "mind-reader"
    (mem / "projects").mkdir(parents=True, exist_ok=True)
    (mem / "projects" / "github.com-acme-shop.md").write_text(
        "# github.com/acme/shop\n\nUpdated 2026-01-01 · 2 sessions read · 4 messages\n\n## Ask before saying done\n\n"
        "| # | Ask yourself | Rule | Seen | Last | Missed |\n|---|---|---|---|---|---|\n"
        "| P1 | Can a user reach every new page from the navigation menu? | Every new page has a menu entry. | 2 | 2026-01-01 | 0 |\n\n"
        "## Standing rules\n\n| # | Rule | User's words | Seen | Last |\n|---|---|---|---|---|\n\n"
        "## Taste\n\n| # | Prefer | Over | Seen | Last |\n|---|---|---|---|---|\n\n## Asleep\n")
    (mem / "MEMORY.md").write_text(
        "# How the user thinks\n\n## Ask before saying done\n\n| # | Ask yourself | Rule | Seen | Last | Missed |\n|---|---|---|---|---|---|\n"
        "| G1 | Did I fix and verify it myself instead of asking the user for permission? | Find, fix, verify; do not ask. | 2 | 2026-01-01 | 0 |\n\n"
        "## Project index\n\n<!-- index:start -->\n<!-- index:end -->\n")
    session("44444444-dddd", shop, [
        ("user", "Add an invoices page."),
        ("assistant", "The invoices page is ready at /invoices. All tests pass."),
        ("user", "And again: no menu link to invoices. I keep telling you this."),
    ], age_days=0)
print("fixtures ready in", CLAUDE)
