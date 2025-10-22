{{ config(materialized='view') }}
with orders as (
  select * from {{ ref('silver_orders_header') }}
),
lines as (
  select * from {{ ref('silver_orders_lines') }}
),
fx as (
  select * from {{ ref('silver_exchange_rates') }}
),
joined as (
  select
    o.order_id,
    o.order_ts_utc,
    o.currency,
    fx.rate_to_aud,
    l.line_number,
    l.product_id,
    l.unit_price,
    l.quantity,
    l.unit_price * l.quantity as amount_original_ccy,
    l.unit_price * l.quantity * fx.rate_to_aud as amount_aud
  from orders o
  inner join lines l on o.order_id = l.order_id
  left join fx on o.currency = fx.currency and date(o.order_ts_utc) = fx.date
)
select * from joined
order by order_id, line_number
