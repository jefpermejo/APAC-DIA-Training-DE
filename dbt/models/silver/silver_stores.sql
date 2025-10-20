{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_stores') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by store_id order by staging_ts desc) as rn
    from src
  ) t
  where rn = 1
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