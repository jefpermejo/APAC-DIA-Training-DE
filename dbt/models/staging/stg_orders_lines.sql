{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'orders_lines') }}
),
cleaned_orders_lines as (
  select
    cast(order_id as bigint) as order_id,
    cast(line_number as int) as line_number,
    cast(product_id as bigint) as product_id,
    cast(qty as int) as quantity,
    cast(unit_price as decimal(10, 4)) as unit_price,
    cast(line_discount_pct as decimal(10, 4)) as line_discount_percent,
    cast(tax_pct as decimal(10, 4)) as tax_percent
  from src
)
select *, cast(current_timestamp as timestamp) as staging_ts from cleaned_orders_lines