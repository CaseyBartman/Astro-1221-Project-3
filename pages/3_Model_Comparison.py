# Model Comparison page
# =====================

# Three cosmological models plotted together on the same Hubble diagram:

# - Empty (Milne) universe: ``Omega_m = 0``, ``Omega_Lambda = 0``.
# - Matter-only (Einstein-de Sitter): ``Omega_m = 1``, ``Omega_Lambda = 0``.
# - Lambda-CDM consensus: ``Omega_m = 0.3``, ``Omega_Lambda = 0.7``.

# This is the page that "shows dark energy": the data visibly prefer the
# Lambda-CDM curve over the matter-only alternative at high redshift.

# This and the next page are two of my favorites, really pages 2-4 are very close
# in what they display but I thought the small differences would be cool. I like seeing
# all three models that we decided to play with over one another (if chosen). 

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    COLOR_DATA,
    COLOR_FIT,
    COLOR_EMPTY,
    COLOR_MATTER,
)
from src.models import SupernovaCosmologyModels


st.set_page_config(page_title="Model Comparison", layout="wide")
configure_plot_style()


st.title("Model Comparison")
st.markdown(
    "Three very different universes. Each curve is what that "
    "universe predicts for the distance modulus of a Type Ia supernova at "
    "redshift ``z``, assuming the same Hubble constant H\u2080 = 70 km/s/Mpc."
)
st.markdown("---")

# -- Explanation of what this page is for -------------------------------

with st.expander("What is this page trying to show?", expanded=True):
    st.markdown(
        """
        The Hubble Diagram page shows a single best-fit curve drawn on
        the data. That's useful, but it hides how
        strongly the data *rules out* other possibilities.
 
        This page draws three completely different universes on top of
        the same data points.
 
        - **Empty universe (Milne)** -- assumes the universe contains
          no matter and no dark energy. A useful
          blank hypothesis: if the data sit on this curve, the universe
          has nothing in it. If they sit above or below, the universe
          has *something*. And we know the universe has something, so we assume
          the data will not sit on the curve.
        - **Matter-only (Einstein-de Sitter)** -- assumes the universe
          is full of ordinary matter (``Omega_m = 1``) and has no dark
          energy. This is what physicists expected before 1998. Gravity
          should slow the expansion down over time.
        - **Dark Energy consensus** -- assumes the universe is ~30%
          matter and ~70% dark energy, which is what fits the data.
          Dark energy makes the expansion *speed up* over time.
 
        The lower panel of the figure below removes the Dark Energy
        curve and plots everything as the difference from it. That is
        where the matter-only curve's disagreement with the data
        becomes unmistakable.
        """
    )
 
## I think at this point, this type of set up for each page has been seen enough to where more explanation would be redundant

# -- Shared constants ---------------------------------------------------

H0_SHARED = 70.0
models = SupernovaCosmologyModels()

## shared constants just means that each fit will use the same values here. 
## The hubble constant is shared because the point of this page is to compare the different models
## If the constant varied you could not tell whether the differences were with the value of the constant or the H values.
## 70 is reasonable enough, if we were to do this project again I would prefer to work with 68 but it does what it needs to do!

# -- Data and curves ----------------------------------------------------

dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)

z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()

z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)


## We load the JLA dataset then pull out the redshift and distance modulus columns as NumPy arrays.
## Similar to the Hubble Diagram page, we made a 200-point array for the redshifts evenly spaced in a log scale.

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

## These are our three models that we have seen numerous times already.
## This computes the predicted distance modulus at each of the 200 grid points for the three models
## none of these are fits, there was no optimizer for this one. This is what each model PREDICTS independent of the data,
## The point is to see how the guesses look agaisnt the actual measurements and fits of other pages. 
## Even with just guesses we can easily tell which model is the best for our universe. 


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

# Residuals: deviation of each model from the consensus, at the data redshifts,
# to make the dark-energy signature visible on the bottom panel.

# -- Main figure --------------------------------------------------------

