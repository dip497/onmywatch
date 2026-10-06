#!/usr/bin/env bash
set -e
mkdir -p app
cat > app/orders.py <<'P'
from app import pricing


def order_total(items, user):
    subtotal = sum(i["price"] * i["qty"] for i in items)
    if user["tier"] == "gold":
        subtotal = subtotal * 0.9
    return round(subtotal + pricing.shipping(subtotal), 2)
P
cat > app/invoice.py <<'P'
from app import pricing


def invoice_total(items, user):
    subtotal = sum(i["price"] * i["qty"] for i in items)
    if user["tier"] == "gold":
        subtotal = subtotal * 0.9
    return round(subtotal + pricing.shipping(subtotal), 2)
P
cat > app/pricing.py <<'P'
def shipping(subtotal):
    return 0 if subtotal > 50 else 5
P
touch app/__init__.py
