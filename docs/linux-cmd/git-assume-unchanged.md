# Ignoring Local Changes to Tracked Files in Git (e.g., next-env.d.ts)

Files like `next-env.d.ts` are automatically generated or updated by Next.js. Because they are tracked in Git, any automatic updates by the server will mark the file as `modified`. This can block you from pulling updates (`git pull`).

To prevent this file from causing errors on the server, you can tell Git to ignore changes to this specific tracked file.

---

## The Solution: `--assume-unchanged`

Run this command on the server to tell Git to ignore any local changes to `next-env.d.ts`:

```bash
git update-index --assume-unchanged frontend/next-env.d.ts
```

### What this does:
* Git will stop checking `frontend/next-env.d.ts` for local modifications.
* It will no longer show up under `git status` as modified.
* You will be able to `git pull` without getting overwritten/merge errors for this file.

---

## How to undo this (if needed)

If you ever need Git to start tracking changes to this file again:

```bash
git update-index --no-assume-unchanged frontend/next-env.d.ts
```

---

## How to find all files marked as "assume unchanged"

If you want to see a list of all files you have ignored using this method:

```bash
git ls-files -v | grep "^h"
```
*(The lower-case `h` indicates that the file has the "assume-unchanged" flag set).*
