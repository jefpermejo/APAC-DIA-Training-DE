{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'sensors') }}
),
cleaned_sensors as (
  select
    cast(sensor_ts as timestamp) as sensor_ts,
    cast(store_id as bigint) as store_id,
    trim(shelf_id) as shelf_id,
    cast(temperature_c as double) as temperature_celcius,
    cast(humidity_pct as double) as humidity_percent,
    cast(battery_mv as int) as battery_mv
  from src
)
select * from cleaned_sensors