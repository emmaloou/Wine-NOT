import os, sqlite3, csv

DB_PATH = os.getenv("SQLITE_DB", "winenot.db")
DATA_DIR = os.getenv("DATA_DIR", "data")

TABLES = {
    "products": {
        "schema": """
        CREATE TABLE IF NOT EXISTS products (
          id INTEGER PRIMARY KEY,
          reference TEXT,
          color TEXT,
          country TEXT,
          region TEXT,
          appellation TEXT,
          vintage INTEGER,
          grapes TEXT,
          alcohol_percent REAL,
          bottle_size_l REAL,
          sweetness TEXT,
          tannin TEXT,
          acidity TEXT,
          rating INTEGER,
          price_eur REAL,
          producer TEXT,
          stock_quantity INTEGER
        );""",
        "csv": "products.csv",
        "cols": ["id","reference","color","country","region","appellation","vintage","grapes","alcohol_percent","bottle_size_l","sweetness","tannin","acidity","rating","price_eur","producer","stock_quantity"]
    },
    "consumers": {
        "schema": """
        CREATE TABLE IF NOT EXISTS consumers (
          id INTEGER PRIMARY KEY,
          name TEXT,
          email TEXT,
          country TEXT,
          created_at TEXT
        );""",
        "csv": "consumers.csv",
        "cols": ["id","name","email","country","created_at"]
    },
    "orders": {
        "schema": """
        CREATE TABLE IF NOT EXISTS orders (
          id INTEGER PRIMARY KEY,
          consumer_id INTEGER,
          product_id INTEGER,
          qty INTEGER,
          channel TEXT,
          order_ts TEXT
        );""",
        "csv": "orders.csv",
        "cols": ["id","consumer_id","product_id","qty","channel","order_ts"]
    }
}

def load_csv(cur, table, csv_path, cols):
    if not os.path.exists(csv_path):
        raise SystemExit(f"Missing {csv_path}. Generate CSVs first.")
    cur.execute(f"DELETE FROM {table}")
    with open(csv_path, newline='', encoding='utf-8') as f:
        rdr = csv.DictReader(f)
        rows = [[row[c] for c in cols] for c,row in zip([cols]*10**9, rdr)]  # compact
    cur.executemany(f"INSERT INTO {table} ({','.join(cols)}) VALUES ({','.join(['?']*len(cols))})", rows)

def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    conn = sqlite3.connect(DB_PATH); cur = conn.cursor()
    for t,meta in TABLES.items():
        cur.execute(meta["schema"]); conn.commit()
        load_csv(cur, t, os.path.join(DATA_DIR, meta["csv"]), meta["cols"]); conn.commit()
        print(f"Loaded {t}.")
    cur.close(); conn.close()
    print(f"SQLite ready at {DB_PATH}.")
if __name__ == "__main__":
    main()
