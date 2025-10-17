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
),
enriched_products as (
  select 
  *,
  case 
    when current_price < 20 then 'Budget'
    when current_price between 20 and 100 then 'Mid-Range'
    else 'Premium'
  end as price_segment,
  date_diff('day', introduced_dt, current_date) as days_on_market,
  case 
    when is_discontinued then 'Discontinued'
    when date_diff('day', introduced_dt, current_date) <= 90 then 'New'
    else 'Active'
  end as product_status,
  case
    when category in ('ELECTRONICS', 'APPLIANCES') then 'High Value'
    when category in ('FOOD', 'BEVERAGES') then 'Consumable'
    else 'General Merchandise'
  end as product_group,
  cast(current_timestamp as timestamp) as staging_ts
  from cleaned_products
)
select * from enriched_products