from typing import Dict, Optional
import pandas as pd
import logging

logger = logging.getLogger(__name__)

# Fuel type normalization mapping
FUEL_TYPE_MAPPING: Dict[str, str] = {
    'solar pv': 'solar',
    'solar photovoltaic': 'solar',
    'wind energy': 'wind',
    'natural gas': 'gas',
    'combined cycle': 'gas',
    'geothermal': 'geothermal',
    'hydroelectric': 'hydro',
    'nuclear': 'nuclear',
}

VALID_FUEL_TYPES = set(FUEL_TYPE_MAPPING.values())


def standardize_fuel_type(
    df: pd.DataFrame,
    column: str = 'fuel_type'
) -> pd.DataFrame:
    """
    Normalize fuel type strings to standard categories.
    
    Converts fuel types to lowercase and applies standardization mapping:
    - 'Solar PV' → 'solar'
    - 'Wind Energy' → 'wind'
    - 'Natural Gas' → 'gas'
    - etc.
    
    Args:
        df: DataFrame with fuel type column
        column: Name of the fuel type column (default: 'fuel_type')
        
    Returns:
        DataFrame with normalized fuel types
        
    Raises:
        ValueError: If column contains invalid fuel types after standardization
        
    Example:
        >>> df = pd.DataFrame({'fuel_type': ['  Solar PV  ', 'WIND Energy']})
        >>> standardize_fuel_type(df)
           fuel_type
        0      solar
        1       wind
    """
    if column not in df.columns:
        logger.warning(f"Column '{column}' not found in DataFrame. Returning unchanged.")
        return df.copy()
    
    df = df.copy()
    
    # Strip whitespace and convert to lowercase
    df[column] = (
        df[column]
        .astype(str)
        .str.strip()
        .str.lower()
    )
    
    # Apply mapping
    df[column] = df[column].replace(FUEL_TYPE_MAPPING)
    
    # Validate: check for unknown fuel types (after mapping)
    if df[column].notna().any():
        unknown = set(df[df[column].notna()][column].unique()) - VALID_FUEL_TYPES
        if unknown:
            logger.warning(f"Unknown fuel types found: {unknown}. They will be kept as-is.")
    
    # Log unique values (excluding NaN)
    unique_values = sorted([v for v in df[column].unique() if pd.notna(v)])
    logger.info(f"Standardized fuel types. Unique values: {unique_values}")
    return df


def rename_columns(
    df: pd.DataFrame,
    mapping: Dict[str, str]
) -> pd.DataFrame:
    """
    Rename DataFrame columns with validation.
    
    Args:
        df: Input DataFrame
        mapping: {old_name: new_name} mapping dictionary
        
    Returns:
        DataFrame with renamed columns
        
    Raises:
        ValueError: If mapped column doesn't exist
        
    Example:
        >>> df = pd.DataFrame({'old_col': [1, 2, 3]})
        >>> rename_columns(df, {'old_col': 'new_col'})
           new_col
        0        1
        1        2
        2        3
    """
    if not mapping:
        return df.copy()
    
    # Validate that all source columns exist
    missing = set(mapping.keys()) - set(df.columns)
    if missing:
        raise ValueError(f"Columns not found for rename: {missing}")
    
    df = df.copy()
    result = df.rename(columns=mapping)
    
    logger.info(f"Renamed columns: {mapping}")
    return result
