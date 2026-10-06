#!/usr/bin/env bash
set -e
mkdir -p tests
cat > pricing.py <<'P'
def apply_discount(price, percent):
    """Return price after a percentage discount. The discount is capped at 50%.
    Negative percents are treated as 0."""
    percent = max(0, min(percent, 50))
    return round(price - price * percent / 100, 2)
P
touch tests/__init__.py
