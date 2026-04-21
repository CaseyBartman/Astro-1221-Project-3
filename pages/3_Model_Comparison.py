"""
Model Comparison page
=====================

Three cosmological models plotted together on the same Hubble diagram:

- Empty (Milne) universe: ``Omega_m = 0``, ``Omega_Lambda = 0``.
- Matter-only (Einstein-de Sitter): ``Omega_m = 1``, ``Omega_Lambda = 0``.
- Lambda-CDM consensus: ``Omega_m = 0.3``, ``Omega_Lambda = 0.7``.

This is the page that "shows dark energy": the data visibly prefer the
Lambda-CDM curve over the matter-only alternative at high redshift.
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    COLOUR_DATA,
    COLOUR_FIT,
    COLOUR_EMPTY,
    COLOUR_MATTER,
)
from src.models import SupernovaCosmologyModels


st.set_page_config(page_title="Model Comparison", layout="wide")
configure_plot_style()


st.title("Model Comparison")
st.markdown(
    "Three very different universes, one dataset. Each curve is what that "
    "universe predicts for the distance modulus of a Type Ia supernova at "
    "redshift ``z``, assuming the same Hubble constant H\u2080 = 70 km/s/Mpc."
)
st.markdown("---")


# -- Shared constants ---------------------------------------------------
H0_SHARED = 70.0
models = SupernovaCosmologyModels()


# -- Data and curves ----------------------------------------------------
dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)

z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()

z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)

# Empty (Milne) universe: closed-form luminosity distance, no integral needed.
mu_empty = models.calculate_empty_universe_model(z_curve, H0_SHARED)

# Matter-only (Einstein-de Sitter): Omega_m = 1, Omega_Lambda = 0.
mu_matter = models.calculate_advanced_cosmological_model(
    z_curve, H0_SHARED, 1.0, 0.0
)

# Consensus Lambda-CDM: Omega_m = 0.3, Omega_Lambda = 0.7.
mu_lcdm = models.calculate_advanced_cosmological_model(
    z_curve, H0_SHARED, 0.3, 0.7
)

# Residuals: deviation of each model from the consensus, at the data redshifts,
# to make the dark-energy signature visible on the bottom panel.
mu_lcdm_at_data = models.calculate_advanced_cosmological_model(
    z_data, H0_SHARED, 0.3, 0.7
)
residuals_data = mu_data - mu_lcdm_at_data
residuals_empty = mu_empty - models.calculate_advanced_cosmological_model(
    z_curve, H0_SHARED, 0.3, 0.7
)
residuals_matter = mu_matter - models.calculate_advanced_cosmological_model(
    z_curve, H0_SHARED, 0.3, 0.7
)


# -- Main figure --------------------------------------------------------
fig, (ax_main, ax_res) = plt.subplots(
    2, 1, figsize=(11, 8),
    gridspec_kw={"height_ratios": [3, 1.4], "hspace": 0.08},
    sharex=True,
)

# Upper panel: data + three curves
ax_main.scatter(
    z_data, mu_data,
    color=COLOUR_DATA, s=12, alpha=0.55, edgecolor="none",
    label=f"JLA data (n = {len(dataframe)})",
    zorder=1,
)
ax_main.plot(
    z_curve, mu_empty,
    color=COLOUR_EMPTY, linewidth=2.0, linestyle="--",
    label="Empty (Milne):   $\\Omega_m=0,\\; \\Omega_\\Lambda=0$",
    zorder=3,
)
ax_main.plot(
    z_curve, mu_matter,
    color=COLOUR_MATTER, linewidth=2.0, linestyle="-.",
    label="Matter-only (EdS): $\\Omega_m=1,\\; \\Omega_\\Lambda=0$",
    zorder=3,
)
ax_main.plot(
    z_curve, mu_lcdm,
    color=COLOUR_FIT, linewidth=2.4,
    label="Consensus ($\\Lambda$CDM): $\\Omega_m=0.3,\\; \\Omega_\\Lambda=0.7$",
    zorder=4,
)
ax_main.set_xscale("log")
ax_main.set_ylabel("Distance modulus $\\mu$")
ax_main.set_title("Three cosmologies, one dataset")
ax_main.legend(loc="lower right", fontsize=9)

# Lower panel: residuals relative to the Lambda-CDM consensus
ax_res.scatter(
    z_data, residuals_data,
    color=COLOUR_DATA, s=10, alpha=0.55, edgecolor="none",
    zorder=1,
)
ax_res.axhline(0.0, color=COLOUR_FIT, linewidth=1.8, linestyle="-",
               label="$\\Lambda$CDM reference")
ax_res.plot(
    z_curve, residuals_empty,
    color=COLOUR_EMPTY, linewidth=1.8, linestyle="--",
    label="Empty - $\\Lambda$CDM",
)
ax_res.plot(
    z_curve, residuals_matter,
    color=COLOUR_MATTER, linewidth=1.8, linestyle="-.",
    label="Matter-only - $\\Lambda$CDM",
)
ax_res.set_xscale("log")
ax_res.set_xlabel("Redshift z")
ax_res.set_ylabel("$\\mu - \\mu_{\\Lambda{\\rm CDM}}$")
ax_res.legend(loc="lower left", fontsize=8, ncol=3)

st.pyplot(fig, clear_figure=True)


# -- Interpretation -----------------------------------------------------
st.markdown(
    """
    #### What this figure shows

    All three curves converge at low redshift -- at ``z < 0.05`` you cannot
    distinguish the cosmologies, because the differences are set by how much
    expansion has happened while the photons were in flight, and not much
    has happened yet. The models diverge rapidly at ``z > 0.3``.

    The lower panel removes the Lambda-CDM consensus and plots everything
    relative to it. The data scatter around zero, as they should if
    Lambda-CDM is a good description. The matter-only curve drops
    systematically below zero at high redshift -- equivalently, a
    matter-only universe predicts supernovae at ``z > 0.5`` should be
    **brighter** than we observe. They are not: they are **fainter**, which
    is exactly what dark energy does to distant objects. This is the 1998
    discovery in one panel.

    The empty Milne universe sits between the two. It is a useful null
    hypothesis -- a universe with expansion but no matter and no dark energy.
    Any departure of the data from the Milne curve is evidence that the
    universe has *something* in it, gravitationally.
    """
)
