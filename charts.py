import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np

conn = sqlite3.connect("blinkit.db")

# ── Data pulls ──────────────────────────────────────────────
revenue = pd.read_sql_query("""
    SELECT p.category,
           ROUND(SUM(oi.quantity * oi.unit_price), 2) AS total_revenue
    FROM order_items oi JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category ORDER BY total_revenue DESC
""", conn)

delay = pd.read_sql_query("""
    SELECT p.category,
           ROUND(100.0 * SUM(CASE WHEN o.delivery_status != 'On Time' THEN 1 ELSE 0 END) / COUNT(*), 2) AS delay_rate_pct
    FROM orders o
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category ORDER BY delay_rate_pct DESC
""", conn)

ratings = pd.read_sql_query("""
    SELECT p.category, ROUND(AVG(cf.rating), 2) AS avg_rating
    FROM customer_feedback cf
    JOIN orders o ON cf.order_id = o.order_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    GROUP BY p.category ORDER BY avg_rating ASC
""", conn)

pharmacy_delay_rating = pd.read_sql_query("""
    SELECT o.delivery_status,
           ROUND(AVG(cf.rating), 2) AS avg_rating,
           COUNT(*) AS count
    FROM orders o
    JOIN customer_feedback cf ON o.order_id = cf.order_id
    JOIN order_items oi ON o.order_id = oi.order_id
    JOIN products p ON oi.product_id = p.product_id
    WHERE p.category = 'Pharmacy'
    GROUP BY o.delivery_status
""", conn)

conn.close()

# ── Style ────────────────────────────────────────────────────
BLINKIT_GREEN = "#0C831F"
BLINKIT_YELLOW = "#F8C200"
BLINKIT_LIGHT = "#E8F5E9"
GRAY = "#B0BEC5"

plt.rcParams.update({
    "font.family": "sans-serif",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "grid.linestyle": "--"
})

fig, axes = plt.subplots(2, 2, figsize=(16, 12))
fig.suptitle("Blinkit Sales & Delivery Analysis", fontsize=18,
             fontweight="bold", color=BLINKIT_GREEN, y=1.01)

# ── Chart 1: Revenue by Category ────────────────────────────
ax1 = axes[0, 0]
colors1 = [BLINKIT_GREEN if i == 0 else GRAY for i in range(len(revenue))]
bars = ax1.barh(revenue["category"], revenue["total_revenue"] / 1000,
                color=colors1, edgecolor="white")
ax1.set_xlabel("Revenue (₹ Thousands)")
ax1.set_title("Revenue by Category", fontweight="bold")
ax1.invert_yaxis()
for bar, val in zip(bars, revenue["total_revenue"]):
    ax1.text(bar.get_width() + 5, bar.get_y() + bar.get_height() / 2,
             f"₹{val/1000:.0f}K", va="center", fontsize=8)

# ── Chart 2: Delay Rate by Category ─────────────────────────
ax2 = axes[0, 1]
colors2 = [BLINKIT_YELLOW if v > 33 else BLINKIT_GREEN for v in delay["delay_rate_pct"]]
bars2 = ax2.barh(delay["category"], delay["delay_rate_pct"],
                 color=colors2, edgecolor="white")
ax2.set_xlabel("Delay Rate (%)")
ax2.set_title("Delay Rate by Category", fontweight="bold")
ax2.invert_yaxis()
for bar, val in zip(bars2, delay["delay_rate_pct"]):
    ax2.text(bar.get_width() + 0.3, bar.get_y() + bar.get_height() / 2,
             f"{val}%", va="center", fontsize=8)
high_patch = mpatches.Patch(color=BLINKIT_YELLOW, label=">33% delay")
ax2.legend(handles=[high_patch], fontsize=8)

# ── Chart 3: Avg Rating by Category ─────────────────────────
ax3 = axes[1, 0]
colors3 = [BLINKIT_YELLOW if v < 3.3 else BLINKIT_GREEN for v in ratings["avg_rating"]]
bars3 = ax3.barh(ratings["category"], ratings["avg_rating"],
                 color=colors3, edgecolor="white")
ax3.set_xlabel("Average Rating (out of 5)")
ax3.set_title("Customer Rating by Category", fontweight="bold")
ax3.set_xlim(3.0, 3.6)
ax3.invert_yaxis()
for bar, val in zip(bars3, ratings["avg_rating"]):
    ax3.text(bar.get_width() + 0.005, bar.get_y() + bar.get_height() / 2,
             f"{val}", va="center", fontsize=8)
low_patch = mpatches.Patch(color=BLINKIT_YELLOW, label="Rating < 3.30")
ax3.legend(handles=[low_patch], fontsize=8)

# ── Chart 4: Pharmacy — Delay vs Rating ─────────────────────
ax4 = axes[1, 1]
status_order = ["On Time", "Slightly Delayed", "Significantly Delayed"]
pharm = pharmacy_delay_rating.set_index("delivery_status").reindex(status_order)
bar_colors = [BLINKIT_GREEN, BLINKIT_YELLOW, "#E53935"]
bars4 = ax4.bar(pharm.index, pharm["avg_rating"],
                color=bar_colors, edgecolor="white", width=0.5)
ax4.set_ylabel("Average Rating")
ax4.set_title("Pharmacy: Delivery Status vs Rating\n(Urgency Category — Delay Hurts Most)", fontweight="bold")
ax4.set_ylim(2.8, 3.6)
for bar, val in zip(bars4, pharm["avg_rating"]):
    ax4.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.01,
             f"{val}", ha="center", fontsize=9, fontweight="bold")

plt.tight_layout()
plt.savefig("blinkit_analysis.png", dpi=150, bbox_inches="tight")
print("Chart saved as blinkit_analysis.png")
plt.show()