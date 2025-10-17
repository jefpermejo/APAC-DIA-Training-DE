{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'customers') }}
),
cleaned_customers as (
  select
    cast(customer_id as bigint) as customer_id,
    natural_key,
    trim(first_name) as first_name,
    trim(last_name) as last_name,
    lower(trim(email)) as email,
    trim(phone) as phone,
    trim(address_line1) as address_line1, 
    trim(address_line2) as address_line2, 
    trim(city) as city, 
    upper(trim(state_region)) as state_region,
    upper(trim(postcode)) as postcode, 
    upper(trim(country_code)) as country_code,
    cast(latitude as double) as latitude,
    cast(longitude as double) as longitude,
    cast(birth_date as date) as birth_date,
    cast(join_ts as timestamp) as join_ts_utc,
    cast(is_vip as boolean) as is_vip,
    cast(gdpr_consent as boolean) as gdpr_consent
  from src
),

enriched_customers as (
  select 
  *,
  trim(first_name) || ' ' || trim(last_name) as full_name,
  date_diff('year', birth_date, current_date) as age,
  date_diff('day', join_ts_utc, current_timestamp) as days_since_join,
  case 
    when is_vip then 'VIP'
    else 'Regular'
  end as customer_segment,
  case 
    when gdpr_consent then 'Consented'
    else 'Not Consented'
  end as gdpr_status,
  case 
    when country_code = 'US' then 'United States'
    when country_code = 'CA' then 'Canada'
    when country_code = 'GB' then 'United Kingdom'
    when country_code = 'AU' then 'Australia'
    when country_code = 'IN' then 'India'
    else 'Other'
  end as country_name,
  case 
    when email = 'bad_email' then 'Invalid Email'
    else regexp_replace(email, '[^a-zA-Z0-9@._-]', '')
  end as email_clean,
  regexp_extract(email, '@(.*)$', 1) as email_domain,
  cast(current_timestamp as timestamp) as staging_ts
  from cleaned_customers
)

select * from enriched_customers