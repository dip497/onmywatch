#!/usr/bin/env bash
f="$(dirname "$0")/../skills/just-tell-me/SKILL.md"
[ -f "$f" ] || exit 0
echo 'JUST-TELL-ME MODE ACTIVE. The rules below apply to every reply. "stop just-tell-me" turns it off for this session.'
echo
awk 'NR==1&&/^---/{fm=1;next} fm&&/^---/{fm=0;next} !fm' "$f"
