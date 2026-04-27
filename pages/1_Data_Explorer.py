# Data Explorer page
# ==================

# Look at the cleaned JLA compilation, search by name, filter by redshift, and
# see what each column actually measures. Each plot has a note explaining what it shows and why we care!

import matplotlib.pyplot as plt
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    COLOR_DATA,
    COLOR_FIT,
)


st.set_page_config(page_title="Data Explorer", layout="wide")
configure_plot_style()

st.title("Data Explorer")
st.markdown(
    "Look at the JLA Type 1a supernovae complilation, each row is one"
    "supernova. Expand the glossary below to understand the column names and their physical measurements"
)
st.markdown("---")

## Sets up the sidebar for this tab and the main title for the page itself with a small description of what's in it. 

#-- Column Glossary ------------------------------------------------------------

with st.expander ("What do the columns actually mean?", expanded=False):
    st.markdown(
        """
        **supernova name** -- Just a name. Names starting with ``SDSS``
        come from the Sloan Digital Sky Survey; names like ``04D1au`` come
        from the Supernova Legacy Survey (SNLS); names like ``sn2005na``
        are traditional IAU supernova designations.
 
        **redshift (z)** -- This shows how much the wavelength of the supernova's
        light has been stretched by the expansion of space between the
        supernova and us. Redshift is what we use as the "distance" axis in a Hubble
        diagram, because it is measured directly from the spectrum and
        is independent of any distance calibration. It has everything to do with the Dopple
        shift since light has wave like attributes. We would calculate 'z' in various ways, one including an equation called Hubble's Law.
        Blueshifts (z<0) are when objects are approaching us, and redshift (z>0) is when an object is leaving us. 
 
        **magnitude (m_B)** -- this is the **apparent** peak brightness in the
        from the telescope. This is *not* the intrinsic luminosity of the supernova,
        it is how bright the supernova appeared to us on Earth. In the
        magnitude system lower numbers are brighter, and a difference of
        5 magnitudes is a factor of 100 in flux. Typical JLA supernovae
        range from about 14 (very bright, very nearby) to about 25
        (faint, very distant).
 
        **stretch (s)** -- the stretch refers to the light-curve shape parameter. 
        This factor shows how fast a supernova light curve rises and falls. A longer stretch
        or slower decline off the curve usually means a more luminous event. This is used to measure
        distances across the expanding universe. Type Ia supernovae with broader light curves (higher s) reach slightly
        higher intrinsic peak brightnesses and take longer to fade or brighten. In JLA, s is centred near 1,
        so values above 1 are broader-than-average and values below are
        narrower. This is one of the two corrections that turn Type Ia
        supernovae into reliable standard candles. In some cases a really high factor could indicit more relativistic happenings like 
        time dilation.
 
        **color (c)** -- the color index measures the temp and evolution of an explosion
        by using B-V. This is the difference between the Blue and Green visible wavelengths. 
        Type 1a specifically have a c around 0 to -0.25, with brighter supernovae being a bit bluer.
        A smaller number would mean a hotter, bluer object. In JLA, these values are centered around 0.
        Just adding on a little more, if c=0 then the supernova has the Type 1a typical color at peak,
        if c is negative then its a little bluer than typical and if positive the color is a little redder than typical.
 
        **mu (distance modulus)** -- this is the calculated distance
        that we say is the actual distance, it cannot be just observed. It is a logarithmic distance
        with the equation being: ``mu = 5 * log10(d_L / 1 Mpc) + 25``, where ``d_L`` is the
        luminosity distance in megaparsecs. A difference of 5 in mu is
        a factor of 10 in distance. Computing mu from the raw magnitude,
        stretch, and Color is what the Tripp relation does, it is the
        y-axis on the Hubble Diagram page.
        """
    )

## I personally forget often want certain variables mean and how they fit into the broader scheme of the project 
## For the viewer and for myself, I thought it would have been nice to have a detailed description of each variable and 
## how they were calculated. 

# -- Load data -----------------------------------------------------------

dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)

# -- Search and filter --------------------------------------------------

st.subheader("Search and filter")
 
search_col, slider_col = st.columns([2, 3])
 
with search_col:
    search_term = st.text_input(
        "Search by name",
        value="",
        placeholder="e.g. SDSS1242, 04D1au, sn2005",
        help=(
            "Case-insensitive substring match. Leave blank to show all."
        ),
    )
 
with slider_col:
    z_min_global = float(dataframe["redshift"].min())
    z_max_global = float(dataframe["redshift"].max())
 
    z_min_selected, z_max_selected = st.slider(
        "Redshift range",
        min_value=z_min_global,
        max_value=z_max_global,
        value=(z_min_global, z_max_global),
        step=0.01,
    )
 
