{{ config(materialized='view') }}
with lines as (
  select * from {{ ref('silver_orders_lines') }}
),
products as (
  select * from {{ ref('silver_products') }}
),
joined as (
  select
    l.order_id,
    l.line_number,
    l.product_id,
    p.name as product_name,
    p.category,
    p.subcategory,
    l.quantity,
    l.unit_price,
    l.line_discount_percent,
    l.tax_percent,
    p.price_segment,
    p.product_status,
    p.product_group
  from lines l
  inner join products p on l.product_id = p.product_id
)
select * from joined
order by order_id, line_number
