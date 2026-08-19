# Retail Sales Performance Analysis

Exploratory data analysis of a 1,000-order retail sales dataset, covering revenue and profit performance by region, category, customer, and product — plus the impact of discounting on profitability and delivery timelines.

## Tools
Python, Pandas, NumPy, Matplotlib, Seaborn, Plotly (JupyterLab)

## Dataset
`retail_sales.csv` — 1,000 orders with order/ship dates, customer, segment, region, category, sub-category, product, sales, quantity, discount, and profit fields.

## Key Insights
- **Total Sales:** $509,262 | **Total Profit:** $23,876
- **Regional performance:** Sales are evenly spread across regions, with the South leading ($129.2K) narrowly ahead of the West, North, and East (all within ~$4K of each other).
- **Category mix:** Office Supplies is the top revenue category ($177.4K), followed closely by Furniture ($171.6K) and Technology ($160.3K).
- **Top customers:** Revenue is fairly distributed with no single dominant account — the top 5 customers each contribute roughly $4.8K–$5.4K, pointing toward an opportunity for a loyalty program to deepen high-value relationships.
- **Best-selling products:** Samsung Galaxy, Gaming Chair, and Metal Bookcase lead by units sold — useful signal for inventory prioritization.
- **Discount vs. profit:** A strong negative correlation (-0.85) between discount rate and profit — heavier discounting is eating directly into margins and should inform pricing strategy.
- **Fulfillment:** Average delivery time is ~3.9 days from order to shipment.

## Notebook
See [`Retail_Sales_Performance_Analysis.ipynb`](./Retail_Sales_Performance_Analysis.ipynb) for the full analysis, including regional and category breakdowns, top customer/product rankings, a discount-vs-profit regression, and the monthly sales trend.
