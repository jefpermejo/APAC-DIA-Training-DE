{{ config(materialized='table', contract={'enforced': true}) }}

with src as (
  select * from {{ source('main_stg', 'exchange_rates') }}
),
cleaned_exchange_rates as (
  select
    cast(date as date) as date,
    upper(trim(currency)) as currency,
    cast(rate_to_aud as double) as rate_to_aud
  from src
)
select * from cleaned_exchange_rates