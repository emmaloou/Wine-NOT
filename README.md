# WineNot - Wine Catalog Data Classification

## Contexte du Projet

**WineNot** est une entreprise spécialisée dans la distribution de vins de qualité issus de différentes régions viticoles européennes et géorgiennes. 

Notre base de données catalogue **500 références de vins** avec des informations détaillées (région, cépage, millésime, notes de dégustation, prix, stock). Pour améliorer notre stratégie commerciale et faciliter l'analyse de notre inventaire, nous avons restructuré notre catalogue en créant une table enrichie avec des classifications métier.

## Objectif

Créer une table de production (`WINENOT.PRD.MERGE`) à partir de notre catalogue brut (`WINENOT.UAT.WINE_CATALOG`) en ajoutant trois dimensions de classification :

1. **Classification régionale** : Catégorisation des vins par prestige et origine géographique
2. **Classification prix** : Segmentation en 4 gammes tarifaires
3. **Classification qualité** : Évaluation basée sur les notes critiques (rating)

## Architecture des Données

```
WINENOT (Database)
├── UAT (Schema)
│   └── WINE_CATALOG (Table source - 500 vins)
└── PRD (Schema)
    └── WINES (Table enrichie avec classifications)
```

## 📊 Structure de la Classification

### Classification Régionale
| Catégorie | Régions |
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

### Classification Prix
- **Budget** : < 15€
- **Mid-Range** : 15-30€
- **Premium** : 30-50€
- **Luxury** : ≥ 50€

### Classification Qualité
- **Exceptional** : rating ≥ 95
- **Excellent** : rating 90-94
- **Very Good** : rating 85-89
- **Good** : rating 80-84
- **Average** : rating < 80

## 🔧 Script SQL de Transformation

### 1. Création de la table enrichie

```sql
CREATE OR REPLACE TABLE WINENOT.PRD.WINES AS
SELECT 
    -- Colonnes originales
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
    
    -- CLASSIFICATION PAR RÉGION
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
    
    -- CLASSIFICATION PAR PRIX
    CASE 
        WHEN price_eur < 15 THEN 'Budget'
        WHEN price_eur BETWEEN 15 AND 30 THEN 'Mid-Range'
        WHEN price_eur BETWEEN 30 AND 50 THEN 'Premium'
        WHEN price_eur >= 50 THEN 'Luxury'
    END AS price_category,
    
    -- CLASSIFICATION PAR QUALITÉ
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

### 2. Vérification du nombre d'enregistrements

```sql
-- Compte total des vins dans la nouvelle table
SELECT COUNT(*) as total_wines 
FROM WINENOT.PRD.MERGE;
```

### 3. Inspection des données transformées

```sql
-- Aperçu des 5 premiers enregistrements avec classifications
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

### 4. Analyse de la distribution par classification

```sql
-- Distribution des vins par région, prix et qualité
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

### 5. Exploration des vins par note

```sql
-- Top 10 des vins les mieux notés
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

-- Vins avec les notes les plus faibles (analyse qualité)
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

## Cas d'Usage

Cette classification permet de :
- **Segmenter le catalogue** pour des campagnes marketing ciblées
- **Analyser la performance** par gamme de prix et région
- **Optimiser les stocks** en identifiant les vins Premium vs Budget
- **Créer des recommandations** basées sur qualité/prix
- **Faciliter le reporting** pour la direction commerciale

## Technologies

- **Snowflake** : Data Warehouse cloud
- **SQL** : Langage de transformation des données
- **Environment** : UAT → PRD pipeline

## Notes Techniques

- La table source contient 500 références de vins
- Aucune donnée n'a été supprimée, seulement enrichie
- Les classifications sont basées sur des règles métier définies avec l'équipe commerciale
- La table PRD.MERGE est recréée à chaque exécution (CREATE OR REPLACE)

---

**Auteurs** : Équipe Data WineNot  
 - Nolwenn Montillot
- Hannah Zilezsch
- Matthieu Dollfus
- Emma Lou Villaret
- Rayane Kryslak-Médioub
**Date** : 30 septembre 2025  
**Version** : 1.0
