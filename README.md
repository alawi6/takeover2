# Takeover complete site

Upload alles uit deze zip naar de root van je GitHub repo.

Bestanden:
- index.html
- dataset.csv
- emim.csv
- update_prices.py
- update_emim.py
- requirements.txt
- .github/workflows/update-datasets.yml

Daarna:
1. Settings > Pages
2. Deploy from a branch
3. main + /root
4. Save
5. Actions > Run workflow

Deze v2 gebruikt Yahoo Finance chart-data voor EMIM.AS zodat historiek direct gevuld wordt.
