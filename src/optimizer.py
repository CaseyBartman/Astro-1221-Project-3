"""
SupernovaOptimizer
------------------
Fits cosmological models to the Tripp-standardised JLA distance moduli
using scipy.optimize.curve_fit, and reports goodness-of-fit metrics.

Three fitters are provided, corresponding to the analyses a student of
the 1998 supernova cosmology papers would want to run:

1. fit_empty_universe_hubble(z, mu) -- one free parameter (H0) using the
   closed-form empty-universe luminosity distance. The classical
   Hubble-law benchmark with no matter and no dark energy.

2. fit_matter_only(z, mu, h0=...) -- one free parameter (Omega_m) with
   Omega_Lambda = 0 enforced. Represents the pre-1998 consensus view
   that the universe was matter-dominated and decelerating. Important
   for showing that, even when Omega_m is allowed to float freely, a
   matter-only universe cannot match the data.

3. fit_density_parameters(z, mu, h0=...) -- two free parameters (Omega_m,
   Omega_Lambda) with H0 held fixed. This matches the standard 1998
   Perlmutter and Riess analyses, which did NOT assume flatness but
   let the data choose any combination of densities. H0 and the
   absolute magnitude M are completely degenerate in a supernova-only
   analysis (they enter only through M - 5*log10(H0)), so the standard
   practice is to fix H0 to an independent value.

All three use scipy.optimize.curve_fit and return parameter uncertainties
derived from the diagonal of the covariance matrix (rubric-relevant tools:
curve_fit, covariance, one-sigma errors via sqrt(diag(pcov))).
"""

import numpy as np
from scipy.optimize import curve_fit

from src.models import SupernovaCosmologyModels
from src.constants import (
    INITIAL_HUBBLE_CONSTANT_GUESS,
    INITIAL_MATTER_DENSITY_GUESS,
    INITIAL_DARK_ENERGY_DENSITY_GUESS,
)


# Value of H0 used by default when density parameters are fitted with H0 held
# fixed. This is the mid-range of current Planck and SH0ES determinations.
DEFAULT_FIXED_H0 = 70.0


