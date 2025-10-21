{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_exchange_rates') }}
),
deduped as (
  select *
  from (
    select *,
      row_number() over (partition by date, currency order by date desc) as rn
    from src
  ) t
  where rn = 1
)
select
  date,
  currency,
  rate_to_aud
from deduped
order by date, currency
