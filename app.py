import streamlit as st
import sqlite3
import db   # 👈 السطر الجديد المهم

DB_PATH = "mnt_analyzer.db"

st.set_page_config(page_title="MNT Analyzer", layout="wide")

tabs = st.tabs(["High Demand", "Real Discounts"])

conn = sqlite3.connect(DB_PATH)
c = conn.cursor()

# --- High Demand Tab ---
with tabs[0]:
    st.header("High Demand Products")
    c.execute('''
        SELECT p.name, p.site, p.category, p.product_url, d.reviews_count, d.rating, d.demand_score
        FROM products p
        JOIN demand_metrics d ON p.id = d.product_id
        ORDER BY d.demand_score DESC
        LIMIT 50
    ''')
    products = c.fetchall()
    for prod in products:
        st.write(f"[{prod[0]}]({prod[3]}) | {prod[1]} | Category: {prod[2]} | Reviews: {prod[4]} | Rating: {prod[5]} | Score: {prod[6]}")

# --- Real Discounts Tab ---
with tabs[1]:
    st.header("Real Discounts")
    c.execute('''
        SELECT p.name, p.site, p.category, p.product_url, ph.old_price, ph.new_price, ph.discount_percentage
        FROM products p
        JOIN validated_discounts vd ON p.id = vd.product_id
        JOIN price_history ph ON p.id = ph.product_id
        WHERE vd.verified = 1
        ORDER BY ph.discount_percentage DESC
        LIMIT 50
    ''')
    discounts = c.fetchall()
    for d in discounts:
        st.write(f"[{d[0]}]({d[3]}) | {d[1]} | Category: {d[2]} | Old: {d[4]} | New: {d[5]} | Discount: {d[6]}%")