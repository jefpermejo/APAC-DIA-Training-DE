{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_orders_lines') }}
),
validated as (
  select *
  from src
  where order_id is not null
    and product_id > 0
    and quantity > 0
    and unit_price > 0
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by order_id, line_number order by order_id desc) as rn
    from validated
  ) t
  where rn = 1
)
select
  order_id,
  line_number,
  product_id,
  quantity,
  unit_price,
  line_discount_percent,
  tax_percent
from deduped
order by order_id, line_number