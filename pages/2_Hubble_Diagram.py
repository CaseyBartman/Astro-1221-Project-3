
# Hubble Diagram page
# ===================
# The main thing to our project! This plots distance modulus versus redshift for
# the JLA compilation. There are best-fit models for the universes displayed. 



import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    format_cosmology_string,
    COLOR_DATA,
    COLOR_FIT,
    COLOR_MUTED,
    COLOR_EMPTY, 
    COLOR_MATTER,
)

from src.models import SupernovaCosmologyModels
from src.optimizer import SupernovaOptimizer


st.set_page_config(page_title="Hubble Diagram", layout="wide")
configure_plot_style()


st.title("Hubble Diagram")
st.markdown(
     "Distance modulus versus redshift for the JLA sample. Select any "
    "combination of fit strategies in the sidebar to overlay them on "
    "the data. Each fit tells a different story about what the "
    "universe is made of."
)
st.markdown("---")

##Like many of our pages, the start is setting up the page and creating a small description of what we will see. 

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

 ## similar to the data explorer page explaining the variables seen in the data tables, this explains parts of what we see in the 
 ## main visual. This part is an expander so all this writing will not be overtaking your screen unless you go to look for it.
 ## all of these large blocks of explaination are really nice for me, even though I have been working on this project it is really 
 ## easy to take a break from it for a couple of days or a work and not fully remember exactly where everything comes from or why its there.

# -- Sidebar: choose which fit to display --------------------------------

st.sidebar.markdown("### Fits to display")
st.sidebar.markdown(
    "Select any combination. Each is run through "
    "``scipy.optimize.curve_fit`` on the JLA data."
)
 
 ## once you click on this page, in the same sidebar as the pages (not on the page itself) there will show a couple options.
 ## You select the fits you want to display, so it could be none, 1 or all of them at the same time. Along with that there is the
 ## option to un-log the redshifts. Using a logscale is nice because it appears linear, but if you wanted to see the actual redshifts, 
 ## you can see that not using the log will still get you the same type of fits. I actually like the not log one because you can see that
 ## the fits seem to fit a lot better at lower redshifts. With a log scale it seems that the incorrect fits are incorrect from the beginning, 
 ## but that would not be the case since we only assumed the wrong fit because it seemed right and smaller redshifts. And finally in the sidebar, 
 ## you have the option to show or hide the residuals panel if it was really an eyesore to you. 

show_empty = st.sidebar.checkbox(
    "Empty universe (H\u2080 only)",
    value=False,
    help=(
        "No matter, no dark energy. Only H\u2080 is fit. The classical "
        "Hubble-law limit."
    ),
)
show_matter_only = st.sidebar.checkbox(
    "Matter-only universe (\u03A9\u2098 only)",
    value=True,
    help=(
        "No dark energy. \u03A9\u2098 is fit, \u03A9\u039B = 0 "
        "enforced, H\u2080 held at 70. Represents the pre-1998 "
        "consensus view."
    ),
)
show_density = st.sidebar.checkbox(
    "Full density fit (\u03A9\u2098 and \u03A9\u039B)",
    value=True,
    help=(
        "Both density parameters free, H\u2080 held at 70. This matches "
        "the 1998 Perlmutter/Riess analyses -- flatness is NOT assumed."
    ),
)

## each of these are the checkboxes in the sidebars, they tell you which fit is which and if you cant tell just by the name
## there is a little ? next to checkbox that gives a little more detail.
 
st.sidebar.markdown("---")
st.sidebar.markdown("### Display")
use_log_axis = st.sidebar.toggle(
    "Logarithmic redshift axis", value=True,
    help="Log spreads out low-z points; linear is easier to read.",
)
show_residuals = st.sidebar.toggle("Show residuals panel", value=True)
 
## This is right under the checkboxes which makes a toggle for both the log redshifts and show residuals
## They started pre toggled and if you choose to turn them off / non-log.

 # -- Load data ----------------------------------------------------------

dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)
 
z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()
 
 
# -- Run selected fits --------------------------------------------------

optimizer = SupernovaOptimizer()
models = SupernovaCosmologyModels()
 
z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)

## we create an array of 200 redshift values that are evenly spaced on a log scale, 
## We decided to use np.logspace to match the log-axis we used in the plot
  
