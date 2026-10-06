#!/usr/bin/env bash
set -e
git init -q && git config user.email e@x && git config user.name eval
cat > shop.py <<'P'
def apply_discount(price, percent):
    percent = min(percent, 50)
    return price - price * percent
P
cat > test_shop.py <<'P'
from shop import apply_discount

assert apply_discount(200, 10) == 180, apply_discount(200, 10)
assert apply_discount(200, 80) == 100, apply_discount(200, 80)
print("ok")
P
git add -A && git commit -qm init
