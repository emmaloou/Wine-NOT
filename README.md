# 🍷 Wine-NOT — Omnichannel Retail Data Platform

**Wine-NOT** is a simulated e-commerce and data warehousing project developed as part of the *ETL & Warehousing* course at **Albert School**.  
The project demonstrates an end-to-end modern data architecture: from raw data generation and ingestion to Snowflake transformation and analytics.

---

## 🧭 Project Overview

| Layer | Description | Technologies |
|--------|--------------|---------------|
| **Layer 1** | Data Generation — simulate raw customer, wine, and order data | Python, Faker, Docker |
| **Layer 2** | Ingestion & Streaming — batch and real-time data flows | Kafka (Redpanda), PostgreSQL |
| **Layer 3** | Warehousing & Transformation — clean, dedupe, enrich | Snowflake, SQL, dbt-core |
| **Layer 4** | Visualization & Monitoring — reporting & observability | Grafana, Looker Studio, Power BI |

---

## 🗂️ Repository Structure

```
Wine-NOT/
├─ data/                        # Generated raw data
│   ├─ wines.csv
│   ├─ customers.csv
│   ├─ orders_events.csv
│   └─ orders_events.jsonl
│
├─ src/
│   ├─ generate/                # Layer 1 – Data generation scripts
│   │   ├─ wine_data_generator.py
│   │   ├─ customer_generator.py
│   │   ├─ order_event_generator.py
│   │   └─ requirements.txt
│   │
│   ├─ ingest/                  # Layer 2 – Batch/stream ingestion (Kafka, DB)
│   └─ transform/               # Layer 3 – SQL transformation scripts
│
├─ snowflake/                   # Snowflake DDL & staging SQLs
│   └─ ddl_bootstrap.sql
│
├─ observability/               # Grafana dashboards (Layer 4)
│
├─ docker-compose.yml
├─ README.md
└─ .env.example
```

---

## 🧱 LAYER 1 — Data Generation

### 🎯 Objective
Produce realistic *“dirty”* datasets that mimic production data:
- 5% duplicate records
- Mixed price formats (€12.5, `12,50`, `12.50 EUR`)
- Mixed date formats (ISO, EU, US)

### 📜 Scripts

| Script | Output | Description |
|---------|---------|-------------|
| `wine_data_generator.py` | `data/wines.csv` | 500+ wine records (country, grape, price, stock, rating). |
| `customer_generator.py` | `data/customers.csv` | 150+ customers with multiple date formats. |
| `order_event_generator.py` | `data/orders_events.jsonl` / `.csv` | 60+ customer orders for streaming demo. |

### ▶️ Run Locally

```bash
# Local virtual env
cd src/generate
pip install -r requirements.txt
python wine_data_generator.py --out ../../data/wines.csv --n 500
python customer_generator.py --out ../../data/customers.csv --n 150
python order_event_generator.py --out ../../data/orders_events.jsonl --count 60
```

Or via Docker:
```bash
docker compose run --rm generator
```

✅ Output → `/data`  
Contains mixed formats and duplicates as required by the course rubric.

---

## ⚙️ LAYER 2 — Ingestion & Streaming

### 🎯 Objective
Simulate **data ingestion** in batch and streaming modes.

### 🧰 Components
| Tool | Purpose |
|------|----------|
| **Redpanda (Kafka)** | Streams real-time order events |
| **PostgreSQL** | Local raw data store |
| **Python Kafka producer** | Reads `orders_events.jsonl` and publishes events |

### ▶️ Run
```bash
docker compose up -d redpanda
python src/ingest/kafka_producer.py
```

(Optional consumer to monitor messages)
```bash
python src/ingest/kafka_consumer.py
```

✅ *Simulates orders flowing live into the warehouse.*

---

## 🧮 LAYER 3 — Data Warehousing & Transformation

### 🎯 Objective
Load, clean, and enrich data to make it analysis-ready.

### 🧱 Schemas

