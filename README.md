# Stock Tracker — Inventory Management & Big Data Analytics

A modern, aesthetic inventory analytics dashboard built with Python, Streamlit, Pandas, and Plotly.

## Features
- Premium dark navy and teal themed interface
- Overview cards for products, stock units, inventory value, and sales revenue
- Product catalogue with search and category/status filters
- Stock health monitoring: healthy, low stock, and out of stock
- Sales analytics with interactive charts
- CSV upload directly from the sidebar or Data Center page, with column normalization and basic data validation
- Business insights and replenishment alerts
- Downloadable processed inventory data
- Includes a synthetic sample dataset with 120 product records

## Run the project

### 1. Extract the ZIP and open the project folder

```bash
cd stock_tracker
```

### 2. Create a virtual environment (recommended)

Ubuntu / macOS:
```bash
python3 -m venv venv
source venv/bin/activate
```

Windows:
```powershell
python -m venv venv
venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Start the dashboard

```bash
streamlit run app.py
```

Open the local URL shown in the terminal (usually `http://localhost:8501`).

## CSV format

Required columns:
- `Product_ID`
- `Product_Name`
- `Category`
- `Quantity`
- `Unit_Price`
- `Units_Sold`

Optional columns:
- `Reorder_Level`
- `Supplier`
- `Last_Updated`

A sample CSV is included in `data/sample_inventory.csv`.

## Big Data extension

This starter dashboard currently performs interactive local data analysis using Pandas. For a full distributed Big Data implementation, integrate PySpark for large-scale transformations and Hadoop HDFS or a database for distributed storage. The current ZIP does not claim to run Spark or Hadoop yet.

## Project structure

```text
stock_tracker/
├── app.py
├── requirements.txt
├── README.md
├── PROJECT_OVERVIEW.txt
└── data/
    └── sample_inventory.csv
```

## Data notes

The included sample data is synthetic and for demonstration only.
- Inventory value = Quantity × Unit_Price
- Revenue = Units_Sold × Unit_Price
- Stock status is calculated from Quantity and Reorder_Level
