{{ config(materialized='view') }}
with header as (
  select * from {{ ref('silver_orders_header') }}
),
lines as (
  select * from {{ ref('silver_orders_lines') }}
),
customers as (
  select customer_id, customer_segment from {{ ref('silver_customers') }}
),
products as (
  select product_id, name as product_name, category, subcategory, price_segment, product_status, product_group from {{ ref('silver_products') }}
),
stores as (
  select store_id, name as store_name, region, state, channel from {{ ref('silver_stores') }}
),
fx as (
  select currency, date, rate_to_aud from {{ ref('silver_exchange_rates') }}
),
joined as (
  select
    h.order_id,
    h.order_ts_utc,
    h.customer_id,
    c.customer_segment,
  h.store_id,
  s.store_name,
  s.region,
  s.state,
  s.channel,
  l.line_number,
  l.product_id,
  p.product_name,
  p.category,
  p.subcategory,
  p.price_segment,
  p.product_status,
  p.product_group,
  l.quantity,
  l.unit_price,
  l.line_discount_percent,
  l.tax_percent,
  h.currency,
  fx.rate_to_aud,
  l.unit_price * l.quantity as line_total_orig_ccy,
  l.unit_price * l.quantity * fx.rate_to_aud as line_total_base_ccy,
  h.coupon_code,
  h.payment_method
  from header h
  inner join lines l on h.order_id = l.order_id
  left join customers c on h.customer_id = c.customer_id
  left join products p on l.product_id = p.product_id
  left join stores s on h.store_id = s.store_id
  left join fx on h.currency = fx.currency and date(h.order_ts_utc) = fx.date
)
select
  order_id,
  order_ts_utc,
  customer_id,
  customer_segment,
  store_id,
  store_name,
  region,
  state,
  channel,
  line_number,
  product_id,
  product_name,
  category,
  subcategory,
  price_segment,
  product_status,
  product_group,
  quantity,
  unit_price,
  line_discount_percent,
  tax_percent,
  currency,
  rate_to_aud,
  line_total_orig_ccy,
  line_total_base_ccy,
  coupon_code,
  payment_method
from joined
order by order_id, line_number