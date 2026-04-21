"""
Hubble Diagram page
===================

The classic plot: distance modulus versus redshift for the JLA
compilation, overlaid with the best-fit universe-expansion model and a
residuals panel showing the deviations of the data from that model.
You can pick the fit strategy from the sidebar.


"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    format_cosmology_string,
    Color_DATA,
    Color_FIT,
    Color_MUTED,
)

from src.models import SupernovaCosmologyModels
from src.optimizer import SupernovaOptimizer


st.set_page_config(page_title="Hubble Diagram", layout="wide")
configure_plot_style()


st.title("Hubble Diagram")
st.markdown(
    "Distance modulus versus redshift for the JLA sample, with the "
    "best-fit model curve and a residuals panel. Use the sidebar to switch between fits."
)
st.markdown("---")

# -- Helper text explaining the key terms -------------------------------
with st.expander("What do these terms mean?", expanded=False):
    st.markdown(
        """
        **Distance modulus (mu)** -- a logarithmic measure of distance.
        See the Data Explorer glossary for the exact formula. Bigger
        ``mu`` means farther away.
 
        **Log redshift axis** -- the horizontal axis is set on a
        logarithmic scale so the nearby supernovae (``z ~ 0.01``) and
        the distant ones (``z ~ 1``) both fit visibly on the same plot.
        Without the log scale, the nearby points would all bunch up
        against the left edge.
 
        **Residuals panel** -- the lower panel plots each data point's
        distance modulus *minus* the model's prediction at that
        redshift. If the model is a good description of the data, the
        residuals scatter randomly around zero. If the model is wrong
        in some systematic way, the residuals will show a trend -- for
        example, rising at high redshift.
 
        **"Best-fit universe-expansion model"** -- the predicted distance-modulus curve for the
        combination of H0, matter density, and dark-energy density that
        minimises the squared difference between model and data. This
        is produced by ``scipy.optimize.curve_fit``; see the
        Methodology page for the mathematical details.
        """
    )
 ##AI produced scientific explanation

# -- Sidebar: choose which fit to display --------------------------------
st.sidebar.markdown("### Fit strategy")
fit_choice = st.sidebar.radio(
    "Which best-fit curve should be shown?",
    options=[
        "Flat universe (curvature is 1)",
        "Density fit at fixed H0 (Nobel Prize style)",
        "Empty universe (Hubble constant only)",
    ],
    index=0,
    help=(
        "All three use scipy.optimize.curve_fit. They differ in which "
        "parameters are held fixed versus fitted. See the Methodology "
        "page for a discussion of why H0 is normally held fixed in "
        "supernova-only analyses."
    ),
)
 
 
# -- Load data ----------------------------------------------------------
dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)
 
z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()
 
 
# -- Run the selected fit -----------------------------------------------
optimizer = SupernovaOptimizer()
 
if fit_choice.startswith("Flat"):
    fit = optimizer.fit_flat_universe(z_data, mu_data)
    fit_label = "Flat LambdaCDM (Omega_m + Omega_Lambda = 1)"
    n_free_params = 1
elif fit_choice.startswith("Density"):
    fit = optimizer.fit_density_parameters(z_data, mu_data)
    fit_label = "Density-fit at fixed H0 = 70"
    n_free_params = 2
else:
    fit = optimizer.fit_empty_universe_hubble(z_data, mu_data)
    # empty-universe fit doesn't return density params -- fill in zeros
    fit = {
        **fit,
        "matterDensity": 0.0,
        "darkEnergyDensity": 0.0,
    }
    fit_label = "Empty universe (Milne)"
    n_free_params = 1
 
# -- Display fit results as a strip of metrics --------------------------
st.markdown(f"#### Fit result: {fit_label}")
m1, m2, m3 = st.columns(3)
m1.metric(
    "H0 (km/s/Mpc)",
    f"{fit['hubbleConstant']:.2f}",
    delta=(f"± {fit['hubbleConstantError']:.2f}"
           if fit['hubbleConstantError'] > 0 else "held fixed"),
    delta_color="off",
)
m2.metric(
    "Omega_m",
    f"{fit['matterDensity']:.3f}",
    delta=(f"± {fit.get('matterDensityError', 0):.3f}"
           if fit.get('matterDensityError', 0) > 0 else "--"),
    delta_color="off",
)
m3.metric(
    "Omega_Lambda",
    f"{fit['darkEnergyDensity']:.3f}",
    delta=(f"± {fit.get('darkEnergyDensityError', 0):.3f}"
           if fit.get('darkEnergyDensityError', 0) > 0 else "--"),
    delta_color="off",
)
 
# -- Compute model curves ------------------------------------------------
models = SupernovaCosmologyModels()
 
z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)

# For the empty-universe fit, use the closed-form model. Otherwise use
# the full integral with the fitted densities.
if fit_choice.startswith("Empty"):
    mu_curve = models.calculate_empty_universe_model(
        z_curve, fit["hubbleConstant"]
    )
    mu_model_at_data = models.calculate_empty_universe_model(
        z_data, fit["hubbleConstant"]
    )
else:
    mu_curve = models.calculate_advanced_cosmological_model(
        z_curve,
        fit["hubbleConstant"],
        fit["matterDensity"],
        fit["darkEnergyDensity"],
    )
    mu_model_at_data = models.calculate_advanced_cosmological_model(
        z_data,
        fit["hubbleConstant"],
        fit["matterDensity"],
        fit["darkEnergyDensity"],
    )
 
residuals = mu_data - mu_model_at_data

# -- Display options -----------------------------------------------------
controls_a, controls_b = st.columns([1, 1])
with controls_a:
    use_log_axis = st.toggle(
        "Logarithmic redshift axis",
        value=True,
    )
with controls_b:
    show_residuals = st.toggle("Show residuals panel", value=True)

# -- Build the figure ----------------------------------------------------
if show_residuals:
    fig, (ax_main, ax_res) = plt.subplots(
        2, 1, figsize=(11, 7),
        gridspec_kw={"height_ratios": [3, 1], "hspace": 0.06},
        sharex=True,
    )
else:
    fig, ax_main = plt.subplots(figsize=(11, 6))
    ax_res = None
 
# Main panel
ax_main.scatter(
    z_data, mu_data,
    color=Color_DATA, s=14, alpha=0.7, edgecolor="none",
    label=f"JLA data (n = {len(dataframe)})",
)
ax_main.plot(
    z_curve, mu_curve,
    color=Color_FIT, linewidth=2.2,
    label=fit_label,
)
ax_main.set_ylabel("Distance modulus $\\mu$")
ax_main.set_title(format_cosmology_string(
    fit["hubbleConstant"],
    fit["matterDensity"],
    fit["darkEnergyDensity"],
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
        color=Color_DATA, s=10, alpha=0.6, edgecolor="none",
    )
    ax_res.axhline(0.0, color=Color_FIT, linewidth=1.5, linestyle="--")
    ax_res.set_ylabel("$\\mu_{\\rm data} - \\mu_{\\rm model}$")
    ax_res.set_xlabel("Redshift z")
    if use_log_axis:
        ax_res.set_xscale("log")
 
    residual_rms = float(np.sqrt(np.mean(residuals ** 2)))
    ax_res.text(
        0.02, 0.9, f"RMS residual = {residual_rms:.3f} mag",
        transform=ax_res.transAxes,
        color=Color_MUTED, fontsize=10, verticalalignment="top",
    )
 
st.pyplot(fig, clear_figure=True)

# -- Chi-squared report -------------------------------------------------
gof = optimizer.calculate_goodness_of_fit(
    mu_data, mu_model_at_data, numberOfParameters=n_free_params,
)
 
st.markdown(
    f"#### Goodness of fit  \n"
    f"chi-squared = **{gof['chiSquared']:.1f}**,  "
    f"reduced chi-squared = **{gof['reducedChiSquared']:.2f}**,  "
    f"degrees of freedom = **{gof['degreesOfFreedom']}**."
)
st.caption(
    "A reduced chi-squared close to 1 indicates a model that matches "
    "the data at roughly the level of the assumed per-point uncertainty "
    "(sigma_mu = 0.15 mag). Much larger than 1 means the model cannot "
    "explain all the scatter; much smaller than 1 means we have "
    "probably overestimated the per-point uncertainty."
)
 
# -- Interpretation note ------------------------------------------------
st.markdown(
    """
    #### How to read this plot
 
    The smooth curve is the best-fit prediction for the relationship
    between distance modulus and redshift. Data points scatter around
    it; that scatter reflects real measurement uncertainty plus a small
    intrinsic scatter in how well the Tripp correction standardises
    Type Ia supernovae.
 
    The absence of a clear upward or downward trend in the residuals
    is itself the evidence for the model: if the universe were
    matter-only (Einstein-de Sitter), the high-redshift residuals would
    curve systematically upward away from zero. See the Model
    Comparison page to see that exact curve drawn on the same data.
    """
)
 