fig, (ax_main, ax_res) = plt.subplots(
    2, 1, figsize=(11, 8),
    gridspec_kw={"height_ratios": [3, 1.4], "hspace": 0.08},
    sharex=True,
)

## setting up another 2 panel subplot with the main groph on top and bigger, and the residuals on bottom and a little smaller
## sharex=true links the panel's x-axis since they will both show the same redshift

# Upper panel: data + three curves
ax_main.scatter(
    z_data, mu_data,
    color=COLOR_DATA, s=12, alpha=0.55, edgecolor="none",
    label=f"JLA data (n = {len(dataframe)})",
    zorder=1,
)
ax_main.plot(
    z_curve, mu_empty,
    color=COLOR_EMPTY, linewidth=2.0, linestyle="--",
    label="Empty (Milne):   $\\Omega_m=0,\\; \\Omega_\\Lambda=0$",
    zorder=3,
)
ax_main.plot(
    z_curve, mu_matter,
    color=COLOR_MATTER, linewidth=2.0, linestyle="-.",
    label="Matter-only (EdS): $\\Omega_m=1,\\; \\Omega_\\Lambda=0$",
    zorder=3,
)
ax_main.plot(
    z_curve, mu_lcdm,
    color=COLOR_FIT, linewidth=2.4,
    label="Consensus ($\\Lambda$CDM): $\\Omega_m=0.3,\\; \\Omega_\\Lambda=0.7$",
    zorder=4,
)
ax_main.set_xscale("log")
ax_main.set_ylabel("Distance modulus $\\mu$")
ax_main.set_title("Three cosmologies, one dataset")
ax_main.legend(loc="lower right", fontsize=9)

## This scatters the data then plots each model on top of it, each model is assigned a different color and line style
## This is build the visual representation of the guesses we have been making

# Lower panel: residuals relative to the Dark Energy consensus
ax_res.scatter(
    z_data, residuals_data,
    color=COLOR_DATA, s=10, alpha=0.55, edgecolor="none",
    zorder=1,
)
ax_res.axhline(0.0, color=COLOR_FIT, linewidth=1.8, linestyle="-",
               label="$\\Lambda$CDM reference")
ax_res.plot(
    z_curve, residuals_empty,
    color=COLOR_EMPTY, linewidth=1.8, linestyle="--",
    label="Empty - $\\Lambda$CDM",
)
ax_res.plot(
    z_curve, residuals_matter,
    color=COLOR_MATTER, linewidth=1.8, linestyle="-.",
    label="Matter-only - $\\Lambda$CDM",
)
ax_res.set_xscale("log")
ax_res.set_xlabel("Redshift z")
ax_res.set_ylabel("$\\mu - \\mu_{\\Lambda{\\rm CDM}}$")
ax_res.legend(loc="lower left", fontsize=8, ncol=3)

##This is doing something very similar to the main plot, we added a horizontal reference line at 0.
## the line for our lambda model lays ontop of that reference line

st.pyplot(fig, clear_figure=True)


# -- Interpretation -----------------------------------------------------

st.markdown(
    """
    #### What this figure shows

    All three curves converge at low redshift. At ``z < 0.05`` the
    three universes are indistinguishable from each other, because
    light from those supernovae hasn't had time to record any
    meaningful expansion history. The curves only diverge where the
    universe is old enough for its contents to matter -- roughly at
    ``z > 0.3``.
 
    The lower panel removes the Lambda-CDM curve and plots everything
    relative to it. The data scatter around zero, which means
    Lambda-CDM is a good description. The matter-only curve drops
    systematically below zero at high redshift, which means a
    matter-only universe would predict supernovae at ``z > 0.5`` to be
    **brighter** than we observe. They are not. They are **fainter**,
    which is exactly what a dark-energy-dominated expansion does to
    distant objects. This is the 1998 discovery in one panel.
 
    The empty Milne universe sits between the two. It's not a viable
    universe but it's a useful reference. Any departure of the data from the Milne curve
    is evidence that the universe contains matter and/or dark energy
    that is gravitationally active.
    """
)

## AI assisted Scientific explanation
