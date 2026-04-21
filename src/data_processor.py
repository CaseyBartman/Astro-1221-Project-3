import pandas as pd
from src.constants import NUMERICAL_PHYSICS_COLUMNS
from src.models import SupernovaCosmologyModels

class SupernovaDataProcessor:
    """
    Transforms raw parsed Supernova dictionaries into a cleaned, strongly-typed Pandas DataFrame.
    """

    def __init__(self):
        self.cosmology_models = SupernovaCosmologyModels()

    def process_raw_records(self, raw_supernova_records):
        """Executes the data cleaning pipeline top-to-bottom."""
        try:
            supernova_dataframe = self._convert_to_dataframe(raw_supernova_records)
            supernova_dataframe = self._cast_numerical_columns(supernova_dataframe)
            supernova_dataframe = self._remove_invalid_measurements(supernova_dataframe)
            return self._calculate_distance_modulus(supernova_dataframe)

        except Exception as processingError:
            # Re-raise with a clear narrative for the Streamlit UI to display
            raise RuntimeError(f"Data processing pipeline failed: {str(processingError)}") from processingError

    def _convert_to_dataframe(self, raw_records):
        """Converts the list of dictionaries into a Pandas DataFrame."""
        if not raw_records or not isinstance(raw_records, list):
            raise ValueError("Raw records payload is empty or not a valid list.")
            
        return pd.DataFrame(raw_records)

    def _cast_numerical_columns(self, dataframe):
        """Casts physical measurements from strings/objects to floats."""
        try:
            for column in NUMERICAL_PHYSICS_COLUMNS:
                dataframe[column] = pd.to_numeric(dataframe[column], errors='coerce')
            return dataframe
            
        except KeyError as missingColumnError:
            raise KeyError(f"Expected physics column is missing from data: {str(missingColumnError)}")

    def _remove_invalid_measurements(self, dataframe):
        """Drops rows where critical physical measurements failed to parse or are missing."""
        try:
            has_valid_data = dataframe.dropna(subset=NUMERICAL_PHYSICS_COLUMNS)
            return has_valid_data
            
        except KeyError as missingColumnError:
            raise KeyError(f"Cannot drop invalid rows. Missing subset column: {str(missingColumnError)}")

    def _calculate_distance_modulus(self, dataframe):
        """
        Apply the Tripp relation to convert raw observables into distance moduli.

        The Tripp standardization uses the light-curve stretch and color
        parameters to correct the observed peak magnitude, turning the raw
        apparent magnitude into a true distance modulus:

            mu = m_B + alpha * (stretch - 1) - beta * color - M

        This is implemented inside SupernovaCosmologyModels.calculate_distance_modulus
        rather than duplicating the formula here, so there is a single source of
        truth for the physics.

        Args:
            dataframe (pd.DataFrame): Frame with columns 'magnitude', 'stretch',
                                      and 'color' already cast to numeric.

        Returns:
            pd.DataFrame: The input frame with an added 'mu' column.
        """
        dataframe = dataframe.copy()
        dataframe['mu'] = self.cosmology_models.calculate_distance_modulus(
            dataframe['magnitude'],
            dataframe['stretch'],
            dataframe['color'],
        )
        return dataframe
