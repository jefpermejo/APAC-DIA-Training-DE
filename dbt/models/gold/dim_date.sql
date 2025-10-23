{{ config(materialized='table') }}
with calendar as (
  select
  cast(strftime(date, '%Y%m%d') as varchar) as date_id,
    date,
  date_part('year', CAST(date AS DATE)) as year,
  date_part('month', CAST(date AS DATE)) as month,
  date_part('day', CAST(date AS DATE)) as day,
  date_part('week', CAST(date AS DATE)) as week,
  date_part('quarter', CAST(date AS DATE)) as quarter,
  case when extract(dow from CAST(date AS DATE)) in (0, 6) then true else false end as is_weekend,
  case when extract(month from CAST(date AS DATE)) in (7,8,9) then 'Q3' else 'Other' end as fiscal_period,
  case when CAST(date AS DATE) in ('2025-01-01','2025-12-25') then true else false end as is_holiday_au,
  case when CAST(date AS DATE) in ('2025-07-04','2025-12-25') then true else false end as is_holiday_us,
  case when CAST(date AS DATE) in ('2025-12-25') then true else false end as is_holiday_uk,
  case when extract(day from CAST(date AS DATE)) = 1 then true else false end as is_quarter_boundary,
  strftime('%G-%V', CAST(date AS DATE)) as iso_week
  from (select unnest(generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day')) as date) d
)
select * from calendar
order by date_id
