{%- set partitions = {
    'field': 'last_report_date',
    'data_type': 'date',
    'granularity': 'month'
} -%}

{{ config(
    materialized='table',
    partition_by=partitions,
    cluster_by=['fuel_type'],
    require_partition_filter=true
) }}

with staging as (
    select *
    from {{ ref('stg_california_energy_sources') }}
)

select
    fuel_type,
    count(distinct source_id) as source_count,
    sum(generation_mw) as total_generation_mw,
    min(report_date) as first_report_date,
    max(report_date) as last_report_date
from staging
group by fuel_type
