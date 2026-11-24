-- AdventureWorks Gold-layer sample analytics
-- Run after creating the Gold views in your serverless SQL database.
-- Confirm column names against the source schema before extending these queries.

-- 1. Order volume by order date
SELECT
    OrderDate,
    COUNT(DISTINCT OrderNumber) AS total_orders
FROM gold.sales
GROUP BY OrderDate
ORDER BY OrderDate;

-- 2. Total units ordered by order date
SELECT
    OrderDate,
    SUM(OrderQuantity) AS total_units_ordered
FROM gold.sales
GROUP BY OrderDate
ORDER BY OrderDate;

-- 3. Sales row count and date coverage
SELECT
    COUNT_BIG(*) AS sales_row_count,
    MIN(OrderDate) AS first_order_date,
    MAX(OrderDate) AS last_order_date
FROM gold.sales;
