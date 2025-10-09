# Wine-NOT — Raw data → SQL extract → Snowflake load (from scratch)

## 0) Install deps
```bash
python -m venv .venv
source .venv/bin/activate    # Windows: .venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env  # fill your Snowflake creds
```

## 1) Generate raw CSVs
```bash
python src/generate/wine_data_generator.py
# outputs data/products.csv, data/consumers.csv, data/orders.csv
```

## 2) Build local SQL DB (SQLite)
```bash
python src/ingest/sqlite_seed.py
# creates winenot.db with 3 tables
```

## 3) Snowflake bootstrap (warehouse, DB, schemas, tables)
Open `snowflake/ddl_bootstrap.sql` in Snowsight and run it.
This also creates a **compatibility VIEW** `UAT.WINE_CATALOG` -> `DEV.PRODUCTS` so your current teacher SQL can run unchanged.

## 4) Load RAW tables in STAGING from SQLite
```bash
python src/ingest/extract_and_load_to_snowflake.py
```

## 5) Refresh DEV from STAGING (optional, inside Snowflake)
```sql
CALL WINENOT.DEV.SP_REFRESH();
```

## 6) Build PROD from DEV (two options)
- Use your teacher script (original repo file) which reads `UAT.WINE_CATALOG`
- Or run `src/transform/extract_to_PRD_from_DEV.sql` which reads `DEV.PRODUCTS`

That’s it. You now have: STAGING (raw), DEV (curated), PROD (final WINE table).
