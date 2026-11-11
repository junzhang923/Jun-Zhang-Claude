# Goal Agent

An interactive agent, built on Claude Code, that helps you get a goal done. You
tell it what you want to achieve. It asks a few clarifying questions, makes a
plan, then works through it with you, doing tasks itself where it can and
coaching you where it can't. Progress is saved to a file, so you can stop and
pick up later from any session or device.

## How to use it

Open a Claude Code session on this repo and type:

| Command | What it does |
| --- | --- |
| `/goal` | Resume your active goal, or start a new one |
| `/goal launch a personal website by December` | Start a new goal |
| `/goal website` | Resume a specific goal |
| `/goal list` | Show all goals and their next steps |
| `/goal done website` | Check results and close a goal |

You can also just say what you want ("I want to save $5k by June") and the agent
will pick it up.

## How it works

- `.claude/skills/goal/SKILL.md`: the agent's instructions (clarify → plan →
  work loop → close-out, plus safety rules).
- `goals/_template.md`: the structure for each goal file.
- `goals/<slug>.md`: one file per goal, holding the success criteria, plan,
  next step, decisions and a dated progress log.

The agent can use any tool the session has: code, web search, files, and
connected services. It always asks before doing anything that is hard to undo
or reaches outside the repo, and it never places trades or moves money without
your explicit confirmation.
