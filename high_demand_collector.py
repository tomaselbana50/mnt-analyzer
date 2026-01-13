import sqlite3
import requests
from bs4 import BeautifulSoup
import time

DB_PATH = "mnt_analyzer.db"

def calculate_demand_score(reviews, rating, recent_sales=1):
    return (reviews * 0.6) + (rating * 0.3) + (recent_sales * 0.1)

def fetch_amazon_category(category):
    # مثال مبسط، لاحقًا تستخدم Playwright أو Selenium
    url = f"https://www.amazon.eg/s?k={category}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    products = []

    # استخراج المنتجات
    for item in soup.select(".s-result-item"):
        try:
            name = item.select_one("h2").text.strip()
            link = "https://www.amazon.eg" + item.select_one("a.a-link-normal")["href"]
            reviews = int(item.select_one(".a-size-small").text.replace(",", "")) if item.select_one(".a-size-small") else 0
            rating = float(item.select_one(".a-icon-alt").text.split()[0]) if item.select_one(".a-icon-alt") else 0
            score = calculate_demand_score(reviews, rating)
            products.append((name, "Amazon", category, link, reviews, rating, score))
        except:
            continue

    return products

def save_high_demand(products):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for name, site, category, link, reviews, rating, score in products:
        c.execute("INSERT INTO products (name, site, category, product_url) VALUES (?, ?, ?, ?)",
                  (name, site, category, link))
        product_id = c.lastrowid
        c.execute("INSERT INTO demand_metrics (product_id, reviews_count, rating, demand_score) VALUES (?, ?, ?, ?)",
                  (product_id, reviews, rating, score))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    category = "electronics"  # مثال
    products = fetch_amazon_category(category)
    save_high_demand(products)
    print(f"{len(products)} high-demand products saved.")
