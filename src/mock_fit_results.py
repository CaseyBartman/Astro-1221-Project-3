"""
Mock fit results for development use before the optimizer is complete.

This module provides placeholder values with the same shape and keys as the
results the real ``SupernovaOptimizer`` in ``optimizer.py`` will return once
implemented. The Streamlit app imports from this file so that the interface
can be developed and tested in parallel with the fitting code.

TO SWAP IN REAL RESULTS:
    Once ``optimizer.py`` is complete, replace the ``get_mock_fit_results()``
    function's return value with a call to the real fitter. For example::

        from src.optimizer import SupernovaOptimizer
        optimizer = SupernovaOptimizer()
        results = optimizer.fit_advanced_cosmological_model(z, mu)

"""

import numpy as np


def get_mock_fit_results():
    """
    Return a dictionary matching the structure of the future real fit output.

    Keys match what the finished ``fit_advanced_cosmological_model`` method
    will return: fitted parameters, their 1-sigma uncertainties, a covariance
    matrix, and a status flag indicating that the values are mock data.

    Returns
    -------
    dict
        Fit results with the following keys:

        ``hubbleConstant`` (float): H0 in km/s/Mpc.
        ``matterDensity`` (float): Omega_m (dimensionless).
        ``darkEnergyDensity`` (float): Omega_Lambda (dimensionless).
        ``hubbleConstantError`` (float): 1-sigma uncertainty on H0.
        ``matterDensityError`` (float): 1-sigma uncertainty on Omega_m.
        ``darkEnergyDensityError`` (float): 1-sigma uncertainty on Omega_Lambda.
        ``covarianceMatrix`` (np.ndarray): 3x3 parameter covariance.
        ``isMock`` (bool): Always ``True`` for this module. The real fitter
            should return ``False`` here so the UI can badge mock vs. real.
    """
    return {
        "hubbleConstant": 70.0,
        "matterDensity": 0.30,
        "darkEnergyDensity": 0.70,
        "hubbleConstantError": 2.5,
        "matterDensityError": 0.05,
        "darkEnergyDensityError": 0.05,
        "covarianceMatrix": np.array([
            [6.25, 0.00, 0.00],
            [0.00, 0.0025, -0.0015],
            [0.00, -0.0015, 0.0025],
        ]),
        "isMock": True,
    }


def get_simple_hubble_mock():
    """
    Return mock results for the low-z (empty-universe) linear fit.

    Keys match the future return of ``fit_simple_hubble_model``.

    Returns
    -------
    dict
        ``hubbleConstant`` (float), ``hubbleConstantError`` (float),
        ``isMock`` (bool).
    """
    return {
        "hubbleConstant": 70.0,
        "hubbleConstantError": 3.0,
        "isMock": True,
    }
