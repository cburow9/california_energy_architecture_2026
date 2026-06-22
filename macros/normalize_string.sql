{% macro normalize_string(value) %}
    lower(regexp_replace(trim({{ value }}), r'[^a-zA-Z0-9 ]+', '', 'g'))
{% endmacro %}