# Each entry: (label, color, linestyle, n_params, fit_dict, mu_curve,
# mu_at_data). Built only for selected fits.
fit_entries = []
 
## This is an empty list and each fit that is chosen will append a tuple to it

if show_empty:
    fit = optimizer.fit_empty_universe_hubble(z_data, mu_data)
    mu_curve = models.calculate_empty_universe_model(z_curve, fit["hubbleConstant"])
    mu_at_data = models.calculate_empty_universe_model(z_data, fit["hubbleConstant"])
    fit_entries.append((
        "Empty universe", COLOR_EMPTY, "--", 1, fit, mu_curve, mu_at_data,
    ))
 
if show_matter_only:
    fit = optimizer.fit_matter_only(z_data, mu_data)
    mu_curve = models.calculate_advanced_cosmological_model(
        z_curve, fit["hubbleConstant"], fit["matterDensity"], 0.0
    )
    mu_at_data = models.calculate_advanced_cosmological_model(
        z_data, fit["hubbleConstant"], fit["matterDensity"], 0.0
    )
    fit_entries.append((
        "Matter-only", COLOR_MATTER, "-.", 1, fit, mu_curve, mu_at_data,
    ))
 
if show_density:
    fit = optimizer.fit_density_parameters(z_data, mu_data)
    mu_curve = models.calculate_advanced_cosmological_model(
        z_curve, fit["hubbleConstant"],
        fit["matterDensity"], fit["darkEnergyDensity"],
    )
    mu_at_data = models.calculate_advanced_cosmological_model(
        z_data, fit["hubbleConstant"],
        fit["matterDensity"], fit["darkEnergyDensity"],
    )
    fit_entries.append((
        "Full density fit", COLOR_FIT, "-", 2, fit, mu_curve, mu_at_data,
    ))
 
 ## the code for each fit looks a little repetitive but each one calls something different
 ## Empty universe calls fit_empty_universe_hubble from optimizer.py and calculate_empty_universe_model.
 ## Matter only calls fit_matter_only from the same source and calculate_advanced_cosmological_model that has Omega lambda forced at 0
 ## Full denisty calls fit_density_parameter and calculate_advanced_cosmological_model
 ## each block has a different way to evaluate its model and it works better to write them all out. 
 
if not fit_entries:
    st.warning(
        "No fits selected. Check at least one box in the sidebar to "
        "display a best-fit curve."
    )
    st.stop()
 
 ## if no boxes are checked then a warning is displayed since we have nothing to plot

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
 
## If the residuals are chosen (which they are automatically) then we make a make a two panel
## figure with the main plot on top and residuals on bottom that stare the x-axis. If the residuals
## are turned off then the main plot is the only thing there 

# Main panel: data + each selected curve
ax_main.scatter(
    z_data, mu_data,
    color=COLOR_DATA, s=14, alpha=0.7, edgecolor="none",
    label=f"JLA data (n = {len(dataframe)})",
    zorder=1,
)

## This plots every supernovae as a teal dot. It gathers the z and mu data to see where the dot belongs on the graph.
## Everything past that is visualization tweaks, color data defined in app_utils finds the color, s=14 defines the size
## of the points, alpha is the opacity, and so forth. 

for (label, color, linestyle, _n_p, fit, mu_curve, _mu_at_data) in fit_entries:
    full_label = (
        f"{label}: "
        f"H\u2080={fit['hubbleConstant']:.1f}, "
        f"\u03A9\u2098={fit['matterDensity']:.2f}, "
        f"\u03A9\u039B={fit['darkEnergyDensity']:.2f}"
    )
    ax_main.plot(
        z_curve, mu_curve,
        color=color, linewidth=2.2, linestyle=linestyle,
        label=full_label, zorder=3,
    )

## This block loops through every fit that is chosen and draws a curve for each one.
## fit_entries is a lost of tuples and each tuple is the stuff inside the ()
## the f strings build the legend that includes the fit name and the three parameters
## the awful looking series of letters and numbers are the codes for the hubble constant, 
## omega M and Lambda, it's just so the subscript and Greek letters actually come through

ax_main.set_ylabel("Distance modulus $\\mu$")
ax_main.legend(loc="lower right", fontsize=9)
if use_log_axis:
    ax_main.set_xscale("log")
