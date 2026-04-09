import csv
import io
import re
from datetime import datetime
from pathlib import Path

import requests
from pypdf import PdfReader

FOD_PDF_URL = "https://economie.fgov.be/sites/default/files/Files/Energy/prices/Officiele-Maximumtarieven-aardolieproducten.pdf"
CSV_PATH = Path("dataset.csv")

TARGETS = {
    "Benzine 95": r"Benzine\s+95\s+RON\s+E10\s+aan\s+de\s+pomp\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
    "Benzine 98": r"Benzine\s+98\s+RON\s+E5\s+aan\s+de\s+pomp\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
    "Diesel": r"Diesel\s+B7\s+aan\s+de\s+pomp\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
    "Stookolie (bestelling > 2.000 liter)": r"Gasolie\s+vanaf\s+2000\s+l\s+l\s+[0-9,().\-]+\s+21\s+([0-9]+(?:,[0-9]+)?)",
}

def fetch_pdf_text():
    response = requests.get(FOD_PDF_URL, timeout=60)
    response.raise_for_status()
    reader = PdfReader(io.BytesIO(response.content))
    text = "\n".join(page.extract_text() or "" for page in reader.pages)
    if not text.strip():
        raise RuntimeError("Geen tekst uit de PDF kunnen halen.")
    return text

def parse_effective_date(pdf_text):
    match = re.search(r"geldig\s+vanaf\s*:\s*(\d{2}/\d{2}/\d{4})", pdf_text, re.IGNORECASE)
    if not match:
        raise RuntimeError("Geen geldigheidsdatum gevonden in de FOD-PDF.")
    return datetime.strptime(match.group(1), "%d/%m/%Y").strftime("%Y-%m-%d")

def parse_prices(pdf_text):
    prices = {}
    for label, pattern in TARGETS.items():
        match = re.search(pattern, pdf_text, re.IGNORECASE)
        if not match:
            raise RuntimeError(f"Prijs voor {label} niet gevonden.")
        prices[label] = float(match.group(1).replace(",", "."))
    return prices

def read_existing_rows():
    if not CSV_PATH.exists():
        return []
    with CSV_PATH.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))

def write_rows(rows):
    fieldnames = ["date","Benzine 95","Benzine 98","Diesel","Stookolie (bestelling > 2.000 liter)"]
    with CSV_PATH.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        for row in sorted(rows, key=lambda r: r["date"]):
            writer.writerow(row)

def main():
    try:
        pdf_text = fetch_pdf_text()
        effective_date = parse_effective_date(pdf_text)
        prices = parse_prices(pdf_text)
        rows = {row["date"]: row for row in read_existing_rows()}
        rows[effective_date] = {"date": effective_date, **{k: f"{v:.3f}" for k, v in prices.items()}}
        write_rows(list(rows.values()))
        print("Bijgewerkt voor", effective_date)
    except Exception as e:
        print("Kon de officiële bron nu niet bereiken of verwerken.")
        print("Bestaande dataset.csv blijft behouden.")
        print("Fout:", e)

if __name__ == "__main__":
    main()
