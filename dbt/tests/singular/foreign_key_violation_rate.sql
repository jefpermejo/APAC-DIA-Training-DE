-- Custom test: Foreign key violation rate < 1.5%
WITH violations AS (
  SELECT o.*
  FROM {{ ref('stg_orders') }} o
  LEFT JOIN {{ ref('stg_customers') }} c ON o.customer_id = c.customer_id
  WHERE c.customer_id IS NULL
),
counts AS (
  SELECT COUNT(*) AS total_orders FROM {{ ref('stg_orders') }}
  UNION ALL
  SELECT COUNT(*) AS violations FROM violations
)
SELECT * FROM counts WHERE violations / NULLIF(total_orders, 0) >= 0.015