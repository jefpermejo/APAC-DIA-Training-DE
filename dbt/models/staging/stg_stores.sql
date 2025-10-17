{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'stores') }}
),
cleaned_stores as (
  select
    cast(store_id as bigint) as store_id,
    trim(store_code) as store_code,
    trim(name) as name,
    trim(channel) as channel,
    trim(region) as region,
    upper(trim(state)) as state,
    cast(latitude as double) as latitude,
    cast(longitude as double) as longitude,
    cast(open_dt as date) as open_dt,
    cast(close_dt as date) as close_dt
  from src
),
enriched_stores as (
  select 
  *,
  date_diff('day', open_dt, current_date) as days_open,
  case 
    when close_dt is not null and close_dt <= current_date then 'Closed'
    else 'Open'
  end as store_status,
  cast(current_timestamp as timestamp) as staging_ts
  from cleaned_stores
)
select * from enriched_stores