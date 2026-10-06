## User

Run the checks before we commit.

## Assistant

I ran `ruff check .`, then `mypy app`, then `pytest -q`, one by one. Ruff found 2 issues, which I fixed, then I ran all three again.

## User

We have `make check` for exactly this, it is in the Makefile. Why did you run them one by one?

## Assistant

You are right, `make check` runs ruff, mypy and pytest in one go. I ran it: all green.

## User

Ok, commit later. Also next time remember where the API keys live: `.env.local`, not `.env`.

## Assistant

Noted. The keys are read from `.env.local`.
