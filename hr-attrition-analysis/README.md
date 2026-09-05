# HR Employee Attrition Analysis

Exploratory data analysis and a predictive model investigating what drives employee
attrition in a 1,470-employee organization, with a written findings report and
retention recommendations.

## Overview

Employee turnover is costly for any organization. This project analyzes the
**IBM HR Analytics Employee Attrition & Performance** dataset (a fictional dataset
published by IBM data scientists) to identify which roles, conditions, and factors
are most strongly associated with employees leaving — and to turn those findings
into concrete, actionable retention recommendations.

## Key Findings

- **Overall attrition rate: 16.1%**
- **Sales Representatives** have the highest attrition of any role — **39.8%**,
  more than double the company average
- **Overtime is the strongest single driver**: employees working overtime leave at
  **30.5%** vs **10.4%** for those who don't
- Employees who left earned **~30% less** on average ($4,787 vs $6,833/month)
- Attrition risk is highest **early in tenure** (leavers average 5.1 years at the
  company vs 7.4 years for those who stay)
- Frequent business travel roughly **triples** attrition risk (24.9% vs 8.0%)

See the full [findings report](HR_Attrition_Analysis_Report.docx) for the complete
breakdown, charts, and recommendations.

## Predictive Model

A logistic regression model was trained on the full feature set and reached
**87.4% accuracy** on held-out test data. The strongest predictors of attrition
were overtime status, marital status, and department; the strongest protective
factors were stock option level, environment satisfaction, and job involvement.

## Tools Used

- **Python** (pandas, NumPy) — data cleaning and aggregation
- **Matplotlib / Seaborn** — visualization
- **Scikit-learn** — logistic regression model
- **Jupyter Notebook** — analysis environment

## Repository Contents

| File | Description |
|---|---|
| `WA_Fn-UseC_-HR-Employee-Attrition.csv` | Raw dataset (source: Kaggle) |
| `hr_attrition_analysis.ipynb` | Full analysis notebook — cleaning, EDA, visualizations, model |
| `HR_Attrition_Analysis_Report.docx` | Written findings & recommendations report |
| `charts/` | Exported chart images used in the report |

## Data Source

[IBM HR Analytics Employee Attrition & Performance](https://www.kaggle.com/datasets/pavansubhasht/ibm-hr-analytics-attrition-dataset) — Kaggle

## Author

**Danish Muhammed**
[LinkedIn](https://linkedin.com/in/danish-muhammed-657854412) · [GitHub](https://github.com/danishkunhimmutty-svg)
