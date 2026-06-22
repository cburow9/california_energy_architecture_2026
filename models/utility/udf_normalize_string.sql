{% macro normalize_string(value) %}
    lower(regexp_replace(trim({{ value }}), '[^a-zA-Z0-9 ]+', '', 'g'))
{% endmacro %}
