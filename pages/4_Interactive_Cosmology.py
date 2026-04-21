"""
Interactive Cosmology page
==========================

Live sliders for ``H_0``, ``Omega_m``, and ``Omega_Lambda``. As the user
drags, the predicted Hubble curve updates in real time over the Union2.1
data. Displays the present-day deceleration parameter ``q_0`` so the user
can see directly when the universe they have built is accelerating.

This page is the pedagogical heart of the application: by manipulating the
cosmological parameters and watching the curve bend, a viewer can develop
direct intuition for why the 1998 supernova data ruled out a matter-only
universe.
"""

import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    format_cosmology_string,
    compute_deceleration_parameter,
    COLOUR_DATA,
    COLOUR_FIT,
    COLOUR_EMPTY,
)
from src.models import SupernovaCosmologyModels


st.set_page_config(page_title="Interactive Cosmology", layout="wide")
configure_plot_style()


st.title("Interactive Cosmology")
st.markdown(
    "Drag the sliders to build your own universe. The amber curve shows "
    "what that universe predicts for the distance modulus as a function of "
    "redshift; the teal points are the real Union2.1 measurements. For "
    "comparison, the violet dashed curve is the empty (Milne) universe, "
    "which is the natural null hypothesis."
)
st.markdown("---")


# -- Sliders ------------------------------------------------------------
slider_col, info_col = st.columns([2, 1], gap="large")

with slider_col:
    st.subheader("Your universe")
    hubble_constant = st.slider(
        "Hubble constant  H\u2080  (km / s / Mpc)",
        min_value=50.0, max_value=90.0, value=70.0, step=0.5,
        help=(
            "The current expansion rate of the universe. Planck measures "
            "roughly 67; local distance-ladder measurements prefer roughly "
            "73. The 'Hubble tension' is the disagreement between these."
        ),
    )
    matter_density = st.slider(
        "Matter density  \u03A9\u2098",
        min_value=0.0, max_value=1.0, value=0.3, step=0.01,
        help=(
            "Fraction of the total energy budget of the universe that is "
            "in the form of matter (dark plus ordinary). The consensus "
            "value is about 0.30."
        ),
    )
    dark_energy_density = st.slider(
        "Dark-energy density  \u03A9\u039B",
        min_value=0.0, max_value=1.0, value=0.7, step=0.01,
        help=(
            "Fraction of the total energy budget in dark energy "
            "(cosmological constant). The consensus value is about 0.70. "
            "Setting this to zero reproduces a universe with no dark "
            "energy."
        ),
    )

with info_col:
    st.subheader("Diagnostics")

    total_density = matter_density + dark_energy_density
    q0 = compute_deceleration_parameter(matter_density, dark_energy_density)

    st.metric(
        "\u03A9_total  = \u03A9\u2098 + \u03A9\u039B",
        f"{total_density:.2f}",
        delta=f"{total_density - 1.0:+.2f} from flat",
        delta_color="off",
    )

    st.metric(
        "Deceleration parameter  q\u2080",
        f"{q0:+.3f}",
        delta="accelerating" if q0 < 0 else "decelerating",
        delta_color=("inverse" if q0 < 0 else "normal"),
        help=(
            "q\u2080 = \u03A9\u2098/2 - \u03A9\u039B, from Ryden & Peterson "
            "eq. 24.37, neglecting radiation. Negative means the expansion "
            "is accelerating -- the 1998 discovery."
        ),
    )

    if abs(total_density - 1.0) > 0.05:
        st.caption(
            ":orange[Note: this model is not spatially flat. The code "
            "silently uses the flat-universe approximation, so curves "
            "shown are approximate for non-flat inputs.]"
        )


# -- Data and curves ----------------------------------------------------
dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)
z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()

models = SupernovaCosmologyModels()

z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)

# Your-universe curve. Use the closed-form empty-universe formula when both
# density parameters are effectively zero, because the numerical integral
# has a removable singularity in that limit.
if matter_density < 1e-3 and dark_energy_density < 1e-3:
    mu_your_universe = models.calculate_empty_universe_model(
        z_curve, hubble_constant
    )
else:
    mu_your_universe = models.calculate_advanced_cosmological_model(
        z_curve, hubble_constant, matter_density, dark_energy_density,
    )

# Milne reference curve at the same H0 -- visually anchors "no dark energy,
# no matter" for comparison.
mu_milne = models.calculate_empty_universe_model(z_curve, hubble_constant)


# -- Plot ---------------------------------------------------------------
fig, ax = plt.subplots(figsize=(11, 6))

ax.scatter(
    z_data, mu_data,
    color=COLOUR_DATA, s=12, alpha=0.55, edgecolor="none",
    label=f"Union2.1 data (n = {len(dataframe)})",
    zorder=1,
)
ax.plot(
    z_curve, mu_milne,
    color=COLOUR_EMPTY, linewidth=1.6, linestyle="--",
    label="Empty universe (Milne)", zorder=2,
)
ax.plot(
    z_curve, mu_your_universe,
    color=COLOUR_FIT, linewidth=2.4,
    label="Your universe", zorder=3,
)
ax.set_xscale("log")
ax.set_xlabel("Redshift z")
ax.set_ylabel("Distance modulus $\\mu$")
ax.set_title(format_cosmology_string(
    hubble_constant, matter_density, dark_energy_density
))
ax.legend(loc="lower right")

st.pyplot(fig, clear_figure=True)


# -- Suggested experiments ----------------------------------------------
st.markdown(
    """
    #### Suggested experiments

    - **Turn dark energy off.** Set ``Omega_Lambda = 0`` and ``Omega_m = 1``
      (matter-only, Einstein-de Sitter). The curve should fall below the
      data at high redshift -- the distant supernovae are fainter than a
      matter-only universe predicts. This was the 1998 discovery.
    - **Turn dark energy on.** Set ``Omega_Lambda = 0.7`` and
      ``Omega_m = 0.3``. The curve now sits neatly on top of the data.
    - **Dial up the Hubble constant.** Push H\u2080 from 67 to 73 and
      watch the curve drop uniformly. This is the Hubble tension: both
      values are within the data's scatter, but they disagree more sharply
      than either measurement's quoted uncertainty permits.
    - **Build an empty universe.** Set both densities to zero. The solid
      amber curve collapses onto the violet Milne reference.
    """
)
