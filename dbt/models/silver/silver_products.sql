{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_products') }}
),
validated as (
  select *
  from src
  where product_id is not null
    and sku is not null
    and current_price is not null and try_cast(current_price as double) > 0
    and currency in ('AUD', 'USD', 'EUR')
  and (not is_discontinued or (discontinued_dt is not null and cast(discontinued_dt as varchar) != '' and trim(cast(discontinued_dt as varchar)) != '' and try_cast(discontinued_dt as date) is not null))
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by product_id order by staging_ts desc) as rn
    from validated
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