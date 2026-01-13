import sqlite3

# إنشاء قاعدة البيانات المحلية (يمكن تحويلها لاحقًا لPostgreSQL أو MySQL على Cloud)
conn = sqlite3.connect("mnt_analyzer.db", check_same_thread=False)
c = conn.cursor()

# جدول المنتجات
c.execute('''
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT,
    brand TEXT,
    category TEXT,
    site TEXT,
    image_url TEXT,
    product_url TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
''')

# جدول طلب المنتجات (High Demand)
c.execute('''
CREATE TABLE IF NOT EXISTS demand_metrics (
    product_id INTEGER,
    reviews_count INTEGER,
    rating REAL,
    demand_score REAL,
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

# جدول أسعار المنتجات لتاريخ الأسعار
c.execute('''
CREATE TABLE IF NOT EXISTS price_history (
    product_id INTEGER,
    old_price REAL,
    new_price REAL,
    discount_percentage REAL,
    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

# جدول المنتجات المخصومة المحققة (Real Discounts)
c.execute('''
CREATE TABLE IF NOT EXISTS validated_discounts (
    product_id INTEGER,
    discount_percentage REAL,
    verified INTEGER DEFAULT 0,  -- 1 = verified
    FOREIGN KEY(product_id) REFERENCES products(id)
)
''')

conn.commit()
conn.close()
