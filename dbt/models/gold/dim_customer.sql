{{ config(materialized='table') }}
with silver_customers as (
  select * from {{ ref('silver_customers') }}
),
customers_enhanced as (
  select
    customer_id,
    natural_key,
    case when gdpr_status = 'Not Consented' then 'MASKED' else first_name end as first_name,
    case when gdpr_status = 'Not Consented' then 'MASKED' else last_name end as last_name,
    case when gdpr_status = 'Not Consented' then 'MASKED' else full_name end as full_name,
    case when gdpr_status = 'Not Consented' then md5(email) else email end as email,
    email_domain,
    case when gdpr_status = 'Not Consented' then 'MASKED' else phone end as phone,
    case when gdpr_status = 'Not Consented' then city else address_line1 end as address_line1,
    address_line2,
    city,
    state_region,
    postcode,
    country_code,
    country_name,
    birth_date,
    age as customer_age,
    join_ts_utc,
    days_since_join,
    datediff('day', join_ts_utc, current_date) as customer_lifetime_days,
    customer_segment,
    gdpr_status
  from silver_customers
)
select
  customer_id as customer_sk,
  *
from customers_enhanced
order by customer_id
