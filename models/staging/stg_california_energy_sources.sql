{{ config(materialized='view') }}

with raw_sources as (
    select
        source_id,
        source_name,
        fuel_type,
        generation_mw,
        report_date
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
