{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_shipments') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by shipment_id order by shipped_date desc) as rn
    from src
  ) t
  where rn = 1
)
select
  shipment_id,
  order_id,
  carrier,
  shipped_date,
  delivered_date,
  ship_cost
from deduped
order by shipment_id
