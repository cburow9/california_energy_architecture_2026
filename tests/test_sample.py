import pytest
import pandas as pd
from src.preprocessing.data_transforms import (
    standardize_fuel_type,
    rename_columns,
    FUEL_TYPE_MAPPING,
    VALID_FUEL_TYPES
)


class TestStandardizeFuelType:
    """Test suite for fuel type standardization."""
    
    @pytest.fixture
    def sample_df(self):
        """Fixture: DataFrame with various fuel type formats."""
        return pd.DataFrame({
            'fuel_type': [
                '  Solar PV  ',
                'WIND ENERGY',
                'natural gas',
                'Hydroelectric',
                'Solar Photovoltaic',
                'Combined Cycle'
            ],
            'generation_mw': [100, 250, 500, 150, 200, 300]
        })
    
    def test_standardize_fuel_type_basic(self, sample_df):
        """Test basic normalization: whitespace, case, and mapping."""
        result = standardize_fuel_type(sample_df, 'fuel_type')
        expected = ['solar', 'wind', 'gas', 'hydro', 'solar', 'gas']
        assert result['fuel_type'].tolist() == expected
    
    def test_standardize_fuel_type_idempotence(self, sample_df):
        """Test that applying standardization twice yields same result."""
        result1 = standardize_fuel_type(sample_df, 'fuel_type')
        result2 = standardize_fuel_type(result1, 'fuel_type')
        assert result1['fuel_type'].equals(result2['fuel_type'])
    
    def test_standardize_fuel_type_missing_column(self):
        """Test handling of missing column - should return DataFrame unchanged."""
        df = pd.DataFrame({'other_col': [1, 2, 3]})
        result = standardize_fuel_type(df, 'fuel_type')
        assert result.equals(df)
        assert 'fuel_type' not in result.columns
    
    def test_standardize_fuel_type_with_nulls(self):
        """Test handling of NULL values in fuel_type column."""
        df = pd.DataFrame({
            'fuel_type': ['solar pv', None, 'wind energy', pd.NA],
            'generation_mw': [100, 200, 300, 400]
        })
        result = standardize_fuel_type(df, 'fuel_type')
        assert result['fuel_type'].tolist()[0] == 'solar'
        assert pd.isna(result['fuel_type'].tolist()[1])
        assert result['fuel_type'].tolist()[2] == 'wind'
    
    def test_standardize_fuel_type_preserves_other_columns(self):
        """Test that standardization doesn't affect other columns."""
        df = pd.DataFrame({
            'fuel_type': ['solar pv', 'wind energy'],
            'generation_mw': [100, 250],
            'facility_id': ['FAC001', 'FAC002']
        })
        result = standardize_fuel_type(df, 'fuel_type')
        assert result['generation_mw'].tolist() == [100, 250]
        assert result['facility_id'].tolist() == ['FAC001', 'FAC002']
    
    def test_standardize_fuel_type_unknown_values(self, caplog):
        """Test warning on unknown fuel types."""
        df = pd.DataFrame({
            'fuel_type': ['solar pv', 'unknown_type'],
            'generation_mw': [100, 250]
        })
        result = standardize_fuel_type(df, 'fuel_type')
        assert result['fuel_type'].tolist()[0] == 'solar'
        assert result['fuel_type'].tolist()[1] == 'unknown_type'  # Kept as-is


class TestRenameColumns:
    """Test suite for column renaming."""
    
    @pytest.fixture
    def sample_df(self):
        """Fixture: Sample DataFrame."""
        return pd.DataFrame({
            'old_col1': [1, 2, 3],
            'old_col2': ['a', 'b', 'c'],
            'keep_col': [10, 20, 30]
        })
    
    def test_rename_columns_basic(self, sample_df):
        """Test basic column renaming."""
        mapping = {'old_col1': 'new_col1', 'old_col2': 'new_col2'}
        result = rename_columns(sample_df, mapping)
        assert 'new_col1' in result.columns
        assert 'new_col2' in result.columns
        assert 'old_col1' not in result.columns
        assert 'keep_col' in result.columns  # Unmapped column preserved
    
    def test_rename_columns_empty_mapping(self, sample_df):
        """Test with empty mapping - should return unchanged."""
        result = rename_columns(sample_df, {})
        assert result.equals(sample_df)
    
    def test_rename_columns_missing_column_raises_error(self, sample_df):
        """Test that renaming non-existent column raises ValueError."""
        mapping = {'nonexistent_col': 'new_name'}
        with pytest.raises(ValueError, match="Columns not found for rename"):
            rename_columns(sample_df, mapping)
    
    def test_rename_columns_preserves_data(self, sample_df):
        """Test that renaming preserves all data and dtypes."""
        mapping = {'old_col1': 'new_col1'}
        result = rename_columns(sample_df, mapping)
        assert result['new_col1'].tolist() == [1, 2, 3]
        assert result['new_col1'].dtype == sample_df['old_col1'].dtype


class TestDataIntegration:
    """Integration tests for data transformation pipeline."""
    
    def test_standardize_then_rename(self):
        """Test pipeline: standardize fuel type then rename columns."""
        df = pd.DataFrame({
            'source_type': ['  Solar PV  ', 'WIND ENERGY'],
            'capacity': [100, 250]
        })
        
        # Step 1: Standardize
        df = standardize_fuel_type(df, 'source_type')
        assert df['source_type'].tolist() == ['solar', 'wind']
        
        # Step 2: Rename
        df = rename_columns(df, {'source_type': 'fuel_type', 'capacity': 'generation_mw'})
        assert 'fuel_type' in df.columns
        assert 'generation_mw' in df.columns
        assert df['fuel_type'].tolist() == ['solar', 'wind']
