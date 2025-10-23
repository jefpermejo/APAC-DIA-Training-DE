
{{ config(materialized='table') }}

with products_scd as (
  select
    product_id,
    name as product_name,
    category,
    subcategory,
    current_price as product_price,
    price_segment,
    product_status,
    product_group,
    dbt_valid_from,
    dbt_valid_to,
    coalesce(dbt_valid_to, '9999-12-31') as valid_to,
    case when dbt_valid_to is null then true else false end as is_current,
    lag(current_price) over (partition by product_id order by dbt_valid_from) as prev_price,
    case when lag(current_price) over (partition by product_id order by dbt_valid_from) is not null and current_price != lag(current_price) over (partition by product_id order by dbt_valid_from) then true else false end as price_changed
  from {{ ref('products_snapshot') }}
)
select
  {{ dbt_utils.generate_surrogate_key(['product_id', 'dbt_valid_from']) }} as product_sk,
  *
from products_scd
order by product_id, dbt_valid_from
