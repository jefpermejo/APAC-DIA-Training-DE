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
)

select * from cleaned_customers