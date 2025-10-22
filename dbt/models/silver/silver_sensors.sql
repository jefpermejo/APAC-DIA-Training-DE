{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_sensors') }}
),
validated as (
  select *
  from src
  where sensor_ts is not null and cast(sensor_ts as varchar) != '' and trim(cast(sensor_ts as varchar)) != '' and try_cast(sensor_ts as timestamp) is not null
    and temperature_celcius between 2 and 35
    and humidity_percent between 20 and 80
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by sensor_ts, store_id, shelf_id order by sensor_ts desc) as rn
    from validated
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
