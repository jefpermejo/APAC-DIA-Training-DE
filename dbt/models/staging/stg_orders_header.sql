{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'orders_header') }}
),
cleaned_orders_header as (
  select
    cast(order_id as bigint) as order_id,
    cast(order_ts as timestamp) as order_ts_utc,
    cast(order_dt_local as date) as order_dt_local,
    cast(customer_id as int) as customer_id,
    cast(store_id as int) as store_id,
    trim(channel) as channel,
    trim(payment_method) as payment_method,
    trim(coupon_code) as coupon_code,
    cast(shipping_fee as decimal(10, 2)) as shipping_fee,
    upper(trim(currency)) as currency
  from src
)
select *, cast(current_timestamp as timestamp) as staging_ts from cleaned_orders_header