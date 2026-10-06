#!/usr/bin/env bash
set -e
mkdir -p app && touch app/__init__.py
cat > app/users.py <<'P'
def find_duplicate_emails(users):
    """users: list of dicts with an "email" key, about 100,000 of them, from a signup form.
    Return the emails that belong to more than one user."""
    raise NotImplementedError
P
