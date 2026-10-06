## User

The login page shows a blank screen after I log in.

## Assistant

The redirect URL was missing a slash. I fixed it in `auth/redirect.ts`.

## User

Still broken.

## Assistant

The session cookie was set without a path, so I added `path=/` in `auth/session.ts`.

## User

Still broken.

## Assistant

I changed the redirect to use `router.replace` instead of `window.location` in `auth/redirect.ts`.
