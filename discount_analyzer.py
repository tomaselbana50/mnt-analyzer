import sqlite3
import requests
from bs4 import BeautifulSoup

DB_PATH = "mnt_analyzer.db"

GLOBAL_AVERAGE = {
    "wireless mouse": 2250,  # مثال، يمكن جلب البيانات عالمياً لاحقاً
}

def fetch_discounts_amazon(category):
    url = f"https://www.amazon.eg/s?k={category}"
    headers = {"User-Agent": "Mozilla/5.0"}
    r = requests.get(url, headers=headers)
    soup = BeautifulSoup(r.text, "html.parser")
    discounts = []

    for item in soup.select(".s-result-item"):
        try:
            name = item.select_one("h2").text.strip()
            link = "https://www.amazon.eg" + item.select_one("a.a-link-normal")["href"]
            old_price_text = item.select_one(".a-price-whole")  # مثال
            new_price_text = item.select_one(".a-price .a-offscreen")
            if old_price_text and new_price_text:
                old_price = float(old_price_text.text.replace("٬",""))
                new_price = float(new_price_text.text.replace("٬",""))
                discount = round(((old_price - new_price) / old_price) * 100, 2)
                # Check discount validity
                if new_price < GLOBAL_AVERAGE.get(name.lower(), new_price):
                    discounts.append((name, "Amazon", category, link, old_price, new_price, discount))
        except:
            continue

    return discounts

def save_valid_discounts(discounts):
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    for name, site, category, link, old_price, new_price, discount in discounts:
        c.execute("INSERT INTO products (name, site, category, product_url) VALUES (?, ?, ?, ?)",
                  (name, site, category, link))
        product_id = c.lastrowid
        c.execute("INSERT INTO price_history (product_id, old_price, new_price, discount_percentage) VALUES (?, ?, ?, ?)",
                  (product_id, old_price, new_price, discount))
        c.execute("INSERT INTO validated_discounts (product_id, discount_percentage, verified) VALUES (?, ?, 1)",
                  (product_id, discount))
    conn.commit()
    conn.close()

if __name__ == "__main__":
    category = "electronics"
    discounts = fetch_discounts_amazon(category)
    save_valid_discounts(discounts)
    print(f"{len(discounts)} validated discounts saved.")
