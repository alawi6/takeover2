import csv
from datetime import datetime, timezone
from pathlib import Path

import requests

CSV_PATH = Path("emim.csv")
YAHOO_CHART_URL = "https://query1.finance.yahoo.com/v8/finance/chart/EMIM.AS?range=2y&interval=1d&includePrePost=false&events=div%2Csplits"

def read_existing():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_rows(rows):
    fieldnames = ["date", "price"]
    rows = sorted(rows, key=lambda r: r["date"])
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)

def fetch_history():
    r = requests.get(
        YAHOO_CHART_URL,
        headers={"User-Agent": "Mozilla/5.0"},
        timeout=60,
    )
    r.raise_for_status()
    data = r.json()

    result = data["chart"]["result"][0]
    timestamps = result.get("timestamp", [])
    quote = result["indicators"]["quote"][0]
    closes = quote.get("close", [])

    rows = []
    for ts, close in zip(timestamps, closes):
        if close is None:
            continue
        date = datetime.fromtimestamp(ts, tz=timezone.utc).strftime("%Y-%m-%d")
        rows.append({"date": date, "price": f"{float(close):.4f}"})
    return rows

def main():
    try:
        fetched_rows = fetch_history()
        if not fetched_rows:
            raise RuntimeError("Geen historische EMIM-data gevonden.")

        existing = {row["date"]: row for row in read_existing()}
        for row in fetched_rows:
            existing[row["date"]] = row

        write_rows(list(existing.values()))
        print(f"EMIM historiek bijgewerkt: {len(fetched_rows)} rijen")

    except Exception as e:
        print("EMIM kon niet bijgewerkt worden.")
        print("Bestaande emim.csv blijft behouden.")
        print("Fout:", e)

if __name__ == "__main__":
    main()
