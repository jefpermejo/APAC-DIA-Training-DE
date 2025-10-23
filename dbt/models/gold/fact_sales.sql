{{ config(materialized='incremental') }}
with orders_enriched as (
  select * from {{ ref('int_orders_combined') }}
),
products as (
  select * from {{ ref('dim_product') }} where is_current = true
),
customers as (
  select * from {{ ref('dim_customer') }}
),
stores as (
  select * from {{ ref('dim_store') }}
),
dates as (
  select * from {{ ref('dim_date') }}
)
select
  {{ dbt_utils.generate_surrogate_key(['o.order_id', 'o.line_number']) }} as sale_sk,
  o.order_id,
  o.line_number,
  o.order_ts_utc,
  o.customer_id,
  o.store_id,
  o.product_id,
  o.unit_price,
  o.quantity,
  o.currency,
  o.rate_to_aud,
  o.line_total_orig_ccy,
  o.line_total_base_ccy,
  o.channel,
  o.coupon_code,
  o.payment_method,
  o.line_total_base_ccy as net_amount,
  o.line_discount_percent * o.unit_price * o.quantity as discount_amount,
  o.tax_percent * o.unit_price * o.quantity as tax_amount,
  -- Dimension attributes for reporting
  prod.product_name,
  prod.category,
  cust.customer_segment,
  sto.store_name,
  sto.region,
  d.year,
  d.month
from orders_enriched ord
inner join products prod on ord.product_id = prod.product_id
left join customers cust on ord.customer_id = cust.customer_id
left join stores sto on ord.store_id = sto.store_id
left join dates d on date(ord.order_ts_utc) = d.date
where ord.product_id > 0
