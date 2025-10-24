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
  {{ dbt_utils.generate_surrogate_key(['ord.order_id', 'ord.line_number']) }} as sale_sk,
  ord.order_id,
  ord.line_number,
  ord.order_ts_utc,
  ord.customer_id,
  ord.store_id,
  ord.product_id,
  ord.unit_price,
  ord.quantity,
  ord.currency,
  ord.rate_to_aud,
  ord.line_total_orig_ccy,
  ord.line_total_base_ccy,
  ord.channel,
  ord.coupon_code,
  ord.payment_method,
  ord.line_total_base_ccy as net_amount,
  ord.line_discount_percent * ord.unit_price * ord.quantity as discount_amount,
  ord.tax_percent * ord.unit_price * ord.quantity as tax_amount,
  -- Dimension attributes for reporting
  prod.product_name,
  prod.category,
  cust.customer_segment,
  sto.store_name,
  sto.region,
  d.date_id,
  d.year,
  d.month,
  d.day
from orders_enriched ord
inner join products prod on ord.product_id = prod.product_id
left join customers cust on ord.customer_id = cust.customer_id
left join stores sto on ord.store_id = sto.store_id
left join dates d on ord.order_ts_utc::date = d.date
where ord.product_id > 0