# Apply filters
filtered = dataframe[
    (dataframe["redshift"] >= z_min_selected)
    & (dataframe["redshift"] <= z_max_selected)
]
 
if search_term.strip():
    mask = filtered["supernova name"].astype(str).str.contains(
        search_term.strip(), case=False, na=False
    )
    filtered = filtered[mask]
 
# -- Summary metrics ----------------------------------------------------

metric_a, metric_b, metric_c = st.columns(3)
metric_a.metric("Matching supernovae", f"{len(filtered):,} / {len(dataframe):,}")
if len(filtered) > 0:
    metric_b.metric("Median redshift", f"{filtered['redshift'].median():.3f}")
    metric_c.metric(
        "Median apparent magnitude",
        f"{filtered['magnitude'].median():.2f}",
    )
else:
    metric_b.metric("Median redshift", "--")
    metric_c.metric("Median apparent magnitude", "--")
 
# -- Data table ---------------------------------------------------------

st.subheader("Matching records")
st.markdown(
    "The ``mu`` column is the Tripp-standardised distance modulus "
    "computed from the raw ``magnitude``, ``stretch``, and ``color`` "
    "values. See the glossary above, or the Methodology page, for the "
    "exact formula."
)

if len(filtered) == 0:
    st.info("No supernovae match the current filter and search")
else:
    st.dataframe(
        filtered,
        use_container_width=True,
        height=320,
        hide_index=True,
    )

# -- Distribution plots -------------------------------------------------

if len(filtered) > 0:
    st.subheader("Distributions")
    st.markdown(
        "The four panels below show how the current selection is "
        "distributed across the main quantities. Together they "
        "tell you at a glance what kind of supernovae are in the sample."
    )
 
    fig, axes = plt.subplots(2, 2, figsize=(11, 7))
    fig.subplots_adjust(hspace=0.35, wspace=0.3)
 
    # Redshift distribution
    axes[0, 0].hist(
        filtered["redshift"], bins=40,
        color=COLOR_DATA, edgecolor="black", alpha=0.85,
    )
    axes[0, 0].set_xlabel("Redshift z")
    axes[0, 0].set_ylabel("Count")
    axes[0, 0].set_title("Redshift distribution")
 
    # Apparent magnitude distribution
    axes[0, 1].hist(
        filtered["magnitude"], bins=40,
        color=COLOR_FIT, edgecolor="black", alpha=0.85,
    )
    axes[0, 1].set_xlabel("Apparent B magnitude m$_B$")
    axes[0, 1].set_ylabel("Count")
    axes[0, 1].set_title("Apparent-magnitude distribution")
 
    # Stretch vs Color -- the Tripp plane
    axes[1, 0].scatter(
        filtered["stretch"], filtered["color"],
        c=filtered["redshift"], cmap="viridis", s=14, alpha=0.8,
    )
    axes[1, 0].set_xlabel("Light-curve stretch s")
    axes[1, 0].set_ylabel("Color c (B - V)")
    axes[1, 0].set_title("Tripp plane (Colored by redshift)")
 
    # mu vs z -- preview of the Hubble diagram
    axes[1, 1].scatter(
        filtered["redshift"], filtered["mu"],
        color=COLOR_DATA, s=12, alpha=0.75, edgecolor="none",
    )
    axes[1, 1].set_xscale("log")
    axes[1, 1].set_xlabel("Redshift z (log scale)")
    axes[1, 1].set_ylabel("Distance modulus $\\mu$")
    axes[1, 1].set_title("Hubble diagram preview")
 
    st.pyplot(fig, clear_figure=True)
 
    st.markdown(
        """
        #### Why these four panels?
 
        - **Redshift distribution (top left)** -- most supernovae are
          at low-to-moderate redshift, because nearby supernovae are
          easier to find. The long tail toward ``z ~ 1`` is the
          crucial part for cosmology: the high-z supernovae are where
          dark energy leaves a visible signature.
        - **Magnitude distribution (top right)** -- the apparent-
          magnitude distribution tracks the redshift distribution,
          because more distant supernovae look fainter. Sharp survey
          flux limits show up here as abrupt edges.
        - **Tripp plane (bottom left)** -- shows every supernova's
          stretch versus Color, Colored by redshift. The cluster
          near ``s = 1`` and ``c = 0`` is the "typical" Type Ia; the
          scatter around that is what the Tripp correction flattens
          out to turn the supernovae into standard candles.
        - **Hubble diagram preview (bottom right)** -- a sneak peek
          of the main science plot. The tight band of points is the
          standard-candle relationship; supernovae at higher redshift
          have higher distance modulus, as they should.
        """
    )
    ##used AI to help with longer scientific explanations
