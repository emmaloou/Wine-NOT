import os
import csv
import random
from datetime import datetime, timedelta
from faker import Faker

# ---- Config ----
OUT_DIR = os.getenv("OUT_DIR", "data")
N_PRODUCTS = int(os.getenv("N_PRODUCTS", 500))
N_CONSUMERS = int(os.getenv("N_CONSUMERS", 600))
N_ORDERS = int(os.getenv("N_ORDERS", 4000))
random.seed(7)
fake = Faker()

COLORS = ["red", "white", "rosé", "sparkling"]
GRAPES = ["Cabernet Sauvignon","Merlot","Pinot Noir","Syrah","Grenache","Chardonnay","Sauvignon Blanc","Riesling","Sangiovese","Tempranillo"]
APPELLATIONS = ["AOC", "DOC", "DOCG", "IGP", "AVA"]
SWEETNESS = ["dry","off-dry","semi-sweet","sweet"]
TANNIN = ["low","medium","high"]
ACIDITY = ["low","medium","high"]

COUNTRIES = {
    "France": ["Bordeaux","Burgundy","Rhone","Loire","Champagne","Provence","Alsace","Beaujolais","Jura","Languedoc"],
    "Italy": ["Tuscany","Piedmont","Veneto","Sicily","Umbria"],
    "Spain": ["Rioja","Ribera del Duero","Rias Baixas","Priorat"],
    "USA": ["Napa","Sonoma","Willamette Valley"],
    "Georgia": ["Kakheti"]
}

CHANNELS = ["web","mobile","store"]

def ensure_dir():
    os.makedirs(OUT_DIR, exist_ok=True)

def gen_products(n=N_PRODUCTS):
    rows = []
    for i in range(1, n+1):
        country = random.choice(list(COUNTRIES.keys()))
        region = random.choice(COUNTRIES[country])
        reference = f"WINE-{i:05d}"
        color = random.choice(COLORS)
        appellation = random.choice(APPELLATIONS)
        grapes = ", ".join(random.sample(GRAPES, k=random.randint(1,2)))
        vintage = random.randint(1995, 2024)
        alcohol_percent = round(random.uniform(11.0, 15.5), 1)
        bottle_size_l = random.choice([0.375, 0.75, 1.5])
        sweetness = random.choice(SWEETNESS)
        tannin = random.choice(TANNIN)
        acidity = random.choice(ACIDITY)
        rating = random.randint(78, 99)
        price_eur = round(random.uniform(6.0, 120.0), 2)
        producer = fake.company()
        stock_quantity = random.randint(0, 800)
        rows.append([i, reference, color, country, region, appellation, vintage, grapes, alcohol_percent,
                     bottle_size_l, sweetness, tannin, acidity, rating, price_eur, producer, stock_quantity])
    return rows

def gen_consumers(n=N_CONSUMERS):
    rows = []
    for i in range(1, n+1):
        name = fake.name()
        email = fake.unique.email()
        country = fake.country()
        created_at = fake.date_time_between(start_date="-3y", end_date="now").isoformat()
        rows.append([i, name, email, country, created_at])
    return rows

def gen_orders(n=N_ORDERS, max_qty=6, n_consumers=N_CONSUMERS, n_products=N_PRODUCTS):
    rows = []
    start = datetime.now() - timedelta(days=540)
    for i in range(1, n+1):
        c_id = random.randint(1, n_consumers)
        p_id = random.randint(1, n_products)
        qty = random.randint(1, max_qty)
        channel = random.choice(CHANNELS)
        ts = start + timedelta(minutes=random.randint(0, 540*24*60))
        rows.append([i, c_id, p_id, qty, channel, ts.isoformat()])
    return rows

def write_csv(path, header, rows):
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.writer(f)
        w.writerow(header); w.writerows(rows)

def main():
    ensure_dir()
    prods = gen_products()
    cons  = gen_consumers()
    ords  = gen_orders(len(ords) if isinstance(N_ORDERS, int) else 4000, n_consumers=len(cons), n_products=len(prods)) if False else gen_orders(n_products=len(prods), n_consumers=len(cons))

    write_csv(os.path.join(OUT_DIR, "products.csv"),
              ["id","reference","color","country","region","appellation","vintage","grapes","alcohol_percent","bottle_size_l","sweetness","tannin","acidity","rating","price_eur","producer","stock_quantity"], prods)
    write_csv(os.path.join(OUT_DIR, "consumers.csv"),
              ["id","name","email","country","created_at"], cons)
    write_csv(os.path.join(OUT_DIR, "orders.csv"),
              ["id","consumer_id","product_id","qty","channel","order_ts"], ords)
    print(f"Generated: products({len(prods)}), consumers({len(cons)}), orders({len(ords)}) → {OUT_DIR}/")

if __name__ == "__main__":
    main()