if not show_residuals:
    ax_main.set_xlabel("Redshift z")
 
## this is the set up for the main plot, the y axis for this plot is always the distance modulus
## it draws the legend and always us to switch between log scale and the different labels for the x-axis
## depending on if it's in the log scale or not
## the dollar signs with mu just makes it so it appears a sthe greek letter and not m.

# Residuals panel
if ax_res is not None:
    ax_res.axhline(0.0, color=COLOR_MUTED, linewidth=1.0, linestyle=":")
    for (label, color, linestyle, _n_p, _fit, _mu_curve, mu_at_data) in fit_entries:
        residuals_this = mu_data - mu_at_data
        ax_res.scatter(
            z_data, residuals_this,
            color=color, s=8, alpha=0.45, edgecolor="none",
        )
    ax_res.set_ylabel("$\\mu_{\\rm data} - \\mu_{\\rm model}$")
    ax_res.set_xlabel("Redshift z")
    if use_log_axis:
        ax_res.set_xscale("log")
 
## if the residual panel is clicked then it will draw a horizontal zero line and scatter the residuals from each selected fit
## positive residuals mean the supernova is further than the model predicts and negative means its closer than predicted

st.pyplot(fig, clear_figure=True)
 
## this gives the matplotlib figure to streamlit and renders the image in a browser
## the clear figure command removes the figures after each run so it doesnt run out of memory or slow down the app
 
# -- Side-by-side fit-results table ------------------------------------

st.markdown("#### Fit results")
 
cols = st.columns(len(fit_entries))
for col, (label, _color, _ls, n_p, fit, _mu_curve, mu_at_data) in zip(cols, fit_entries):
    with col:
        st.markdown(f"**{label}**")

        # Build display strings explicitly to avoid nested-f-string escaping.
        h0_err = fit.get("hubbleConstantError", 0.0)
        h0_str = f"H\u2080      = {fit['hubbleConstant']:.2f}"
        if h0_err > 0:
            h0_str += f"  ± {h0_err:.2f}"
        st.text(h0_str)
 
        om_err = fit.get("matterDensityError", 0.0)
        om_str = f"\u03A9\u2098     = {fit['matterDensity']:.3f}"
        if om_err > 0:
            om_str += f"  ± {om_err:.3f}"
        st.text(om_str)
 
        ol_err = fit.get("darkEnergyDensityError", 0.0)
        ol_str = f"\u03A9\u039B     = {fit['darkEnergyDensity']:.3f}"
        if ol_err > 0:
            ol_str += f"  ± {ol_err:.3f}"
        st.text(ol_str)
 
## for each parameter we want to build a string with the value plus an uncertainty. 
## the uncertainty will only show up if the value is being fit, or if the uncertainity is greater than 0
## the .get command is there with the hope that if something doesnt return, the parameter will just go to 0.0
## and the gross f strings are because of issues I kept running into. python couldnt parse through the quotes inside
## the inner f string so we built it step by step to aviod any mess

        gof = optimizer.calculate_goodness_of_fit(
            mu_data, mu_at_data, numberOfParameters=n_p,
        )
        st.text(f"\u03C7\u00B2       = {gof['chiSquared']:.1f}")
        st.text(f"\u03C7\u00B2 / dof = {gof['reducedChiSquared']:.2f}")
 
## each fit has a different number of free parameters and reduced x^2 divides by a term with n_p, so its important to pull the number for each fit.

st.caption(
    "Lower chi-squared means a better fit. The data prefer the fit "
    "with the smallest reduced chi-squared, and that preference is "
    "the statistical evidence for the content of the "
    "universe."
)
## more explanation

# -- Interpretation note ------------------------------------------------

st.markdown(
    """
    #### How to read this plot
 
    The smooth curve is the best-fit prediction for the relationship
    between distance modulus and redshift. Data points scatter around
    it, that scatter reflects real measurement uncertainty plus a small
    intrinsic scatter in how well the Tripp correction standardises
    Type Ia supernovae.
 
    The absence of a clear upward or downward trend in the residuals
    is itself the evidence for the model, if the universe were
    matter-only (Einstein-de Sitter), the high-redshift residuals would
    curve systematically upward away from zero. See the Model
    Comparison page to see that exact curve drawn on the same data.
    """
)
 
## and even MORE!