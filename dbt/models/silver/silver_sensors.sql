{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_sensors') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by sensor_ts, store_id, shelf_id order by sensor_ts desc) as rn
    from src
  ) t
  where rn = 1
)
select
  sensor_ts,
  store_id,
  shelf_id,
  temperature_celcius,
  humidity_percent,
  battery_mv
from deduped
order by sensor_ts, store_id, shelf_id
