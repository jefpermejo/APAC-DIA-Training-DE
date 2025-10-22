{{ config(materialized='view') }}
with orders as (
  select * from {{ ref('silver_orders_header') }}
),
customers as (
  select * from {{ ref('silver_customers') }}
),
stores as (
  select * from {{ ref('silver_stores') }}
),
joined as (
  select
    o.order_id,
    o.order_ts_utc,
    o.customer_id,
    c.full_name as customer_name,
    c.customer_segment,
    o.store_id,
    s.name as store_name,
    s.region as store_region,
    o.channel,
    o.payment_method,
    o.coupon_code,
    o.shipping_fee,
    o.currency
  from orders o
  inner join customers c on o.customer_id = c.customer_id
  inner join stores s on o.store_id = s.store_id
)
select * from joined
order by order_id
