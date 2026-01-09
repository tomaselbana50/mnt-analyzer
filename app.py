import requests
from bs4 import BeautifulSoup
import pandas as pd
import streamlit as st
import json

# تحميل إعدادات المشروع من config.json
with open("config.json", encoding="utf-8-sig") as f:
    config = json.load(f)


email_user = config["email"]
global_price_ref = config["global_price_reference"]

# -------------------------------
# الفئات والمواقع
# -------------------------------
sites = {
    "Amazon": ["Electronics", "Home & Kitchen", "Health & Household Products", "Beauty", "Tools & Home Improvement"],
    "Noon": ["Electronics", "Health & Nutrition", "Kitchen & Dining", "Small Appliances", "Large Appliances", "Beauty & Fragrance", "Office Electronics", "Skates, Skateboarding & Scooters"],
    "Jumia": ["Phones & Tablets", "Health & Beauty", "Kitchen & Dining", "Appliances", "Televisions & Audio", "Computing", "Gaming", "Electronics"]
}

# -------------------------------
# دوال الـ Scraping
# -------------------------------
def scrape_amazon(category):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.amazon.eg/s?k={category.replace(' ', '+')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    for item in soup.select(".s-result-item"):
        title_tag = item.select_one("h2 a span")
        price_tag = item.select_one(".a-price .a-offscreen")
        old_price_tag = item.select_one(".a-price.a-text-price .a-offscreen")
        rating_tag = item.select_one(".a-icon-alt")
        review_tag = item.select_one(".a-size-base")

        if title_tag and price_tag:
            title = title_tag.text.strip()
            price = float(price_tag.text.replace("EGP", "").replace(",", "").strip())
            old_price = None
            if old_price_tag:
                try:
                    old_price = float(old_price_tag.text.replace("EGP", "").replace(",", "").strip())
                except:
                    old_price = None
            rating = rating_tag.text.strip() if rating_tag else "No Rating"
            reviews = int(review_tag.text.replace(",", "").strip()) if review_tag and review_tag.text.strip().isdigit() else 0

            products.append({
                "Site": "Amazon",
                "Category": category,
                "Title": title,
                "Price": price,
                "Old Price": old_price,
                "Rating": rating,
                "Reviews": reviews,
                "Brand": ""
            })
    return products

def scrape_noon(category):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.noon.com/egypt-en/{category.replace(' ','-')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    for item in soup.select(".productContainer"):
        title_tag = item.select_one(".productTitle")
        price_tag = item.select_one(".finalPrice")
        old_price_tag = item.select_one(".wasPrice")
        brand_tag = item.select_one(".brandName")

        if title_tag and price_tag:
            title = title_tag.text.strip()
            try:
                price = float(price_tag.text.replace("EGP", "").replace(",", "").strip())
            except:
                continue
            old_price = None
            if old_price_tag:
                try:
                    old_price = float(old_price_tag.text.replace("EGP", "").replace(",", "").strip())
                except:
                    old_price = None
            brand = brand_tag.text.strip() if brand_tag else ""
            products.append({
                "Site": "Noon",
                "Category": category,
                "Title": title,
                "Price": price,
                "Old Price": old_price,
                "Rating": "N/A",
                "Reviews": 0,
                "Brand": brand
            })
    return products

def scrape_jumia(category):
    headers = {"User-Agent": "Mozilla/5.0"}
    url = f"https://www.jumia.com.eg/catalog/?q={category.replace(' ','+')}"
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    products = []
    for item in soup.select(".core"):
        title_tag = item.select_one(".name")
        price_tag = item.select_one(".prc")
        old_price_tag = item.select_one(".old")
        brand_tag = item.select_one(".brand")

        if title_tag and price_tag:
            title = title_tag.text.strip()
            try:
                price = float(price_tag.text.replace("EGP", "").replace(",", "").strip())
            except:
                continue
            old_price = None
            if old_price_tag:
                try:
                    old_price = float(old_price_tag.text.replace("EGP", "").replace(",", "").strip())
                except:
                    old_price = None
            brand = brand_tag.text.strip() if brand_tag else ""
            products.append({
                "Site": "Jumia",
                "Category": category,
                "Title": title,
                "Price": price,
                "Old Price": old_price,
                "Rating": "N/A",
                "Reviews": 0,
                "Brand": brand
            })
    return products

# -------------------------------
# دمج كل المواقع في دالة واحدة
# -------------------------------
def scrape_all(site, category):
    if site == "Amazon":
        return scrape_amazon(category)
    elif site == "Noon":
        return scrape_noon(category)
    elif site == "Jumia":
        return scrape_jumia(category)
    else:
        return []

# -------------------------------
# تحليل المنتجات
# -------------------------------
def analyze_products(df, global_price):
    df['Discount %'] = df.apply(lambda x: round((x['Old Price'] - x['Price'])/x['Old Price']*100, 2) if x['Old Price'] else None, axis=1)
    df['Demand'] = df['Reviews'].apply(lambda x: 'High' if x>50 else ('Medium' if x>10 else 'Low'))
    df['Price vs Global'] = df['Price'].apply(lambda x: 'Below Global Avg' if x < global_price else 'Above Global Avg')
    df['Classification'] = df.apply(
        lambda x: "Opportunity" if x['Discount %'] and x['Discount %']>40 and x['Price vs Global']=="Below Global Avg" else
        ("Watchlist" if x['Discount %'] and x['Discount %']>10 else "Fake Discount"), axis=1)
    return df

# -------------------------------
# واجهة Streamlit
# -------------------------------
st.set_page_config(page_title="MNT Analyzer", layout="wide")
st.title("📊 MNT Price Tracker & Demand Analyzer")

col1, col2, col3, col4 = st.columns(4)
with col1:
    site_filter = st.selectbox("🛒 الموقع", list(sites.keys()))
with col2:
    category_filter = st.selectbox("📂 الفئة", sites[site_filter])
with col3:
    min_price = st.number_input("من سعر (EGP)", value=0)
with col4:
    max_price = st.number_input("إلى سعر (EGP)", value=10000)

brand_filter = st.text_input("🔎 البراند (اختياري)", "")

if st.button("ابدأ التحليل 🚀"):
    with st.spinner("جارٍ جمع وتحليل المنتجات..."):
        products = scrape_all(site_filter, category_filter)
        if not products:
            st.warning("⚠️ لم يتم العثور على منتجات.")
        else:
            df = pd.DataFrame(products)
            if brand_filter:
                df = df[df['Title'].str.contains(brand_filter, case=False, na=False) | df['Brand'].str.contains(brand_filter, case=False, na=False)]
            df = df[(df['Price']>=min_price) & (df['Price']<=max_price)]
            df = analyze_products(df, global_price_ref)

            st.success(f"✅ تم العثور على {len(df)} منتج")
            st.dataframe(df, use_container_width=True)
            st.download_button("📥 تحميل النتائج كـ CSV", df.to_csv(index=False).encode('utf-8'), "products.csv", "text/csv")

st.caption("© 2026 MNT Analyzer — Developed for Thomas Nashaat")
