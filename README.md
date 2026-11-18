# Friday

Friday is an interactive goal agent, built on Claude Code, that helps you get a goal done. You
tell it what you want to achieve. It asks a few clarifying questions, makes a
plan, then works through it with you, doing tasks itself where it can and
coaching you where it can't. Progress is saved to a file, so you can stop and
pick up later from any session or device.

## How to use it

Open a Claude Code session on this repo and type:

| Command | What it does |
| --- | --- |
| `/friday` | Resume your active goal, or start a new one |
| `/friday launch a personal website by December` | Start a new goal |
| `/friday website` | Resume a specific goal |
| `/friday list` | Show all goals and their next steps |
| `/friday done website` | Check results and close a goal |

You can also just say what you want ("I want to save $5k by June") and Friday
will pick it up.

## How it works

- `.claude/skills/friday/SKILL.md`: the agent's instructions (clarify → plan →
  work loop → close-out, plus safety rules).
- `goals/_template.md`: the structure for each goal file.
- `goals/<slug>.md`: one file per goal, holding the success criteria, plan,
  next step, decisions and a dated progress log.

The agent can use any tool the session has: code, web search, files, and
connected services. It always asks before doing anything that is hard to undo
or reaches outside the repo, and it never places trades or moves money without
your explicit confirmation.

## Drop tracker (stocks + ETFs)

A small tracker in `drop-tracker/` that watches stable, long-established stocks and index
ETFs and notifies you when one falls **30% or more below its 52-week high**.

- **Watchlist and threshold:** edit `drop-tracker/watchlist.json`. It holds
  `threshold_pct` (default 30), `lookback_days` (default 365, i.e. 52-week
  high), a `stocks` list and an `etfs` list (QQQ, plus SPY and VOO for the
  S&P 500). Use Yahoo-style tickers (`BRK-B`).
- **Which stocks, and why:** the default list is companies with a long record
  of being stable, so a 30% drop is unusual and worth a look. Each one meets
  all three of these:
  1. **Large and established:** market cap over $75B.
  2. **Steady through bad times:** 25+ consecutive years of dividend increases
     (an S&P 500 "Dividend Aristocrat"). Raising the payout every year through
     the 2000-02 crash, 2008-09 and 2020 takes steady earnings.
  3. **Lower volatility than the market:** beta under 1 when picked.

  That gives JNJ, PG, KO, PEP, WMT, MCD, ABT, CL, ADP, ITW, LOW, CB and SPGI,
  plus Berkshire Hathaway (BRK-B), which pays no dividend but has a 60-year
  low-volatility record. Fast-moving growth names (NVDA, META, etc.) and
  commodity-driven energy stocks are left out on purpose. Re-check the list
  once a year: a company that cuts its dividend should come off.
- **Schedule:** `.github/workflows/drop-tracker.yml` runs every weekday about
  30 minutes after the US close. You can also run it by hand from the Actions
  tab ("Drop tracker" → Run workflow), optionally with a different threshold.
- **Notifications:** for each ticker past the threshold, the workflow opens a
  GitHub issue labelled `drop-alert` and assigns it to you, so GitHub emails
  and pushes it to your phone. While that issue is open, the ticker won't
  re-alert; close it once you've reviewed it. For instant phone pushes, also
  add a repo secret `NTFY_TOPIC` with a private topic name and subscribe to it
  in the free [ntfy](https://ntfy.sh) app.
- **Report:** every run writes the full table (price, high, % drop) to the
  workflow run summary.
- **Run locally:** `python drop-tracker/tracker.py` (standard library only;
  prices come from Yahoo Finance with Stooq as fallback). Tests:
  `python -m unittest discover -s drop-tracker/tests`.

It only reads prices and sends alerts. It never places trades.