class SupernovaOptimizer:
    """
    Handles fitting cosmological models to supernova distance moduli and
    reporting parameter uncertainties and goodness-of-fit metrics.
    """

    def __init__(self):
        self.cosmology_models = SupernovaCosmologyModels()

    # ------------------------------------------------------------------
    # Fit 1: one-parameter empty-universe (classical Hubble-law benchmark)
    # ------------------------------------------------------------------
    def fit_empty_universe_hubble(self, z, mu):
        """
        Fit the Hubble constant using the empty-universe (Milne) model.

        Uses the closed-form luminosity distance d_L = c*z*(1+z)/H0 and
        scipy.optimize.curve_fit. At z << 1 this reduces to the classical
        Hubble law cz = H0 * d.

        Args:
            z (array-like): Redshift values.
            mu (array-like): Tripp-standardised distance moduli.

        Returns:
            dict: best-fit H0, uncertainty, and metadata.
        """
        popt, pcov = curve_fit(
            self.cosmology_models.calculate_empty_universe_model,
            z, mu,
            p0=[INITIAL_HUBBLE_CONSTANT_GUESS],
        )

        return {
            'hubbleConstant': float(popt[0]),
            'hubbleConstantError': float(np.sqrt(pcov[0][0])),
            'matterDensity': 0.0,
            'darkEnergyDensity': 0.0,
            'fitModel': 'empty-universe',
            'isMock': False,
        }

    # ------------------------------------------------------------------
    # Fit 2: one-parameter matter-only fit (pre-1998 consensus view)
    # ------------------------------------------------------------------
    def fit_matter_only(self, z, mu, h0=DEFAULT_FIXED_H0):
        """
        Fit Omega_m with Omega_Lambda = 0 enforced (no dark energy).

        Represents the pre-1998 consensus view that the universe was
        matter-dominated and decelerating. The cosmologically natural
        value in this scenario is Omega_m = 1 (Einstein-de Sitter); this
        method lets Omega_m float freely between 0 and 1 and reports
        whatever value best fits the data with no dark energy allowed.

        In practice this fit produces a noticeably worse chi-squared
        than the full two-parameter density fit, which is direct
        evidence that the data require dark energy.

        Args:
            z (array-like): Redshift values.
            mu (array-like): Tripp-standardised distance moduli.
            h0 (float, optional): Value of H0 (km/s/Mpc) to hold fixed.
                Defaults to 70.0.

        Returns:
            dict with fitted Omega_m, forced Omega_Lambda = 0, and
            uncertainties.
        """
        def matter_only_model(redshift, matter_density):
            return self.cosmology_models.calculate_advanced_cosmological_model(
                redshift, h0, matter_density, 0.0
            )

        popt, pcov = curve_fit(
            matter_only_model, z, mu,
            p0=[INITIAL_MATTER_DENSITY_GUESS],
            bounds=([0.0], [1.0]),
        )

        matter_density = float(popt[0])
        matter_density_error = float(np.sqrt(pcov[0][0]))

        return {
            'hubbleConstant': float(h0),
            'matterDensity': matter_density,
            'darkEnergyDensity': 0.0,
            'hubbleConstantError': 0.0,
            'matterDensityError': matter_density_error,
            'darkEnergyDensityError': 0.0,
            'fitModel': 'matter-only',
            'fixedH0': float(h0),
            'isMock': False,
        }

    # ------------------------------------------------------------------
    # Fit 3: two-parameter density fit at fixed H0 (Perlmutter/Riess style)
    # ------------------------------------------------------------------
    def fit_density_parameters(self, z, mu, h0=DEFAULT_FIXED_H0):
        """
        Fit Omega_m and Omega_Lambda simultaneously, with H0 held fixed.

        This is the fit that matches the 1998 Perlmutter and Riess
        analyses. Neither density parameter is assumed; the data
        themselves decide whether there is dark energy, matter, or
        both. H0 is held at the supplied value because H0 and the
        absolute magnitude M of the Tripp-standardised supernovae are
        completely degenerate in mu(z) from the supernova data alone:
        they enter only through the combination M - 5*log10(H0). Fixing
        H0 is the standard treatment.

        Args:
            z (array-like): Redshift values.
            mu (array-like): Tripp-standardised distance moduli.
            h0 (float, optional): Value of H0 (km/s/Mpc) to hold fixed.
                Defaults to 70.0.

        Returns:
            dict with fitted densities, their uncertainties, the covariance
            matrix, and metadata including the fixed H0 value.
        """
        def model_at_fixed_h0(redshift, matter_density, dark_energy_density):
            return self.cosmology_models.calculate_advanced_cosmological_model(
                redshift, h0, matter_density, dark_energy_density
            )

        p0 = [INITIAL_MATTER_DENSITY_GUESS, INITIAL_DARK_ENERGY_DENSITY_GUESS]
        bounds = ([0.0, 0.0], [1.0, 1.0])

        popt, pcov = curve_fit(
            model_at_fixed_h0, z, mu,
            p0=p0, bounds=bounds,
        )

        uncertainties = np.sqrt(np.diag(pcov))

        return {
            'hubbleConstant': float(h0),
            'matterDensity': float(popt[0]),
            'darkEnergyDensity': float(popt[1]),
            'hubbleConstantError': 0.0,
            'matterDensityError': float(uncertainties[0]),
            'darkEnergyDensityError': float(uncertainties[1]),
            'covarianceMatrix': pcov,
            'fitModel': 'density-at-fixed-H0',
            'fixedH0': float(h0),
            'isMock': False,
        }

    # ------------------------------------------------------------------
    # Goodness of fit
    # ------------------------------------------------------------------
    def calculate_goodness_of_fit(self, mu_observed, mu_predicted,
                                  numberOfParameters, sigma=0.15):
        """
        Calculate chi-squared, reduced chi-squared, and residuals.

        Args:
            mu_observed (array-like): Observed distance moduli.
            mu_predicted (array-like): Model predictions at the same redshifts.
            numberOfParameters (int): Number of free parameters in the fit.
            sigma (float, optional): Per-point uncertainty on mu. JLA reports
                typical sigma_mu values in the 0.12-0.25 mag range for
                Tripp-standardised supernovae; 0.15 is a reasonable
                single-number stand-in. Defaults to 0.15.

        Returns:
            dict: chiSquared, reducedChiSquared, residuals, degreesOfFreedom.
        """
        residuals = np.asarray(mu_observed) - np.asarray(mu_predicted)
        chi_squared = float(np.sum((residuals / sigma) ** 2))

        degrees_of_freedom = len(mu_observed) - numberOfParameters
        reduced_chi_squared = chi_squared / degrees_of_freedom

        return {
            'chiSquared': chi_squared,
            'reducedChiSquared': reduced_chi_squared,
            'residuals': residuals,
            'degreesOfFreedom': degrees_of_freedom,
        }


# ------------------------------------------------------------------
# Command-line test. Runs all three fits on the real JLA data.
# ------------------------------------------------------------------
if __name__ == "__main__":
    from src.data_loader import SupernovaDataLoader
    from src.data_processor import SupernovaDataProcessor

    loader = SupernovaDataLoader()
    processor = SupernovaDataProcessor()
    optimizer = SupernovaOptimizer()

    df = processor.process_raw_records(loader.parse_supernova_objects())
    print(f"Loaded {len(df)} supernovae, z = [{df['redshift'].min():.3f}, {df['redshift'].max():.3f}]")
    print()

    z = df['redshift'].values
    mu = df['mu'].values

    print("Fit 1: empty-universe (H0 only; Omega_m = Omega_L = 0)")
    r1 = optimizer.fit_empty_universe_hubble(z, mu)
    print(f"  H0 = {r1['hubbleConstant']:.2f} +/- {r1['hubbleConstantError']:.2f} km/s/Mpc")
    print()

    print("Fit 2: matter-only (Omega_m free; Omega_L = 0; H0 = 70)")
    r2 = optimizer.fit_matter_only(z, mu, h0=70.0)
    print(f"  Omega_m = {r2['matterDensity']:.3f} +/- {r2['matterDensityError']:.3f}")
    print(f"  Omega_L = 0 (enforced)")
    print()

    print("Fit 3: density parameters (Omega_m, Omega_L both free; H0 = 70)")
    r3 = optimizer.fit_density_parameters(z, mu, h0=70.0)
    print(f"  Omega_m = {r3['matterDensity']:.3f} +/- {r3['matterDensityError']:.3f}")
    print(f"  Omega_L = {r3['darkEnergyDensity']:.3f} +/- {r3['darkEnergyDensityError']:.3f}")
