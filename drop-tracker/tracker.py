#!/usr/bin/env python3
"""Drop tracker: flags watchlist tickers trading 30%+ (configurable) below their
52-week (configurable) high. Standard library only.

Usage:
  python drop-tracker/tracker.py                      # print report
  python drop-tracker/tracker.py --json out.json      # also write machine-readable results
  python drop-tracker/tracker.py --threshold 20       # override threshold
"""
from __future__ import annotations

import argparse
import csv
import io
import json
import sys
import time
import urllib.request
from dataclasses import asdict, dataclass
from pathlib import Path

HERE = Path(__file__).resolve().parent
UA = {"User-Agent": "Mozilla/5.0 (drop-tracker)"}


@dataclass
class Result:
    ticker: str
    kind: str  # "stock" | "etf"
    price: float | None
    high: float | None
    drop_pct: float | None
    triggered: bool
    error: str | None = None


def _get(url: str, timeout: int = 20) -> bytes:
    req = urllib.request.Request(url, headers=UA)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read()


def fetch_yahoo(ticker: str, lookback_days: int) -> tuple[float, list[float]]:
    """Return (latest price, list of daily highs within lookback)."""
    period2 = int(time.time())
    period1 = period2 - lookback_days * 86400
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/{ticker}"
        f"?period1={period1}&period2={period2}&interval=1d"
    )
    data = json.loads(_get(url))
    res = data["chart"]["result"][0]
    highs = [h for h in res["indicators"]["quote"][0]["high"] if h is not None]
    price = res["meta"].get("regularMarketPrice")
    if price is None:
        closes = [c for c in res["indicators"]["quote"][0]["close"] if c is not None]
        price = closes[-1]
    return float(price), [float(h) for h in highs]


def fetch_stooq(ticker: str, lookback_days: int) -> tuple[float, list[float]]:
    sym = ticker.lower().replace("-", ".") + ".us"
    rows = list(csv.DictReader(io.StringIO(_get(f"https://stooq.com/q/d/l/?s={sym}&i=d").decode())))
    if not rows or "High" not in rows[0]:
        raise ValueError("no stooq data")
    rows = rows[-int(lookback_days * 252 / 365) :]  # trading days approx.
    return float(rows[-1]["Close"]), [float(r["High"]) for r in rows]


SOURCES = [fetch_yahoo, fetch_stooq]


def evaluate(ticker: str, kind: str, price: float, highs: list[float], threshold: float) -> Result:
    high = max(highs + [price])
    drop = (high - price) / high * 100 if high else 0.0
    return Result(ticker, kind, round(price, 2), round(high, 2), round(drop, 2), drop >= threshold)


def check(ticker: str, kind: str, threshold: float, lookback_days: int) -> Result:
    errors = []
    for src in SOURCES:
        try:
            price, highs = src(ticker, lookback_days)
            return evaluate(ticker, kind, price, highs, threshold)
        except Exception as e:  # try next source
            errors.append(f"{src.__name__}: {e}")
    return Result(ticker, kind, None, None, None, False, "; ".join(errors))


def load_config(path: Path) -> dict:
    cfg = json.loads(path.read_text())
    cfg.setdefault("threshold_pct", 30)
    cfg.setdefault("lookback_days", 365)
    cfg.setdefault("stocks", [])
    cfg.setdefault("etfs", [])
    return cfg


def render(results: list[Result], threshold: float, lookback_days: int) -> str:
    hits = [r for r in results if r.triggered]
    lines = [f"Drop tracker: {len(hits)} of {len(results)} tickers are {threshold:g}%+ below their {lookback_days}-day high", ""]
    lines.append("| Ticker | Type | Price | High | Drop | Alert |")
    lines.append("| --- | --- | ---: | ---: | ---: | :---: |")
    for r in sorted(results, key=lambda r: -(r.drop_pct or -1)):
        if r.error:
            lines.append(f"| {r.ticker} | {r.kind} | – | – | – | error |")
        else:
            lines.append(f"| {r.ticker} | {r.kind} | {r.price:,.2f} | {r.high:,.2f} | {r.drop_pct:.1f}% | {'🚨' if r.triggered else ''} |")
    errs = [r for r in results if r.error]
    if errs:
        lines += ["", "Errors:"] + [f"- {r.ticker}: {r.error}" for r in errs]
    return "\n".join(lines)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", type=Path, default=HERE / "watchlist.json")
    ap.add_argument("--threshold", type=float)
    ap.add_argument("--json", type=Path, help="write results JSON here")
    args = ap.parse_args(argv)

    cfg = load_config(args.config)
    threshold = args.threshold if args.threshold is not None else float(cfg["threshold_pct"])
    lookback = int(cfg["lookback_days"])
    tickers = [(t, "stock") for t in cfg["stocks"]] + [(t, "etf") for t in cfg["etfs"]]
    results = [check(t, k, threshold, lookback) for t, k in tickers]

    print(render(results, threshold, lookback))
    if args.json:
        args.json.write_text(json.dumps({
            "threshold_pct": threshold,
            "lookback_days": lookback,
            "results": [asdict(r) for r in results],
        }, indent=2))
    # Exit 2 if every ticker failed (data source down), so CI shows red.
    return 2 if results and all(r.error for r in results) else 0


if __name__ == "__main__":
    sys.exit(main())
