# WineNot - Wine Catalog Data Classification

## Project Context

**WineNot** is a company specializing in the distribution of quality wines from different European and Georgian wine regions. 

Our catalog database includes 500 wine references with detailed information (region, grape variety, vintage, tasting notes, price, stock). To improve our business strategy and facilitate inventory analysis, we restructured our catalog by creating an enriched table with business classifications.

## Objective

Create a production table (`WINENOT.PRD.MERGE`) from our raw catalog (`WINENOT.UAT.WINE_CATALOG`) by adding three classification dimensions :

1. **Regional Classification**: Categorization of wines by prestige and geographic origin
2. **Price Classification** : Segmentation into 4 price ranges
3. **Quality Classification**: Evaluation based on critical ratings

## Data Architecture

```
WINENOT (Database)
├── UAT (Schema)
│   └── WINE_CATALOG (Source table - 500 wines)
└── PRD (Schema)
    └── WINES (Enriched table with classifications)
```

## 📊 Classification Structure

### Regional Classification
| Category | Regions |
|-----------|---------|
| **Premium French - Rhone Valley** | Rhone |
| **Premium French - Bordeaux** | Bordeaux |
| **Premium French - Burgundy** | Burgundy |
| **Prestige French - Champagne** | Champagne |
| **Regional French** | Loire, Alsace, Provence, Jura, Beaujolais, Languedoc |
| **Premium Spanish - Rioja** | Rioja |
| **Premium Spanish - Ribera** | Ribera del Duero |
| **Regional Spanish - Atlantic** | Rias Baixas |
| **Premium Italian - North** | Tuscany, Piedmont |
| **Regional Italian** | Sicily, Veneto |
| **Georgian Heritage** | Kakheti |

### Price Classification
- **Budget** : < 15€
- **Mid-Range** : 15-30€
- **Premium** : 30-50€
- **Luxury** : ≥ 50€

### Quality Classification
- **Exceptional** : rating ≥ 95
- **Excellent** : rating 90-94
- **Very Good** : rating 85-89
- **Good** : rating 80-84
- **Average** : rating < 80

## 🔧 Transformation SQL Script

### 1. Creation of the enriched table

```sql
CREATE OR REPLACE TABLE WINENOT.PRD.WINES AS
SELECT 
    -- Original columns
    id,
    reference,
    color,
    country,
    region,
    appellation,
    vintage,
    grapes,
    alcohol_percent,
    bottle_size_l,
    sweetness,
    tannin,
    acidity,
    rating,
    price_eur,
    producer,
    stock_quantity,
    
    -- REGIONAL CLASSIFICATION
    CASE 
        WHEN region = 'Rhone' THEN 'Premium French - Rhone Valley'
        WHEN region = 'Bordeaux' THEN 'Premium French - Bordeaux'
        WHEN region = 'Burgundy' THEN 'Premium French - Burgundy'
        WHEN region = 'Champagne' THEN 'Prestige French - Champagne'
        WHEN region IN ('Loire', 'Alsace', 'Provence', 'Jura', 'Beaujolais', 'Languedoc') 
            THEN 'Regional French'
        WHEN region = 'Rioja' THEN 'Premium Spanish - Rioja'
        WHEN region = 'Ribera del Duero' THEN 'Premium Spanish - Ribera'
        WHEN region = 'Rias Baixas' THEN 'Regional Spanish - Atlantic'
        WHEN region IN ('Tuscany', 'Piedmont') THEN 'Premium Italian - North'
        WHEN region IN ('Sicily', 'Veneto') THEN 'Regional Italian'
        WHEN region = 'Kakheti' THEN 'Georgian Heritage'
        ELSE 'Other'
    END AS region_classification,
    
    -- PRICE CLASSIFICATION
    CASE 
        WHEN price_eur < 15 THEN 'Budget'
        WHEN price_eur BETWEEN 15 AND 30 THEN 'Mid-Range'
        WHEN price_eur BETWEEN 30 AND 50 THEN 'Premium'
        WHEN price_eur >= 50 THEN 'Luxury'
    END AS price_category,
    
    -- QUALITY CLASSIFICATION
    CASE 
        WHEN rating >= 95 THEN 'Exceptional'
        WHEN rating >= 90 THEN 'Excellent'
        WHEN rating >= 85 THEN 'Very Good'
        WHEN rating >= 80 THEN 'Good'
        ELSE 'Average'
    END AS quality_tier

FROM WINENOT.UAT.WINE_CATALOG
ORDER BY region, price_eur DESC;
```

