# Goal: Get notified when an established stock or index ETF drops 30%+

- **Status:** active
- **Started:** 2026-11-18
- **Target date:** none
- **Hands-on level:** agent does it

## Why
Spot big drawdowns in quality, market-established names (and the broad market
via QQQ and S&P 500 ETFs) as potential buying opportunities, without watching
charts every day.

## Success criteria
- [x] Tracker measures each ticker's drop from its 52-week high
- [x] Watchlist covers stable blue chips (Dividend Aristocrats, beta < 1, >$75B, plus BRK-B) and QQQ, SPY, VOO; editable
- [x] Threshold is configurable (default 30%)
- [x] Runs automatically on a schedule and notifies Jun

## Constraints
- Read-only: never places trades.
- No paid data or extra services required; ntfy push is optional.

## Plan
### Milestone 1: Build
- [x] `drop-tracker/tracker.py` + `watchlist.json` + tests
- [x] Notification step (GitHub issue per alert, optional ntfy)
- [x] Scheduled GitHub Action and README section
### Milestone 2: Go live
- [x] Jun merges the PR
- [x] Trigger "Drop tracker" once by hand from the Actions tab and check the run summary
- [ ] Optional: add `NTFY_TOPIC` secret for phone pushes

## Next step
None required. The tracker runs each weekday after the close. Optional: add the `NTFY_TOPIC` secret for phone pushes; review the stock list yearly.

## Decisions
- 2026-11-18: Measure the drop from the 52-week high (not purchase price or a single day's move).
- 2026-11-18: Track ETFs too: QQQ, SPY and VOO.
- 2026-11-18: Stocks must have a track record of stability: Dividend Aristocrat, beta < 1, market cap > $75B (BRK-B as exception). Dropped NVDA, META, GOOGL, AMZN, MSFT, AAPL, JPM, V, UNH, COST.
- 2026-11-18: Notify via GitHub issues (no secrets needed); ntfy as optional add-on.

## Progress log
- 2026-11-18: Goal created. Built tracker, workflow and README section. Snapshot
  with Robinhood closes from 2026-11-17: NVDA (-36.1%) and GOOGL (-31.4%) are past
  30%; QQQ is -13.9%, SPY/VOO -6.3%.

- 2026-11-18: Narrowed the watchlist to stable blue chips. Snapshot on 2026-11-17
  closes: nothing past 30%; closest are LOW (-24.8%), ABT (-20.7%), MCD (-19.3%), PEP (-17.2%).
- 2026-11-18: PR #1 merged. First live run (Actions run 44310905924) fetched all 17
  tickers; no alerts. Closest: LOW -24.8%, ABT -20.7%, MCD -19.3%.

## Lessons
