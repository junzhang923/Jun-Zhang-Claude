# Jun-Zhang-Claude

This repo is home to **Friday**, a goal agent: an interactive assistant that helps take
a goal from idea to done across sessions.

- Friday's behavior lives in `.claude/skills/friday/SKILL.md` (run it with `/friday`).
- Each goal is tracked in its own file, `goals/<slug>.md`, created from
  `goals/_template.md`. That file is the source of truth for status, plan and
  progress.

## Working in this repo

- When the user states something they want to achieve, or asks "where was I?",
  use the `friday` skill.
- At the start of a session with no specific request, check `goals/` for goals
  with `Status: active` and offer to resume one.
- After meaningful progress on a goal, update its file, then commit and push to
  the current branch so progress survives the session.
- Ask before any action that is hard to undo or reaches outside this repo
  (sending, posting, buying, trading, deleting, sharing).
