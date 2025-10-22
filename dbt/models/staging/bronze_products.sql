-- Bronze products view: exposes raw product data for snapshots and downstream cleaning
-- Grain: One row per product_id from raw bronze source
-- Bronze products view: now sources from cleaned staging model
-- This allows snapshots to reference bronze_products as a business-ready view
select * from {{ ref('stg_products') }}