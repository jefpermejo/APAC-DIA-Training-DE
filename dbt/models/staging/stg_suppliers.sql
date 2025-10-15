{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'suppliers') }}
),
cleaned_suppliers as (
  select
    cast(supplier_id as bigint) as supplier_id,
    trim(supplier_code) as supplier_code,
    trim(name) as name,
    upper(trim(country_code)) as country_code,
    cast(lead_time_days as integer) as lead_time_days,
    cast(preferred as boolean) as preferred
  from src
)
select * from cleaned_suppliers