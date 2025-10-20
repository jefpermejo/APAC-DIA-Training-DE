{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_orders_lines') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by order_id, line_number order by order_id desc) as rn
    from src
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