| Schema | Purpose |
|---------|----------|
| **RAW** | Original data from CSVs |
| **STAGING** | Parsed, cleaned, deduplicated data |
| **DEV** | Dimensional models (`DIM_WINE`, `DIM_CUSTOMER`, `FACT_ORDER`) |
| **PRD** | Business-ready datasets (classified & enriched) |

### 🧰 Setup

In **Snowsight (Snowflake Web UI)**:

1. Run `snowflake/ddl_bootstrap.sql`  
   → creates database `WINENOT` with schemas `RAW`, `STAGING`, `DEV`, `PRD`.

2. Upload CSVs from `data/` into RAW tables.

3. Run transformation SQLs (from README or DDL script):
   - Parse mixed formats (`TRY_TO_TIMESTAMP`, `REGEXP_REPLACE`)
   - Deduplicate (`ROW_NUMBER()` partitioned by ID)
   - Enrich final table (`region_classification`, `price_category`, `quality_tier`)

---

## 🍇 Business Classification Logic (PRD Layer)

| Dimension | Categories | Example |
|------------|-------------|----------|
| **Regional Classification** | Premium French, Prestige Spanish, Georgian Heritage, etc. | Bordeaux → “Premium French - Bordeaux” |
| **Price Classification** | Budget (<15 €), Mid-Range (15–30 €), Premium (30–50 €), Luxury (≥50 €) | 42 € → “Premium” |
| **Quality Classification** | Exceptional (≥95), Excellent (90–94), Very Good (85–89), Good (80–84), Average (<80) | Rating 91 → “Excellent” |

**SQL example (simplified):**
```sql
CREATE OR REPLACE TABLE WINENOT.PRD.WINES AS
SELECT *,
  CASE 
    WHEN region ILIKE 'Bordeaux' THEN 'Premium French - Bordeaux'
    WHEN region ILIKE 'Champagne' THEN 'Prestige French - Champagne'
    WHEN region IN ('Rioja','Ribera del Duero') THEN 'Premium Spanish'
    WHEN region ILIKE 'Kakheti' THEN 'Georgian Heritage'
    ELSE 'Other'
  END AS region_classification,
  CASE 
    WHEN price_eur < 15 THEN 'Budget'
    WHEN price_eur BETWEEN 15 AND 30 THEN 'Mid-Range'
    WHEN price_eur BETWEEN 30 AND 50 THEN 'Premium'
    ELSE 'Luxury'
  END AS price_category,
  CASE 
    WHEN rating >= 95 THEN 'Exceptional'
    WHEN rating >= 90 THEN 'Excellent'
    WHEN rating >= 85 THEN 'Very Good'
    WHEN rating >= 80 THEN 'Good'
    ELSE 'Average'
  END AS quality_tier
FROM WINENOT.DEV.DIM_WINE;
```

✅ Output: `WINENOT.PRD.WINES` — final enriched table.

---

## 📊 LAYER 4 — Visualization & Monitoring

### 🎯 Objective
Empower analytics, monitoring, and data observability.

| Tool | Purpose |
|------|----------|
| **Grafana** | ETL health & database metrics |
| **Looker Studio / Power BI** | Business dashboards (sales, stock, quality) |
| **Sifflet / Atlan (conceptual)** | Data governance, lineage & observability |

### Example Dashboards
- **Top Wines by Revenue**  
- **Stock Levels & Replenishment Rate**  
- **Orders Over Time (Kafka stream)**  
- **Average Price & Rating by Region**

---

## 🧩 Technologies Used

| Category | Tools |
|-----------|-------|
| **Data Generation** | Python, Faker |
| **Ingestion** | Kafka (Redpanda), PostgreSQL |
| **Warehouse** | Snowflake |
| **Transformation** | SQL, dbt-core |
| **Visualization** | Grafana, Looker Studio, Power BI |
| **Observability** | Sifflet, Atlan |

---

## 👩‍💻 Authors

**Team Data Wine-NOT**  
- Matthieu Dollfus
- Rayane Kryslak  
- Nolwenn Montillot
- Emma Lou Villaret  
- Hannah Zilezsch    

📅 *Version 1.1 — October 2025*  
📚 *ETL & Warehousing — Albert School*

---