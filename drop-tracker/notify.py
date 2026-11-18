#!/usr/bin/env python3
"""Turn tracker results into notifications.

Writes the alert title/body for the GitHub Action, which opens one issue per
triggered ticker (GitHub then emails / pushes it to you). Optionally also posts
to an ntfy.sh topic if NTFY_TOPIC is set.
"""
from __future__ import annotations

import json
import os
import sys
import urllib.request
from pathlib import Path


def alerts(results_path: Path) -> list[dict]:
    data = json.loads(results_path.read_text())
    out = []
    for r in data["results"]:
        if not r["triggered"]:
            continue
        out.append({
            "ticker": r["ticker"],
            "title": f"Drop alert: {r['ticker']} is down {r['drop_pct']:.1f}% from its {data['lookback_days']}-day high",
            "body": (
                f"**{r['ticker']}** ({r['kind']}) is trading at **${r['price']:,.2f}**, "
                f"{r['drop_pct']:.1f}% below its {data['lookback_days']}-day high of ${r['high']:,.2f}.\n\n"
                f"Threshold: {data['threshold_pct']:g}%.\n\n"
                "This is an automated alert, not financial advice. Close this issue once reviewed; "
                "a new one opens if the ticker triggers again after that."
            ),
        })
    return out


def send_ntfy(topic: str, a: dict) -> None:
    req = urllib.request.Request(
        f"https://ntfy.sh/{topic}", data=a["body"].replace("**", "").encode(),
        headers={"Title": a["title"], "Tags": "chart_with_downwards_trend"}, method="POST",
    )
    urllib.request.urlopen(req, timeout=15).read()


def main() -> int:
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "results.json")
    found = alerts(path)
    Path(os.environ.get("ALERTS_OUT", "alerts.json")).write_text(json.dumps(found, indent=2))
    topic = os.environ.get("NTFY_TOPIC")
    for a in found:
        print(a["title"])
        if topic:
            try:
                send_ntfy(topic, a)
            except Exception as e:
                print(f"ntfy failed for {a['ticker']}: {e}", file=sys.stderr)
    if not found:
        print("No alerts.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
