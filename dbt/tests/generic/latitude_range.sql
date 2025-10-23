-- Custom test: Latitude between -90 and 90
SELECT *
FROM {{ model }}
WHERE latitude < -90 OR latitude > 90