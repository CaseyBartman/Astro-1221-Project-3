"""
Hubble Diagram page
===================

The classic plot: distance modulus versus redshift for the JLA
compilation, overlaid with the best-fit Lambda-CDM cosmological model and a
residuals panel showing the deviations of the data from that model.

Currently uses mock fit results from ``src.mock_fit_results``. When the real
``SupernovaOptimizer`` is finished, change the ``fit_results`` assignment.
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    format_cosmology_string,
    COLOUR_DATA,
    COLOUR_FIT,
    COLOUR_MUTED,
)
from src.mock_fit_results import get_mock_fit_results
from src.models import SupernovaCosmologyModels


st.set_page_config(page_title="Hubble Diagram", layout="wide")
configure_plot_style()


st.title("Hubble Diagram")
st.markdown(
    "Distance modulus versus redshift for the JLA sample, with the "
    "best-fit Lambda-CDM cosmology shown as a smooth curve. The lower panel "
    "shows the residuals: the scatter of each supernova around the fitted "
    "model."
)
st.markdown("---")


# -- Load data and fit results ------------------------------------------
dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)

# TODO: Swap for real results when optimizer.py is complete.
fit_results = get_mock_fit_results()

if fit_results["isMock"]:
    st.warning(
        "Showing **mock fit values** pending the optimizer module. The curve "
        "shown here is the fiducial consensus cosmology "
        "(H\u2080 = 70, \u03A9\u2098 = 0.30, \u03A9\u039B = 0.70), not a "
        "fit to these data. This will update automatically once "
        "`src/optimizer.py` is implemented.",
        icon=":material/warning:",
    )


# -- Axis options --------------------------------------------------------
controls_a, controls_b = st.columns([1, 1])
with controls_a:
    use_log_axis = st.toggle(
        "Logarithmic redshift axis",
        value=True,
        help=(
            "A log axis compresses the wide dynamic range from z = 0.01 to "
            "z > 1 so low-redshift and high-redshift supernovae can be "
            "viewed together."
        ),
    )
with controls_b:
    show_residuals = st.toggle("Show residuals panel", value=True)


# -- Compute model curve on a dense redshift grid -----------------------
models = SupernovaCosmologyModels()

z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()

z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)
mu_curve = models.calculate_advanced_cosmological_model(
    z_curve,
    fit_results["hubbleConstant"],
    fit_results["matterDensity"],
    fit_results["darkEnergyDensity"],
)

# Residuals at each actual data point.
mu_model_at_data = models.calculate_advanced_cosmological_model(
    z_data,
    fit_results["hubbleConstant"],
    fit_results["matterDensity"],
    fit_results["darkEnergyDensity"],
)
residuals = mu_data - mu_model_at_data


# -- Build the figure ---------------------------------------------------
if show_residuals:
    fig, (ax_main, ax_res) = plt.subplots(
        2, 1, figsize=(11, 7),
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
        sharex=True,
    )
else:
    fig, ax_main = plt.subplots(figsize=(11, 6))
    ax_res = None

# Main panel: data and fit curve
ax_main.scatter(
    z_data, mu_data,
    color=COLOUR_DATA, s=14, alpha=0.7, edgecolor="none",
    label=f"JLA data (n = {len(dataframe)})",
)
ax_main.plot(
    z_curve, mu_curve,
    color=COLOUR_FIT, linewidth=2.2,
    label="Lambda-CDM best fit",
)
ax_main.set_ylabel("Distance modulus $\\mu$")
ax_main.set_title(format_cosmology_string(
    fit_results["hubbleConstant"],
    fit_results["matterDensity"],
    fit_results["darkEnergyDensity"],
))
ax_main.legend(loc="lower right")
if use_log_axis:
    ax_main.set_xscale("log")
if not show_residuals:
    ax_main.set_xlabel("Redshift z")

# Residuals panel
if ax_res is not None:
    ax_res.scatter(
        z_data, residuals,
        color=COLOUR_DATA, s=10, alpha=0.6, edgecolor="none",
    )
    ax_res.axhline(0.0, color=COLOUR_FIT, linewidth=1.5, linestyle="--")
    ax_res.set_ylabel("$\\mu_{\\rm data} - \\mu_{\\rm model}$")
    ax_res.set_xlabel("Redshift z")
    if use_log_axis:
        ax_res.set_xscale("log")

    residual_rms = float(np.sqrt(np.mean(residuals ** 2)))
    ax_res.text(
        0.02, 0.9, f"RMS residual = {residual_rms:.3f} mag",
        transform=ax_res.transAxes,
        color=COLOUR_MUTED, fontsize=10, verticalalignment="top",
    )

st.pyplot(fig, clear_figure=True)


# -- Interpretation note ------------------------------------------------
st.markdown(
    """
    #### How to read this plot

    The smooth curve is what the consensus Lambda-CDM cosmology predicts
    for the relationship between a supernova's distance modulus and its
    redshift. The scatter of data points around that curve reflects
    real measurement uncertainty and a small intrinsic scatter in how
    well the Tripp correction standardises Type Ia supernovae.

    The absence of a clear tilt or curve in the residuals is itself the
    evidence: if the universe were matter-only (Einstein-de Sitter), the
    high-redshift residuals would curve systematically upward away from
    zero. See the **Model Comparison** page to see that curve directly.
    """
)
