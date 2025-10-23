-- Custom test: Email format validation
SELECT *
FROM {{ model }}
WHERE email !~ '^[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$'