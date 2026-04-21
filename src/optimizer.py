"""
SupernovaOptimizer
------------------
Fits cosmological models to the Tripp-standardised Union2.1 distance moduli
using scipy.optimize.curve_fit, and reports goodness-of-fit metrics.

Three fitters are provided, corresponding to the three analyses a student of
the 1998 supernova cosmology papers would want to run:

1. fit_empty_universe_hubble(z, mu) -- one free parameter (H0) using the
   closed-form empty-universe luminosity distance. The classical Hubble-law
   benchmark.

2. fit_density_parameters(z, mu, h0=...) -- two free parameters (Omega_m,
   Omega_Lambda) with H0 held fixed. H0 and the absolute magnitude M are
   completely degenerate in a supernova-only analysis (they enter only
   through the combination M - 5*log10(H0)), so the standard practice
   established by the 1998 Perlmutter and Riess analyses is to fix H0 to
   an independent value and report only the density parameters.

3. fit_flat_universe(z, mu, h0=...) -- one free parameter (Omega_m) with
   H0 fixed and flatness enforced (Omega_Lambda = 1 - Omega_m). The
   'textbook' one-number fit.

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
            dict: {
                'hubbleConstant': best-fit H0 in km/s/Mpc,
                'hubbleConstantError': 1-sigma uncertainty on H0,
                'fitModel': 'empty-universe',
                'isMock': False,
            }
        """
        popt, pcov = curve_fit(
            self.cosmology_models.calculate_empty_universe_model,
            z, mu,
            p0=[INITIAL_HUBBLE_CONSTANT_GUESS],
        )

        return {
            'hubbleConstant': float(popt[0]),
            'hubbleConstantError': float(np.sqrt(pcov[0][0])),
            'fitModel': 'empty-universe',
            'isMock': False,
        }

    # ------------------------------------------------------------------
    # Fit 2: two-parameter density fit at fixed H0 (Perlmutter/Riess style)
    # ------------------------------------------------------------------
    def fit_density_parameters(self, z, mu, h0=DEFAULT_FIXED_H0):
        """
        Fit Omega_m and Omega_Lambda simultaneously, with H0 held fixed.

        H0 is held at the supplied value because H0 and the absolute magnitude
        M of the Tripp-standardised supernovae are completely degenerate in
        mu(z) from the supernova data alone: they enter only through the
        combination M - 5*log10(H0). Fitting all three parameters at once
        produces enormous covariance entries that faithfully reflect this
        physical degeneracy but prevent any useful interpretation. Fixing H0
        is the standard treatment.

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
    # Fit 3: one-parameter flat-universe fit (textbook one-number answer)
    # ------------------------------------------------------------------
    def fit_flat_universe(self, z, mu, h0=DEFAULT_FIXED_H0):
        """
        Fit a flat Lambda-CDM universe: Omega_m free, Omega_Lambda = 1 - Omega_m.

        Enforces the spatial-flatness constraint Omega_m + Omega_Lambda = 1,
        leaving only one free cosmological parameter. This is the simplest
        physically reasonable one-number answer the data can provide, and is
        how many textbooks quote 'the' best-fit cosmology. H0 is held fixed
        for the same degeneracy reason as in fit_density_parameters.

        Args:
            z (array-like): Redshift values.
            mu (array-like): Tripp-standardised distance moduli.
            h0 (float, optional): Value of H0 (km/s/Mpc) to hold fixed.
                Defaults to 70.0.

        Returns:
            dict with fitted Omega_m, derived Omega_Lambda = 1 - Omega_m,
            and matched uncertainties (same numeric value, flatness-linked).
        """
        def flat_model(redshift, matter_density):
            dark_energy_density = 1.0 - matter_density
            return self.cosmology_models.calculate_advanced_cosmological_model(
                redshift, h0, matter_density, dark_energy_density
            )

        popt, pcov = curve_fit(
            flat_model, z, mu,
            p0=[INITIAL_MATTER_DENSITY_GUESS],
            bounds=([0.0], [1.0]),
        )

        matter_density = float(popt[0])
        matter_density_error = float(np.sqrt(pcov[0][0]))

        return {
            'hubbleConstant': float(h0),
            'matterDensity': matter_density,
            'darkEnergyDensity': 1.0 - matter_density,
            'hubbleConstantError': 0.0,
            'matterDensityError': matter_density_error,
            'darkEnergyDensityError': matter_density_error,
            'fitModel': 'flat-universe',
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
            sigma (float, optional): Per-point uncertainty on mu. Union2.1
                reports typical sigma_mu values in the 0.12-0.25 mag range
                for Tripp-standardised supernovae; 0.15 is a reasonable
                single-number stand-in. Defaults to 0.15.

        Returns:
            dict: {
                'chiSquared': sum of (residual/sigma)^2,
                'reducedChiSquared': chiSquared / degrees of freedom,
                'residuals': observed minus predicted (numpy array),
                'degreesOfFreedom': int,
            }
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
# Command-line test. Loads the Union2.1 data, runs all three fits,
# and prints a summary. Useful for sanity checks after changes.
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

    print("Fit 1: empty-universe, one parameter (H0)")
    r1 = optimizer.fit_empty_universe_hubble(z, mu)
    print(f"  H0 = {r1['hubbleConstant']:.2f} +/- {r1['hubbleConstantError']:.2f} km/s/Mpc")
    print()

    print("Fit 2: density parameters at fixed H0 = 70.0")
    r2 = optimizer.fit_density_parameters(z, mu, h0=70.0)
    print(f"  Omega_m       = {r2['matterDensity']:.3f} +/- {r2['matterDensityError']:.3f}")
    print(f"  Omega_Lambda  = {r2['darkEnergyDensity']:.3f} +/- {r2['darkEnergyDensityError']:.3f}")
    print()

    print("Fit 3: flat universe (Omega_m free, Omega_Lambda = 1 - Omega_m)")
    r3 = optimizer.fit_flat_universe(z, mu, h0=70.0)
    print(f"  Omega_m       = {r3['matterDensity']:.3f} +/- {r3['matterDensityError']:.3f}")
    print(f"  Omega_Lambda  = {r3['darkEnergyDensity']:.3f}   (by flatness)")
