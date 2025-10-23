-- Custom test: Longitude between -180 and 180
SELECT *
FROM {{ model }}
WHERE longitude < -180 OR longitude > 180