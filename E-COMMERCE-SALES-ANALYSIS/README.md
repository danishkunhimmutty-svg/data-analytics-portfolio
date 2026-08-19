# Ecommerce Purchases Analysis
_Part of my [Data Analytics Portfolio](../)_

Exploratory analysis of 10,000 ecommerce transaction records — customer purchasing behavior, payment methods, browsing patterns, and targeted record lookups using Pandas.

## Tools
Python, Pandas

## Dataset
`Ecommerce_Purchases.csv` — 10,000 transactions with customer address, purchase timing (AM/PM), browser info, company, credit card details, job title, IP address, language, and purchase price fields.

## Key Insights
- **Average purchase price:** $50.35, ranging from $0.00 to $99.99 across the dataset.
- **Language:** 1,098 purchases (11%) were made by users with English ('en') set as their browser language.
- **Job titles:** No single profession dominates — "Interior and spatial designer" (31), "Lawyer" (30), and "Social researcher" (28) are the most common, out of a highly varied job list.
- **Purchase timing:** Transactions are nearly evenly split between AM (4,932) and PM (5,068).
- **Payment methods:** 39 purchases were made with an American Express card for more than $95 — useful for identifying high-value premium-card customers.
- **Card expirations:** 1,033 credit cards (10.3%) expire in 2025, relevant for flagging accounts needing updated payment info.
- **Email providers:** Hotmail (1,638), Yahoo (1,616), and Gmail (1,605) are the top three domains, with free webmail providers dominating over custom/company domains.

## Notebook
See [`Ecommerce_Purchases_Analysis.ipynb`](./Ecommerce_Purchases_Analysis.ipynb) for the full analysis, including targeted lookups (e.g. finding a customer's email from their credit card number, or purchase price by lot number).
