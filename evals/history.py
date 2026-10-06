"""Turn a history.md (## User / ## Assistant sections) into the session JSONL that case.yaml's history_file needs.

Usage: python3 evals/history.py evals/<skill>/<case>/history.md
"""
import json
import re
import sys
import uuid
from pathlib import Path

src = Path(sys.argv[1])
turns = re.findall(r"^## (User|Assistant)\n(.*?)(?=^## (?:User|Assistant)\n|\Z)", src.read_text(), re.M | re.S)
session = str(uuid.uuid4())
parent = None
lines = []
for i, (role, text) in enumerate(turns):
    role = role.lower()
    content = text.strip() if role == "user" else [{"type": "text", "text": text.strip()}]
    message = {"role": role, "content": content}
    if role == "assistant":
        message.update(type="message", model="claude-opus-5-5", id=f"msg_{uuid.uuid4().hex}", stop_reason="end_turn")
    me = str(uuid.uuid4())
    lines.append({
        "parentUuid": parent, "isSidechain": False, "type": role, "message": message, "uuid": me,
        "timestamp": f"2026-01-01T00:00:{i:02d}.000Z", "userType": "external", "cwd": ".", "sessionId": session,
    })
    parent = me
out = src.with_suffix(".jsonl")
out.write_text("".join(json.dumps(l) + "\n" for l in lines))
print(f"{out}: {len(lines)} turns")
