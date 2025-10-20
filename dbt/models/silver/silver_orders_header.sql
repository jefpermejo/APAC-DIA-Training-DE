{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_orders_header') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by order_id order by order_ts_utc desc) as rn
    from src
  ) t
  where rn = 1
)
select
  order_id,
  order_ts_utc,
  order_dt_local,
  customer_id,
  store_id,
  channel,
  payment_method,
  coupon_code,
  shipping_fee,
  currency
from deduped
order by order_id