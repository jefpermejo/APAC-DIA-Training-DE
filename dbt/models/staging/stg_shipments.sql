{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'shipments') }}
),
cleaned_shipments as (
  select
    cast(shipment_id as bigint) as shipment_id,
    cast(order_id as bigint) as order_id,
    upper(trim(carrier)) as carrier,
    cast(shipped_at as timestamp) as shipped_date,
    cast(delivered_at as timestamp) as delivered_date,
    cast(ship_cost as double) as ship_cost
  from src
)
select * from cleaned_shipments