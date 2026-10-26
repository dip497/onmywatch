#!/usr/bin/env bash
# Skills injected at every session start. Each turns off with "stop <name>".
# Claude Code and Codex read plain stdout. Cursor needs --json: {"additional_context": "..."}.
rules() {
  for name in just-tell-me talk-is-cheap; do
    f="$(dirname "$0")/../skills/$name/SKILL.md"
    [ -f "$f" ] || continue
    echo "${name^^} MODE ACTIVE. The rules below apply to every reply. \"stop $name\" turns it off for this session."
    echo
    dir="$(cd "$(dirname "$f")" && pwd)"
    awk 'NR==1&&/^---/{fm=1;next} fm&&/^---/{fm=0;next} !fm' "$f" | sed "s#\`references/#\`$dir/references/#g"
    echo
  done
}
if [ "$1" = "--json" ]; then
  rules | python3 -c 'import json,sys; print(json.dumps({"additional_context": sys.stdin.read()}))'
else
  rules
fi
