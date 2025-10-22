{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_orders_header') }}
),
validated as (
  select *
  from src
  where order_id is not null
    and customer_id > 0
    and store_id > 0
    and order_ts_utc is not null
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by order_id order by order_ts_utc desc) as rn
    from validated
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