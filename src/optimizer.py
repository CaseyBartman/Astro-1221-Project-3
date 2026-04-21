import pandas as pd
import numpy as np
from requests import models
from scipy.optimize import curve_fit
from src.models import SupernovaCosmologyModels
from src.constants import INITIAL_HUBBLE_CONSTANT_GUESS, INITIAL_MATTER_DENSITY_GUESS

class SupernovaOptimizer:
    """
    Handles fitting the cosmological models to the cleaned data using scipy.optimize,
    and calculating goodness-of-fit metrics.
    """

    def __init__(self):
        self.cosmology_models = SupernovaCosmologyModels()

    def fit_simple_hubble_model(self, z, mu):
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
        popt, pcov = curve_fit(self.cosmology_models.calculate_empty_universe_model, z, mu, p0=[INITIAL_HUBBLE_CONSTANT_GUESS])

        return {'hubbleConstant': popt[0], 'uncertainty': np.sqrt(pcov[0][0])}

    def fit_advanced_cosmological_model(self, z, mu, h0 = 73.35):
        """
        Fits multiple parameters omega_m, Omega_lambda using the advanced model holding h0 constant for optimization reasons
        
        Returns:
            dict: Contains fitted parameters and their covariance matrix.
        """
        def fixed_h0_wrapper(z_val, matterdensity, darkenergydensity):
            return self.cosmology_models.calculate_advanced_cosmological_model(z_val, h0, matterdensity, darkenergydensity)
        # p0: Initial guesses [H0, Omega_m, Omega_Lambda]
        # Starting with the 'Consensus' universe: 70, 0.3, 0.7
        p0 = [0.3, 0.7]  
        # bounds: ([min_H0, min_Om, min_Ol], [max_H0, max_Om, max_Ol])
        # Keeps the math within physically 'sane' limits
        bounds = ([0.0, 0.7], [1.0, 1.5])
        # DEBUG CHECK
        popt, pcov = curve_fit(fixed_h0_wrapper, z, mu, p0=p0, bounds=bounds)
        percent = np.sqrt(np.diag(pcov))
        return {'hubbleConstant': h0,
        'matterDensity': popt[0], 
        'darkEnergyDensity': popt[1],
         'uncertainties': {'H0_error':0.0,
         '0m_error': percent[0],
          '0l_error': percent[1]},
        'covariance_matrix': pcov}


    def calculate_goodness_of_fit(self, mu, predicteddistanceModuli, numberOfParameters):
        """
        Calculates the Chi-Squared value and generates the residuals.
        
        Args:
            actualDistanceModuli (pd.Series): The true data points.
            luminosityDistancesMpc (pd.Series): Luminosity distances (Mpc) predicted by a cosmology model.
            numberOfParameters (int): Used to calculate degrees of freedom.
            
        Returns:
            dict: Contains 'chiSquaredValue', 'reducedChiSquared', and a pd.Series of 'residuals'.
            
        Note to Groupmate 2:
        Keep logic flat. If branching is needed (e.g., checking if lengths match), 
        move that logic to a helper function.
        """
        residuals = mu - predicteddistanceModuli
        sigma = .3
        chisq = np.sum((residuals**2) / (sigma**2))

        degrees_of_freedom = len(mu) - numberOfParameters
        reducedchisq = chisq / degrees_of_freedom
        return {
            'predictedDistanceModuli': predicteddistanceModuli,
            'chisquaredvalue': chisq,
            'reducedchisq': reducedchisq,
            'residuals': residuals
        }
       
        

#testing code for running in terminal 
if __name__ == "__main__":
    from src.constants import INITIAL_HUBBLE_CONSTANT_GUESS
    import numpy as np
    
    # 1. Initialize
    opt = SupernovaOptimizer()
    print(f"Initial Guess: {INITIAL_HUBBLE_CONSTANT_GUESS}")

    # 2. Create some dummy 'test' data to make sure the math works
    z_test = np.array([0.01, 0.05, 0.1])
    mu_test = np.array([33.0, 36.5, 38.5])

    # 3. Run the fit
    try:
        results = opt.fit_simple_hubble_model(z_test, mu_test)
        print(f"Optimized H0: {results['hubbleConstant']:.4f}")
        print(f"Uncertainty:  {results['uncertainty']:.4f}")
    except Exception as e:
        print(f"Fit failed: {e}")