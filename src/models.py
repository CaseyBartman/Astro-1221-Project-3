import numpy as np
from scipy.integrate import quad
from src.constants import (
    SPEED_OF_LIGHT_KM_S,
    DISTANCE_MODULUS_LOG_MULTIPLIER,
    DISTANCE_MODULUS_OFFSET,
    TRIPP_ALPHA,
    TRIPP_BETA,
    ABSOLUTE_MAGNITUDE_M
)

class SupernovaCosmologyModels:
    """
    Implements the standardizations and theoretical distance modulus 
    calculations for evaluating the expanding universe.

    This class handles the core astrophysics required to prove cosmic acelleration.
    It provides methods to standardize Type Ia Supernovae into reliable 
    standard candles and compares their observed distances against 
    theoretical models of universe expansion.

    See the scientific bibliography in README.MD for more sources on the formulas 
    implemented here and their matching citations. We could have just used a scipy
    package to implement these models and formulas for us, but that defeats the 
    entire purpose of the project. 
    """

    def calculate_distance_modulus(self, observedMagnitude, stretchFactor, colorValue):
        """
        Standardizes raw telescope data to calculate the true distance modulus.

        This applies the empirical Tripp Relation to correct the apparent
        magnitude based on the light curve's stretch and color characteristics.

        Args:
            observedMagnitude (float | pd.Series): The raw apparent magnitude observed.
            stretchFactor (float | pd.Series): The width/stretch of the light curve.
            colorValue (float | pd.Series): The B-V color index measurement.

        Returns:
            float | pd.Series: The standardized distance modulus (mu).
        """
        # FORMULA: mu = m + (alpha * s) - (beta * c) - M
        # Where m is magnitude, s is stretch, c is color, and M is absolute magnitude.
        stretchCorrection = TRIPP_ALPHA * stretchFactor
        colorCorrection = TRIPP_BETA * colorValue
        
        standardizedModulus = observedMagnitude + stretchCorrection - colorCorrection - ABSOLUTE_MAGNITUDE_M
        return standardizedModulus

    def calculate_simple_hubble_model(self, redshiftValues, hubbleConstant):
        """
        Calculates theoretical distance modulus using the low-redshift linear approximation.

        Args:
            redshiftValues (float | pd.Series): The measured redshift (z) of the supernovae.
            hubbleConstant (float): The Hubble constant (H0) in km/s/Mpc to test.

        Returns:
            float | pd.Series: The theoretical distance modulus predicted by a linear universe.
        """
        # FORMULA: d_L = (c * z) / H_0
        # Where c is the speed of light, z is redshift, and H_0 is the Hubble constant.
        luminosityDistanceMpc = (SPEED_OF_LIGHT_KM_S * redshiftValues) / hubbleConstant
        
        # FORMULA: mu = 5 * log10(d_L) + 25
        return self._convert_distance_to_modulus(luminosityDistanceMpc)

    def calculate_advanced_cosmological_model(self, redshiftValues, hubbleConstant, matterDensity, darkEnergyDensity):
        """
        Calculates distance modulus by integrating over dark energy and matter density.

        Args:
            redshiftValues (float | pd.Series): The measured redshift (z).
            hubbleConstant (float): The Hubble constant (H0) in km/s/Mpc.
            matterDensity (float): The dimensionless matter density parameter (Omega_m).
            darkEnergyDensity (float): The dimensionless dark energy density (Omega_Lambda).

        Returns:
            float | pd.Series: The theoretical distance modulus for an accelerating universe.
        """
        vectorized_distance_calculator = np.vectorize(self._calculate_single_luminosity_distance)
        
        luminosityDistancesMpc = vectorized_distance_calculator(
            redshiftValues, hubbleConstant, matterDensity, darkEnergyDensity
        )
        
        return self._convert_distance_to_modulus(luminosityDistancesMpc)

    # ---------------------------------------------------------
    # Private Helper Functions (Stepdown Rule)
    # ---------------------------------------------------------

    def _convert_distance_to_modulus(self, luminosityDistanceMpc):
        """Converts a physical distance in Megaparsecs to a logarithmic distance modulus."""
        logarithmicDistance = np.log10(luminosityDistanceMpc)
        return (DISTANCE_MODULUS_LOG_MULTIPLIER * logarithmicDistance) + DISTANCE_MODULUS_OFFSET

    def _calculate_single_luminosity_distance(self, singleRedshift, hubbleConstant, matterDensity, darkEnergyDensity):
        """Handles the scipy integration of the expansion factor for a single redshift value."""
        integralResult, _integrationError = quad(
            self._inverse_expansion_factor,
            0, 
            singleRedshift, 
            args=(matterDensity, darkEnergyDensity)
        )
        
        # FORMULA: d_L = [ c * (1 + z) / H_0 ] * integral from 0 to z ( dz' / E(z))
        leadingFactor = (SPEED_OF_LIGHT_KM_S * (1.0 + singleRedshift)) / hubbleConstant
        return leadingFactor * integralResult

    def _inverse_expansion_factor(self, integrationVariableZ, matterDensity, darkEnergyDensity):
        """Calculates 1/E(z), the integrand representing the inverse of the universe's expansion rate."""
        # FORMULA: E(z) = sqrt( Omega_m * (1 + z)^3 + Omega_Lambda )
        matterComponent = matterDensity * ((1.0 + integrationVariableZ) ** 3.0)
        expansionFactorSquared = matterComponent + darkEnergyDensity
        
        return 1.0 / np.sqrt(expansionFactorSquared)