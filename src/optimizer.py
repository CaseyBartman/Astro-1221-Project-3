import pandas as pd
from scipy.optimize import curve_fit
from models import SupernovaCosmologyModels
from constants import INITIAL_HUBBLE_CONSTANT_GUESS, INITIAL_MATTER_DENSITY_GUESS

class SupernovaOptimizer:
    """
    Handles fitting the cosmological models to the cleaned data using scipy.optimize,
    and calculating goodness-of-fit metrics.
    """

    def __init__(self):
        self.cosmology_models = SupernovaCosmologyModels()

    def fit_simple_hubble_model(self, redshiftValues, actualDistanceModuli):
        """
        Uses curve_fit to find the optimal Hubble Constant for the simple model.
        
        Args:
            redshiftValues (pd.Series): The x-axis data.
            actualDistanceModuli (pd.Series): The y-axis data (standardized by Groupmate 1).
            
        Returns:
            dict: Contains 'hubbleConstant' and 'uncertainty' keys.
            
        Note to Groupmate 2:
        Use the constants.py file for your p0 (initial guesses). No magic values!
        """
        # TODO: Wrap scipy.optimize.curve_fit passing self.cosmology_models.calculate_simple_hubble_model --- ive changed it to calculate_empty_univesre_model
        pass

    def fit_advanced_cosmological_model(self, redshiftValues, actualDistanceModuli):
        """
        Fits multiple parameters (H0, Omega_m, Omega_Lambda) using the advanced model.
        
        Returns:
            dict: Contains fitted parameters and their covariance matrix.
        """
        # TODO: Implement multi-parameter optimization here.
        pass

    def calculate_goodness_of_fit(self, actualDistanceModuli, predictedDistanceModuli, numberOfParameters):
        """
        Calculates the Chi-Squared value and generates the residuals.
        
        Args:
            actualDistanceModuli (pd.Series): The true data points.
            predictedDistanceModuli (pd.Series): The model's line of best fit.
            numberOfParameters (int): Used to calculate degrees of freedom.
            
        Returns:
            dict: Contains 'chiSquaredValue', 'reducedChiSquared', and a pd.Series of 'residuals'.
            
        Note to Groupmate 2:
        Keep logic flat. If branching is needed (e.g., checking if lengths match), 
        move that logic to a helper function.
        """
        # TODO: Calculate Chi-squared and residuals array.
        pass