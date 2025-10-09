import os, sqlite3, pandas as pd
from dotenv import load_dotenv
import snowflake.connector
from snowflake.connector.pandas_tools import write_pandas

load_dotenv()

DB_PATH = os.getenv("SQLITE_DB", "winenot.db")

SF = dict(
    account=os.getenv("SF_ACCOUNT"),
    user=os.getenv("SF_USER"),
    password=os.getenv("SF_PASSWORD"),
    role=os.getenv("SF_ROLE","SYSADMIN"),
    warehouse=os.getenv("SF_WAREHOUSE","WINENOT_WH"),
    database=os.getenv("SF_DATABASE","WINENOT"),
    schema=os.getenv("SF_SCHEMA","STAGING")
)

RAW_MAP = {
    "products": "PRODUCTS_RAW",
    "consumers":"CONSUMERS_RAW",
    "orders":  "ORDERS_RAW"
}

def q(sql):
    with sqlite3.connect(DB_PATH) as conn:
        return pd.read_sql_query(sql, conn)

def sf_conn():
    return snowflake.connector.connect(**SF)

def safe_write(df, table):
    conn = sf_conn()
    try:
        ok, chunks, rows, _ = write_pandas(conn, df, table, auto_create_table=False)
        print(f"{table}: {rows} rows loaded.")
    finally:
        conn.close()

def main():
    products = q("SELECT * FROM products")
    consumers = q("SELECT * FROM consumers")
    orders    = q("SELECT * FROM orders")

    safe_write(products, RAW_MAP["products"])
    safe_write(consumers, RAW_MAP["consumers"])
    safe_write(orders,    RAW_MAP["orders"])

if __name__ == "__main__":
    main()
