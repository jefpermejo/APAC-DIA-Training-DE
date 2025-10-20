{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_products') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by product_id order by staging_ts desc) as rn
    from src
  ) t
  where rn = 1
)
select
  product_id,
  sku,
  name,
  category,
  subcategory,
  current_price,
  currency,
  is_discontinued,
  introduced_dt,
  discontinued_dt,
  price_segment,
  days_on_market,
  product_status,
  product_group
from deduped
order by product_id