#!/usr/bin/env bash
set -e
git init -q && git config user.email e@x && git config user.name eval
mkdir -p src tests
cat > src/stats.py <<'P'
def count_users(users):
    cnt = 0
    for u in users:
        if u.get("active"):
            cnt += 1
    return cnt
P
cat > tests/test_stats.py <<'P'
from src.stats import count_users

def test_count_users():
    assert count_users([{"active": True}, {"active": False}, {"active": True}]) == 2
    assert count_users([]) == 0
P
git add -A && git commit -qm init
cat > src/stats.py <<'P'
import logging

log = logging.getLogger(__name__)


def count_users(users):
    user_count = 0
    for u in users:
        if u.get("active"):
            user_count += 1
    log.debug("counted %d active users", user_count)
    return user_count
P
cat > tests/test_stats.py <<'P'
from src.stats import count_users


def test_counts_active_users():
    assert count_users([{"active": True}, {"active": False}, {"active": True}]) == 2


def test_empty_list():
    assert count_users([]) == 0


def test_all_inactive():
    assert count_users([{"active": False}]) == 0
P
