{{ config(materialized='view') }}
with header as (
  select * from {{ ref('silver_orders_header') }}
),
lines as (
  select * from {{ ref('silver_orders_lines') }}
),
joined as (
  select
    h.order_id,
    h.order_ts_utc,
    h.order_dt_local,
    h.channel,
    h.payment_method,
    h.coupon_code,
    h.shipping_fee,
    h.currency,
    h.customer_id,
    h.store_id,
    l.line_number,
    l.product_id,
    l.quantity,
    l.unit_price,
    l.line_discount_percent,
    l.tax_percent
  from header h
  inner join lines l on h.order_id = l.order_id
)
select * from joined
order by order_id, line_number
