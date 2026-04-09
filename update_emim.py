import csv
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

PAGE_URL = "https://live.euronext.com/en/product/etfs/IE00BKM4GZ66-XAMS"
CSV_PATH = Path("emim.csv")

def extract_price(page_html):
    patterns = [
        r'"lastPrice"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)',
        r'"price"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)',
        r'"instrCurrPrice"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)',
        r'"last"\s*:\s*"?([0-9]+(?:\.[0-9]+)?)',
    ]
    for pattern in patterns:
        m = re.search(pattern, page_html)
        if m:
            return float(m.group(1))
    m = re.search(r'IE00BKM4GZ66.*?([0-9]{2,3}\.\d{2,4})', page_html, re.DOTALL)
    if m:
        return float(m.group(1))
    raise RuntimeError("Geen koers gevonden op de Euronext-pagina.")

def read_existing():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_rows(rows):
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["date","price"])
        writer.writeheader()
        for row in sorted(rows, key=lambda r: r["date"]):
            writer.writerow(row)

def main():
    try:
        r = requests.get(PAGE_URL, headers={"User-Agent": "Mozilla/5.0"}, timeout=60)
        r.raise_for_status()
        price = extract_price(r.text)
        iso_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        rows = {row["date"]: row for row in read_existing()}
        rows[iso_date] = {"date": iso_date, "price": f"{price:.4f}"}
        write_rows(list(rows.values()))
        print("EMIM bijgewerkt:", iso_date, price)
    except Exception as e:
        print("EMIM kon niet bijgewerkt worden.")
        print("Bestaande emim.csv blijft behouden.")
        print("Fout:", e)

if __name__ == "__main__":
    main()
