{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'products') }}
),
cleaned_products as (
  select
    cast(product_id as bigint) as product_id,
    trim(sku) as sku,
    trim(name) as name,
    upper(trim(category)) as category,
    upper(trim(subcategory)) as subcategory,
    cast(current_price as double) as current_price,
    upper(trim(currency)) as  currency,
    cast(is_discontinued as boolean) as is_discontinued,
    cast(introduced_dt as date) as introduced_dt,
    cast(discontinued_dt as date) as discontinued_dt
  from src
)
select * from cleaned_products