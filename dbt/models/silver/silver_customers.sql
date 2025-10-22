{{ config(materialized='table') }}
with src as (
  select * from {{ ref('stg_customers') }}
),
validated as (
  select *
  from src
  where customer_id is not null
    and natural_key is not null
    and email_clean like '%@%.%'
    and phone is not null and phone != ''
    and address_line1 is not null and address_line1 != ''
    and latitude between -44 and -10
    and longitude between 112 and 152
    and birth_date <= current_date
),
deduped as (
  select *
  from (
       select *,
         row_number() over (partition by customer_id order by staging_ts desc) as rn,
         row_number() over (partition by natural_key order by staging_ts desc) as rn_nk
    from validated
  ) t
  where rn = 1 and rn_nk = 1
)
select
  customer_id,
  natural_key,
  first_name,
  last_name,
  full_name,
  email_clean as email,
  email_domain,
  phone,
  address_line1,
  address_line2,
  city,
  state_region,
  postcode,
  country_code,
  country_name,
  birth_date,
  age,
  join_ts_utc,
  days_since_join,
  customer_segment,
  gdpr_status
from deduped
order by customer_id