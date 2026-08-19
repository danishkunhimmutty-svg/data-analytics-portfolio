# Employee Salary Analysis
_Part of my [Data Analytics Portfolio](../)_

Exploratory analysis of San Francisco city employee salary records (2011–2014) using Pandas — pay trends over time, job title patterns, and outlier detection.

## Tools
Python, Pandas

## Dataset
`Salaries.csv` — 148,654 employee salary records with base pay, overtime pay, other pay, benefits, total pay, job title, year (2011–2014), and agency fields.

## Key Insights
- **Average base pay:** $66,325 across all records, with a clear upward trend from $63,596 (2011) to $69,630 (2013) before dipping slightly to $66,564 (2014).
- **Highest earner:** Nathaniel Ford, General Manager of the Metropolitan Transit Authority, with $567,595 in total pay & benefits — driven largely by a $400K "other pay" component.
- **Data quality flag:** The lowest total pay & benefits value is *negative* (-$618.13), indicating a data entry anomaly worth flagging or excluding in downstream analysis.
- **Job title diversity:** 2,159 unique job titles across the dataset; 202 titles were held by only one person in 2013 alone.
- **Leadership roles:** 627 employees hold a job title containing "chief."
- **Title length vs. pay:** Job title length shows essentially no correlation with total pay & benefits (r = -0.04), suggesting title verbosity isn't a meaningful pay signal.

## Notebook
See [`Employee_Salary_Analysis.ipynb`](./Employee_Salary_Analysis.ipynb) for the full analysis, including per-year base pay trends, top/bottom earner lookups, and job title pattern analysis.
