#!/usr/bin/env bash
# Skills injected at every session start. Each turns off with "stop <name>".
for name in just-tell-me talk-is-cheap; do
  f="$(dirname "$0")/../skills/$name/SKILL.md"
  [ -f "$f" ] || continue
  echo "${name^^} MODE ACTIVE. The rules below apply to every reply. \"stop $name\" turns it off for this session."
  echo
  dir="$(cd "$(dirname "$f")" && pwd)"
  awk 'NR==1&&/^---/{fm=1;next} fm&&/^---/{fm=0;next} !fm' "$f" | sed "s#\`references/#\`$dir/references/#g"
  echo
done
# read-my-mind: once the user has a mind-reader agent, have it review work before it is reported done.
if [ -f "${CLAUDE_CONFIG_DIR:-$HOME/.claude}/agents/mind-reader.md" ]; then
  echo "MIND-READER ACTIVE. Before you report a feature, fix, UI change, design or plan as done, run the mind-reader agent on it and fix what it finds. It asks the questions this user keeps asking."
fi
