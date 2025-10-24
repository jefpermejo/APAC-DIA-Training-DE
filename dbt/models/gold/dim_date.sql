{{ config(materialized='table') }}
with calendar as (
  select
    cast(strftime(date, '%Y%m%d') as varchar) as date_id,
    date,
    strftime(date, '%Y-%m-%d') as day_ymd,
    date_part('year', CAST(date AS DATE)) as year,
    date_part('month', CAST(date AS DATE)) as month,
    date_part('day', CAST(date AS DATE)) as day,
    date_part('week', CAST(date AS DATE)) as week,
    date_part('quarter', CAST(date AS DATE)) as quarter,
    case when extract(dow from CAST(date AS DATE)) in (0, 6) then true else false end as is_weekend,
    -- Fiscal year starts in July, so fiscal Q1 is July-Sept, Q2 is Oct-Dec, Q3 is Jan-Mar, Q4 is Apr-Jun
    case 
      when extract(month from CAST(date AS DATE)) between 7 and 9 then 'Q1'
      when extract(month from CAST(date AS DATE)) between 10 and 12 then 'Q2'
      when extract(month from CAST(date AS DATE)) between 1 and 3 then 'Q3'
      else 'Q4'
    end as fiscal_quarter,
    case 
      when extract(month from CAST(date AS DATE)) >= 7 then date_part('year', CAST(date AS DATE))
      else date_part('year', CAST(date AS DATE)) - 1
    end as fiscal_year,
    case when CAST(date AS DATE) in ('2025-01-01','2025-12-25') then true else false end as is_holiday_au,
    case when CAST(date AS DATE) in ('2025-07-04','2025-12-25') then true else false end as is_holiday_us,
    case when CAST(date AS DATE) in ('2025-12-25') then true else false end as is_holiday_uk,
    case when extract(day from CAST(date AS DATE)) = 1 then true else false end as is_quarter_boundary,
    strftime('%G-%V', CAST(date AS DATE)) as iso_week
  from (select unnest(generate_series('2020-01-01'::date, '2030-12-31'::date, '1 day')) as date) d
)
select * from calendar
order by date_id
