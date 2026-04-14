import pandas as pd
import sqlite3
import os

DB_PATH = "blinkit.db"
DATA_DIR = "data"

files = {
    "customer_feedback": "blinkit_customer_feedback.csv",
    "customers":         "blinkit_customers.csv",
    "delivery":          "blinkit_delivery_performance.csv",
    "inventory":         "blinkit_inventory.csv",
    "marketing":         "blinkit_marketing_performance.csv",
    "order_items":       "blinkit_order_items.csv",
    "orders":            "blinkit_orders.csv",
    "products":          "blinkit_products.csv",
}

conn = sqlite3.connect(DB_PATH)

for table, filename in files.items():
    filepath = os.path.join(DATA_DIR, filename)
    df = pd.read_csv(filepath)
    df.to_sql(table, conn, if_exists="replace", index=False)
    print(f"Loaded {table:25s} — {len(df):,} rows, {len(df.columns)} cols")

conn.close()
print("\nDone. Database saved as blinkit.db")