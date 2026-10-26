"""Write the Codex and Cursor plugin files from the Claude Code ones.

Usage: python3 scripts/sync-hosts.py          write every generated file
       python3 scripts/sync-hosts.py --check  exit 1 if any generated file is out of date

.claude-plugin/plugin.json owns name, version, description and author. Each skill's frontmatter
owns whether only the user may start it (`disable-model-invocation: true`); Codex reads that from
skills/<name>/agents/openai.yaml instead, so this script writes that file too. All hosts share
skills/ and hooks/; nothing is copied.
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CHECK = "--check" in sys.argv


def as_json(data):
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def user_only(skill_md):
    front = re.match(r"---\n(.*?)\n---", skill_md.read_text(), re.S)
    return bool(front and re.search(r"^disable-model-invocation:\s*true\s*$", front.group(1), re.M))


def wanted():
    claude = json.loads((ROOT / ".claude-plugin/plugin.json").read_text())
    name, desc = claude["name"], claude["description"]
    shared = {"name": name, "version": claude["version"], "description": desc,
              "author": claude["author"], "repository": claude.get("repository"), "license": claude.get("license")}
    files = {
        ".codex-plugin/plugin.json": as_json({**shared, "skills": "./skills/", "hooks": "./hooks/hooks.json"}),
        ".agents/plugins/marketplace.json": as_json({
            "name": name, "interface": {"displayName": name},
            "plugins": [{"name": name, "source": {"source": "local", "path": "./"},
                         "policy": {"installation": "AVAILABLE", "authentication": "ON_INSTALL"},
                         "category": "Coding"}]}),
        ".cursor-plugin/plugin.json": as_json({**shared, "skills": "./skills/", "hooks": "./hooks/cursor-hooks.json"}),
        ".cursor-plugin/marketplace.json": as_json({
            "name": name, "owner": claude["author"],
            "plugins": [{"name": name, "source": "./", "description": desc}]}),
    }
    for skill in sorted((ROOT / "skills").glob("*/SKILL.md")):
        target = f"skills/{skill.parent.name}/agents/openai.yaml"
        files[target] = "policy:\n  allow_implicit_invocation: false\n" if user_only(skill) else None
    return files


stale = []
for rel, text in wanted().items():
    path = ROOT / rel
    current = path.read_text() if path.exists() else None
    if current == text:
        continue
    stale.append(rel)
    if CHECK:
        continue
    if text is None:
        path.unlink()
        if not any(path.parent.iterdir()):
            path.parent.rmdir()
    else:
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text)

if CHECK and stale:
    print("out of date, run python3 scripts/sync-hosts.py:\n  " + "\n  ".join(stale))
    sys.exit(1)
print("\n".join(f"wrote {s}" for s in stale) if stale else "all host files up to date")