### 2. Record count check

```sql
-- Total amount of wines in the new table
SELECT COUNT(*) as total_wines 
FROM WINENOT.PRD.MERGE;
```

### 3. Inspect transformed data

```sql
-- Snapshot of the first 5 registered wines with classification
SELECT 
    id,
    reference,
    region,
    region_classification,
    price_eur,
    price_category,
    rating,
    quality_tier
FROM WINENOT.PRD.WINES
LIMIT 5;
```

### 4. Distribution analysis by classification

```sql
-- Distribution of wines by region, price, and quality
SELECT 
    region_classification,
    price_category,
    quality_tier,
    COUNT(*) as wine_count,
    ROUND(AVG(price_eur), 2) as avg_price,
    ROUND(AVG(rating), 1) as avg_rating
FROM WINENOT.PRD.WINES
GROUP BY region_classification, price_category, quality_tier
ORDER BY wine_count DESC
LIMIT 20;
```

### 5. Exploration by rating

```sql
-- Top 10 wines with the best ratings
SELECT 
    reference,
    producer,
    region_classification,
    vintage,
    rating,
    price_eur,
    quality_tier
FROM WINENOT.PRD.WINES
ORDER BY rating DESC
LIMIT 10;

-- Wines with the lowest ratings (quality analysis)
SELECT 
    reference,
    producer,
    region_classification,
    rating,
    price_eur,
    quality_tier
FROM WINENOT.PRD.WINES
ORDER BY rating ASC
LIMIT 10;
```

## Use Cases

This classification enables:
- **Catalog segmentation** for targeted marketing campaigns
- **Performance analysis** by price range and region
- **Stock optimization** by identifying Premium vs. Budget wines
- **Recommendations building** based on quality/price
- **Simplified reporting** for sales management

## Technologies

- **Snowflake** : Cloud Data Warehouse
- **SQL** : Data transformation language
- **Environment** : UAT → PRD pipeline

## Technical Notes

- Source table contains 500 wine references
- No data was deleted, only enriched
- Classifications are based on business rules defined with the sales team
- The PRD.MERGE table is recreated on each execution (CREATE OR REPLACE)

- For data visualization, we recommend Looker Studio because it is a free solution, easy to integrate, and compatible with many SQL connectors. However, other tools like Power BI could be used for more advanced business needs.

---

**Authors** : Équipe Data WineNot  
 - Nolwenn Montillot
- Hannah Zilezsch
- Matthieu Dollfus
- Emma Lou Villaret
- Rayane Kryslak-Médioub
**Date** : Septembre, 30th 2025  
**Version** : 1.0


PIPELINE BUILD
# Don't take into account the scheduled time

🗓️ Gantt des étapes du pipeline (Vue synthétique)

Phase 1 — Setup & Fondations (Semaine 1 à 3)

Étape	Durée estimée	Peut démarrer en parallèle ?	Dépend de
Website & Design System – Rayane	3 sem.	✅ Oui	Aucune (front statique possible)
API Gateway scaffold – Nolwenn	3 sem.	✅ Oui	Aucune
Data Layer DDL – Matthieu	2 sem.	✅ Oui	Aucune
Airflow infra (docker, connexions) – Mory	1 sem.	✅ Oui	Aucune
Observability stack (Prometheus/Grafana setup) – Emma Lou	1 sem.	✅ Oui	Aucune

➡️ Tout peut être démarré en parallèle ici (aucune dépendance forte).
Chacun peut travailler dans son périmètre sans attendre les autres.
Seule exigence : s’accorder tôt sur les schemas de données et endpoints API.

