{{ config(materialized='table') }}
with silver_suppliers as (
  select * from {{ ref('silver_suppliers') }}
),
suppliers_enhanced as (
  select
    supplier_id,
    name as supplier_name,
    country_code,
    lead_time_category,
    preferred,
    case when lead_time_days < 5 then 'Tier 1' when lead_time_days < 10 then 'Tier 2' else 'Tier 3' end as supplier_tier
  from silver_suppliers
)
select
  supplier_id as supplier_sk,
  *
from suppliers_enhanced
order by supplier_id
