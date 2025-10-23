{{ config(materialized='table') }}
with silver_stores as (
  select * from {{ ref('silver_stores') }}
),
stores_enhanced as (
  select
    store_id,
    name as store_name,
    region,
    state,
    channel,
    datediff('day', open_dt, current_date) as store_age_days,
    case when latitude > 0.5 then 'Large' else 'Small' end as store_size_category,
    case when close_dt is null then 'Open' else 'Closed' end as operational_status
  from silver_stores
)
select
  store_id as store_sk,
  *
from stores_enhanced
order by store_id
