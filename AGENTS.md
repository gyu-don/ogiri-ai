@CLAUDE.md

## Secrets and environment variables

The evaluation skills installed from
[humor-skills](https://github.com/gyu-don/humor-skills) call the TypeSafe AI
(Jev) API and need `TYPESAFE_API_KEY`. This repo's Doppler scope is already
configured, so:

- If the variable is **already in the environment**, run the command directly:
  `node .claude/skills/<name>/scripts/evaluate.ts <input.json>`
- If it is **not set**, prefix the command with `doppler run --`:
  `doppler run -- node .claude/skills/<name>/scripts/evaluate.ts <input.json>`

Check with `[ -n "$TYPESAFE_API_KEY" ]` rather than guessing; the scripts also
fail loudly with the fix (`TYPESAFE_API_KEY is missing. Run through Doppler: ...`).
When in doubt, `doppler run --` is safe — it is a no-op for commands that do not
read the variable.

Never print, log, or commit the key, and do not write it into a `.env` file.
