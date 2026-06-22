{{ config(
    materialized='table',
    on_schema_change='fail'
) }}

with raw_sources as (
    select
        source_id,
        source_name,
        fuel_type,
        generation_mw,
        report_date,
        row_number() over (
            partition by source_id, report_date
            order by current_timestamp() desc
        ) as rn
    from {{ source('google_public', 'california_energy_supply') }}
)

select
    source_id,
    source_name,
    lower(fuel_type) as fuel_type,
    generation_mw,
    cast(report_date as date) as report_date
from raw_sources
where source_id is not null
  and rn = 1  -- Deduplicate: keep only latest record per source per date
