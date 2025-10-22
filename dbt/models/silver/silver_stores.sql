{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_stores') }}
),
validated as (
  select *
  from src
  where store_id is not null
    and store_code is not null
  and latitude between -90 and 90
  and longitude between -180 and 180
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by store_id order by staging_ts desc) as rn,
      row_number() over (partition by store_code order by staging_ts desc) as rn_code
    from validated
  ) t
  where rn = 1 and rn_code = 1
)
select
  store_id,
  store_code,
  name,
  channel,
  region,
  state,
  latitude,
  longitude,
  open_dt,
  close_dt,
  days_open,
  store_status
from deduped
order by store_id