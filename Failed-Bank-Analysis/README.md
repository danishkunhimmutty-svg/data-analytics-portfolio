# Failed Banks Analysis
_Part of my [Data Analytics Portfolio](../)_

Analysis of the FDIC's official failed bank list, scraped live from fdic.gov, covering failure trends by year, state, and acquiring institution.

## Tools
Python, Pandas, NumPy

## Dataset
Scraped directly from the [FDIC Failed Bank List](https://www.fdic.gov/bank-failures/failed-bank-list) using `pd.read_html()` — bank name, city, state, certificate number, acquiring institution, closing date, and fund number for each failed bank on record.

## Key Insights
- **25 bank failures** recorded, spanning **2017 to 2026**.
- **Peak failure year:** 2023, with 5 bank failures — more than any other year in the dataset.
- **Quietest years:** 2024 and 2025 each saw just 2 failures.
- **Average failures per year:** ~3.6, with a 3-year rolling average trending downward from a high of 4.3 (centered on 2023) to 2.7 by 2026.
- **State concentration:** Kansas and Illinois lead with 4 failures each, followed by Texas and California with 2 each — the rest of the affected states saw only 1 failure.
- **Acquisitions:** 24 different institutions acquired the 25 failed banks; United Fidelity Bank, fsb was the only acquirer to pick up more than one (2), with the remaining 23 institutions each acquiring one.
- **Data completeness:** No missing values across any of the 7 fields in the scraped dataset.

## Notebook
See [`Failed_Banks_Analysis.ipynb`](./Failed_Banks_Analysis.ipynb) for the full analysis, including a state × year pivot table and the rolling 3-year average of failures.

*Note: since this notebook scrapes live data from the FDIC site, re-running it will reflect the most current failed bank list rather than the figures above.*
