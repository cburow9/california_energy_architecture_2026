import pandas as pd


def standardize_fuel_type(df: pd.DataFrame, column: str = 'fuel_type') -> pd.DataFrame:
    df = df.copy()
    if column in df.columns:
        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
            .str.lower()
            .replace({
                'solar pv': 'solar',
                'wind energy': 'wind',
                'natural gas': 'gas',
            })
        )
    return df


def rename_columns(df: pd.DataFrame, mapping: dict) -> pd.DataFrame:
    return df.rename(columns=mapping)
