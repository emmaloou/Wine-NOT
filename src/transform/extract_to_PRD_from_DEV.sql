-- Alternative to your teacher's script: sources from DEV.PRODUCTS
CREATE OR REPLACE TABLE WINENOT.PRD.WINES AS
SELECT
  id, reference, color, country, region, appellation, vintage, grapes,
  alcohol_percent, bottle_size_l, sweetness, tannin, acidity, rating,
  price_eur, producer, stock_quantity,
  CASE
    WHEN region = 'Rhone' THEN 'Premium French - Rhone Valley'
    WHEN region = 'Bordeaux' THEN 'Premium French - Bordeaux'
    WHEN region = 'Burgundy' THEN 'Premium French - Burgundy'
    WHEN region = 'Champagne' THEN 'Prestige French - Champagne'
    WHEN region IN ('Loire','Alsace','Provence','Jura','Beaujolais','Languedoc') THEN 'Regional French'
    WHEN region = 'Rioja' THEN 'Premium Spanish - Rioja'
    WHEN region = 'Ribera del Duero' THEN 'Premium Spanish - Ribera'
    WHEN region = 'Rias Baixas' THEN 'Regional Spanish - Atlantic'
    WHEN region IN ('Tuscany','Piedmont') THEN 'Premium Italian - North'
    WHEN region IN ('Sicily','Veneto') THEN 'Regional Italian'
    WHEN region = 'Kakheti' THEN 'Georgian Heritage'
    ELSE 'Other' END AS region_classification,
  CASE
    WHEN price_eur < 15 THEN 'Budget'
    WHEN price_eur BETWEEN 15 AND 30 THEN 'Mid-Range'
    WHEN price_eur BETWEEN 30 AND 50 THEN 'Premium'
    WHEN price_eur >= 50 THEN 'Luxury'
  END AS price_category,
  CASE
    WHEN rating >= 95 THEN 'Exceptional'
    WHEN rating >= 90 THEN 'Excellent'
    WHEN rating >= 85 THEN 'Very Good'
    WHEN rating >= 80 THEN 'Good'
    ELSE 'Average'
  END AS quality_tier
FROM WINENOT.DEV.PRODUCTS
ORDER BY region, price_eur DESC;
