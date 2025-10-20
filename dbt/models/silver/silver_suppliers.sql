{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_suppliers') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by supplier_id order by staging_ts desc) as rn
    from src
  ) t
  where rn = 1
)
select
  supplier_id,
  supplier_code,
  name,
  country_code,
  lead_time_days,
  preferred,
  lead_time_category
from deduped
order by supplier_id