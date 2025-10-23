-- Custom test: Discount percent between 0 and 100
SELECT *
FROM {{ model }}
WHERE discount_percent < 0 OR discount_percent > 100