⸻

Phase 2 — Intégration & Flux de Données (Semaine 4 à 6)

Étape	Durée	Parallèle ?	Dépend de
API business logic (Auth, Cart, Checkout, Stripe)	2-3 sem.	⚠️ Partiellement	OLTP schema stable
Website connexion API (/products, /cart, /checkout)	2 sem.	⚠️ Partielle	API endpoints mockés ou stables
dbt init + DW schema	2 sem.	✅ Oui	Postgres DDL validé
Airflow DAGs RAW dumps (Postgres → MinIO)	1 sem.	✅ Oui	Postgres opérationnel
MinIO lifecycle & encryption	1 sem.	✅ Oui	Airflow base en place
QA initiale (lint, smoke test CI)	1 sem.	✅ Oui	Builds dispo

➡️ Dépendances principales :
	•	Website dépend de l’API (au moins des mocks pour tests).
	•	API dépend du schéma OLTP défini par Matthieu.
	•	Airflow dépend du Postgres prêt et accessible.
	•	dbt peut se développer en parallèle, dès que les sources sont connues.

⸻

Phase 3 — Orchestration & Dataflows complets (Semaine 7 à 9)

Étape	Durée	Parallèle ?	Dépend de
Airflow DAG: lake_to_dw_curated (dbt run)	2 sem.	✅ Oui	dbt models disponibles
DAG purchase workflow (order.confirmed → invoice PDF → MinIO)	2 sem.	⚠️ Non	API doit émettre l’événement
Grafana dashboards (ETL health, stock)	1 sem.	✅ Oui	Airflow metrics disponibles
Alerting rules & notifications	1 sem.	✅ Oui	Prometheus data
QA E2E tests (signup → KYC → achat)	2 sem.	⚠️ Non	Website + API + Stripe en test

➡️ Critiques ici :
	•	Airflow → dépend de la bonne émission d’order.confirmed.
	•	Les tests E2E nécessitent le site, l’API et la base prêts en environnement intégré.

⸻

Phase 4 — Finalisation & Documentation (Semaine 10 à 11)

Étape	Durée	Parallèle ?	Dépend de
Compliance (GDPR, DPIA, retention)	1 sem.	✅ Oui	MinIO + Airflow stable
SECURITY.md, env.example	1 sem.	✅ Oui	Config finalisée
Docs (Swagger, dbt, Contrib Guide)	1 sem.	✅ Oui	Tout livrable validé
Lighthouse & Performance audits	1 sem.	✅ Oui	Website déployé


⸻

🧠 Synthèse stratégique (vue projet / dépendances fortes)

Dépendance clé	Sens	Risque si décalé
API ↔ Data schema	Matthieu définit avant Nolwenn	⚠️ API en blocage fonctionnel
Website ↔ API	Rayane dépend de /products + /cart	⚠️ Mock requis sinon freeze front
API ↔ Airflow	order.confirmed attendu	⚠️ Pas d’automatisation downstream
Airflow ↔ dbt	Mory dépend du DW de Matthieu	⚠️ Retard de reporting
Observability ↔ Tout le monde	Emma Lou observe Airflow/API	⛔ Manque de visibilité et alerting


⸻

🪜 Priorisation recommandée

1️⃣ Semaine 1–3 : Fondations
	•	DDL PostgreSQL, API skeleton, Next.js scaffold, Airflow & MinIO infra.
	•	Décision sur CMS et hosting.

2️⃣ Semaine 4–6 : Connexions
	•	API fonctionnelle (Auth, Cart, Checkout) + mock events.
	•	Front intégré à l’API.
	•	dbt prêt et testé sur premiers dumps.

3️⃣ Semaine 7–9 : Automatisation
	•	Airflow complet (RAW→CURATED, fact tables).
	•	Observabilité active.
	•	E2E tests sur toute la chaîne.

4️⃣ Semaine 10–11 : Stabilisation
	•	Compliance, docs, CI/CD propre.
	•	Lighthouse, QA finale, release candidate.

