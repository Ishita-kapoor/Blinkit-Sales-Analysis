import pandas as pd
import sqlite3

conn = sqlite3.connect("blinkit.db")

# Q1: Revenue by product category
q1 = """
SELECT p.category,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue,
       COUNT(DISTINCT oi.order_id) AS total_orders
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY total_revenue DESC
"""

# Q2: Late delivery rate by category (fixed)
q2 = """
SELECT p.category,
       COUNT(*) AS total_orders,
       SUM(CASE WHEN o.delivery_status != 'On Time' THEN 1 ELSE 0 END) AS delayed_orders,
       ROUND(100.0 * SUM(CASE WHEN o.delivery_status != 'On Time' THEN 1 ELSE 0 END) / COUNT(*), 2) AS delay_rate_pct
FROM orders o
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY delay_rate_pct DESC
"""

# Q3: Average customer rating by category
q3 = """
SELECT p.category,
       ROUND(AVG(cf.rating), 2) AS avg_rating,
       COUNT(cf.feedback_id) AS review_count
FROM customer_feedback cf
JOIN orders o ON cf.order_id = o.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category
ORDER BY avg_rating ASC
"""

# Q4: Does late delivery hurt ratings?
q4 = """
SELECT o.delivery_status,
       ROUND(AVG(cf.rating), 2) AS avg_rating,
       COUNT(*) AS total_reviews
FROM orders o
JOIN customer_feedback cf ON o.order_id = cf.order_id
GROUP BY o.delivery_status
"""

# Q5: Top 10 products by revenue
q5 = """
SELECT p.product_name,
       p.category,
       ROUND(SUM(oi.quantity * oi.unit_price), 2) AS revenue
FROM order_items oi
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.product_id
ORDER BY revenue DESC
LIMIT 10
"""
# Q6: Rating breakdown by delivery status AND category
q6 = """
SELECT p.category,
       o.delivery_status,
       ROUND(AVG(cf.rating), 2) AS avg_rating,
       COUNT(*) AS count
FROM orders o
JOIN customer_feedback cf ON o.order_id = cf.order_id
JOIN order_items oi ON o.order_id = oi.order_id
JOIN products p ON oi.product_id = p.product_id
GROUP BY p.category, o.delivery_status
ORDER BY p.category, o.delivery_status
"""

queries = {"Q1 Revenue by Category": q1,
           "Q2 Delay Rate by Category": q2,
           "Q3 Avg Rating by Category": q3,
           "Q4 Delivery Status vs Rating": q4,
           "Q5 Top 10 Products by Revenue": q5,
           "Q6 Rating by Category + Delivery Status": q6}

for name, query in queries.items():
    print(f"\n{'='*50}")
    print(f"{name}")
    print('='*50)
    df = pd.read_sql_query(query, conn)
    print(df.to_string(index=False))

conn.close()