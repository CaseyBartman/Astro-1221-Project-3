"""
Data Explorer page
==================

 cleaned JLA compilation, filter by redshift range, and
visualise the distributions of the four physical columns.
"""

import matplotlib.pyplot as plt
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    COLOUR_DATA,
    COLOUR_FIT,
)


st.set_page_config(page_title="Data Explorer", layout="wide")
configure_plot_style()


st.title("Data Explorer")
st.markdown(
    "Look at the JLA Type 1a supernovae complilation, each row is one"
    "supernova with its redshift, peak apparent B-band magnitude, "
    "light-curve stretch, and colour parameter."
)
st.markdown("---")


# -- Load data -----------------------------------------------------------
dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)


# -- Redshift filter -----------------------------------------------------
st.subheader("Filter by redshift")

z_min_global = float(dataframe["redshift"].min())
z_max_global = float(dataframe["redshift"].max())

z_min_selected, z_max_selected = st.slider(
    "Redshift range",
    min_value=z_min_global,
    max_value=z_max_global,
    value=(z_min_global, z_max_global),
    step=0.01,
)

filtered = dataframe[
    (dataframe["redshift"] >= z_min_selected)
    & (dataframe["redshift"] <= z_max_selected)
]

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Supernovae in range", f"{len(filtered):,} / {len(dataframe):,}")
metric_b.metric("Median redshift", f"{filtered['redshift'].median():.3f}")
metric_c.metric(
    "Median apparent magnitude",
    f"{filtered['magnitude'].median():.2f}",
)


# -- Data table ---------------------------------------------------------
st.subheader("Raw records")
st.markdown(
    "The ``mu`` column is the Tripp-standardised distance modulus computed "
    "from the raw ``magnitude``, ``stretch``, and ``color`` values. See the "
    "Methodology page for the exact formula."
)
st.dataframe(
    filtered,
    use_container_width=True,
    height=320,
    hide_index=True,
)


# -- Distribution plots -------------------------------------------------
st.subheader("Distributions")

fig, axes = plt.subplots(2, 2, figsize=(11, 7))
fig.subplots_adjust(hspace=0.35, wspace=0.3)

# Redshift distribution
axes[0, 0].hist(
    filtered["redshift"], bins=40,
    color=COLOUR_DATA, edgecolor="black", alpha=0.85,
)
axes[0, 0].set_xlabel("Redshift z")
axes[0, 0].set_ylabel("Count")
axes[0, 0].set_title("Redshift distribution")

# Apparent magnitude distribution
axes[0, 1].hist(
    filtered["magnitude"], bins=40,
    color=COLOUR_FIT, edgecolor="black", alpha=0.85,
)
axes[0, 1].set_xlabel("Apparent B magnitude m$_B$")
axes[0, 1].set_ylabel("Count")
axes[0, 1].set_title("Apparent-magnitude distribution")

# Stretch vs colour -- the Tripp plane
axes[1, 0].scatter(
    filtered["stretch"], filtered["color"],
    c=filtered["redshift"], cmap="viridis", s=14, alpha=0.8,
)
axes[1, 0].set_xlabel("Light-curve stretch s")
axes[1, 0].set_ylabel("Colour c (B - V)")
axes[1, 0].set_title("Tripp plane (coloured by redshift)")

# mu vs z -- preview of the Hubble diagram
axes[1, 1].scatter(
    filtered["redshift"], filtered["mu"],
    color=COLOUR_DATA, s=12, alpha=0.75, edgecolor="none",
)
axes[1, 1].set_xscale("log")
axes[1, 1].set_xlabel("Redshift z (log scale)")
axes[1, 1].set_ylabel("Distance modulus $\\mu$")
axes[1, 1].set_title("Hubble diagram preview")

st.pyplot(fig, clear_figure=True)


st.caption(
    "The stretch-colour scatter is the empirical basis for the Tripp "
    "correction: supernovae away from the typical stretch or colour have "
    "systematically different peak luminosities, and the correction places "
    "them back on the standard candle."
)
