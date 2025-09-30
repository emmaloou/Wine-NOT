-- Switch to the PRD schema
USE SCHEMA PRD;

-- Create the target table in PRD 
CREATE TABLE IF NOT EXISTS PRD.WINES (
    id INTEGER,
    reference VARCHAR,
    color VARCHAR,
    country VARCHAR,
    region VARCHAR,
    appellation VARCHAR,
    vintage INTEGER,
    grapes VARCHAR,  -- Keeping as VARCHAR for simplicity; could be ARRAY if needed
    alcohol_percent FLOAT,
    bottle_size_l FLOAT,
    sweetness VARCHAR,
    tannin INTEGER,
    acidity INTEGER,
    rating FLOAT,
    price_eur FLOAT,
    producer VARCHAR,
    stock_quantity INTEGER,
    wine_age INTEGER,        
    rating_category VARCHAR,  
    is_available BOOLEAN,
    price_per_liter FLOAT
);

-- Merge raw data from UAT into PRD with transformations
MERGE INTO PRD.WINES AS target
USING (
    SELECT 
        id,
        reference,
        LOWER(color) AS color,
        country,
        region,
        appellation,
        CAST(vintage AS INTEGER) AS vintage,
        REPLACE(grapes, '"', '') AS grapes,  -- Remove quotes from grapes
        CAST(alcohol_percent AS FLOAT) AS alcohol_percent,
        CAST(bottle_size_l AS FLOAT) AS bottle_size_l,
        sweetness,
        tannin,
        acidity,
        CAST(rating AS FLOAT) AS rating,
        CAST(price_eur AS FLOAT) AS price_eur,
        producer,
        COALESCE(stock_quantity, 0) AS stock_quantity,  -- Handle NULL as 0
        (2025 - vintage) AS wine_age,  -- Calculate age based on current year (2025)
        CASE 
            WHEN rating >= 95 THEN 'Excellent'
            WHEN rating >= 90 THEN 'Very Good'
            WHEN rating >= 85 THEN 'Good'
            ELSE 'Average'
        END AS rating_category,  -- Categorize rating
        (stock_quantity > 0) AS is_available,  -- Boolean for availability
        ROUND(price_eur / bottle_size_l, 2) AS price_per_liter  -- Price per liter
    FROM UAT.WINE_CATALOG
    WHERE 
        vintage <= 2025  -- Filter out future vintages
        AND rating BETWEEN 0 AND 100  -- Filter invalid ratings
) AS source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET
        target.reference = source.reference,
        target.color = source.color,
        target.country = source.country,
        target.region = source.region,
        target.appellation = source.appellation,
        target.vintage = source.vintage,
        target.grapes = source.grapes,
        target.alcohol_percent = source.alcohol_percent,
        target.bottle_size_l = source.bottle_size_l,
        target.sweetness = source.sweetness,
        target.tannin = source.tannin,
        target.acidity = source.acidity,
        target.rating = source.rating,
        target.price_eur = source.price_eur,
        target.producer = source.producer,
        target.stock_quantity = source.stock_quantity,
        target.wine_age = source.wine_age,
        target.rating_category = source.rating_category,
        target.is_available = source.is_available,
        target.price_per_liter = source.price_per_liter
WHEN NOT MATCHED THEN
    INSERT (
        id, reference, color, country, region, appellation, vintage, grapes,
        alcohol_percent, bottle_size_l, sweetness, tannin, acidity, rating,
        price_eur, producer, stock_quantity, wine_age, rating_category,
        is_available, price_per_liter
    )
    VALUES (
        source.id, source.reference, source.color, source.country, source.region,
        source.appellation, source.vintage, source.grapes, source.alcohol_percent,
        source.bottle_size_l, source.sweetness, source.tannin, source.acidity,
        source.rating, source.price_eur, source.producer, source.stock_quantity,
        source.wine_age, source.rating_category, source.is_available,
        source.price_per_liter
    );

SELECT COUNT(*) AS total_rows, 
       SUM(CASE WHEN wine_age IS NOT NULL THEN 1 ELSE 0 END) AS transformed_rows
FROM PRD.WINES;
