# Interactive Cosmology page
# ==========================

# We have sliders for ``H_0``, ``Omega_m``, and ``Omega_Lambda``. As the user
# drags, the predicted Hubble curve updates in real time over the JLA
# data. It displays the present-day deceleration parameter ``q_0`` so the user
# can see directly when the universe they have built is accelerating.

# By moving the parameters and watching the curve bend, we can develop direct
# intuition for why the 1998 supernova data ruled out a matter-only
# universe.

# Though I have realized post presenation, that holding the Hubble Constant to 68 would 
# be for a better fit. My 2292 class takes the Hubble Constant to be 68 whenever we do which 
# now makes so much sense. If we were to redo this, I would take the constant to be 68 instead.
# I don't feel like doing any more larger tweaks to the working code, but 70 works fine enough for 
# our visualization!


import matplotlib.pyplot as plt
import numpy as np
import streamlit as st

from src.app_utils import (
    get_supernova_dataframe,
    get_standardised_distance_moduli,
    configure_plot_style,
    format_cosmology_string,
    compute_deceleration_parameter,
    COLOR_DATA,
    COLOR_FIT,
    COLOR_EMPTY,
)
from src.models import SupernovaCosmologyModels


st.set_page_config(page_title="Interactive Cosmology", layout="wide")
configure_plot_style()


st.title("Interactive Cosmology")
st.markdown(
    "Set the three numbers that define the universe to anything."
    " The Hubble constant is the expansion rate today, Omega m is the matter content"
    "and Omega Lambda is the dark-energy content. The teal points are the measured supernovae "
    "and the yellow curve is the universe that was determined by the sliders"
)
st.markdown("---")

# -- Quick explainer ----------------------------------------------------

with st.expander("What does 'interactive' mean on this page?", expanded=False):
    st.markdown(
        """
        On the Hubble Diagram and Model Comparison pages, the curves
        are locked to specific combinations of parameters. On this
        page you control them directly. 
 
        A few things to try are listed below in the
        "Suggested experiments" section, each one shows a specific
        thing you can see with the sliders.
        """
    )
 
## the first few blocks of code need very little explanation, we created the title and description of the main page with a small
## expandable explanation of what this page is!

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

## The whole idea of this page is that you can play with the parameters yourself to see how any small changes might affect the best fit
## We have created sliders for Omega M and Lambda as well as the Hubble Constant, because even though we held the constant constant, it doesn't have to be that value
## each slider has a min, max, auto values, and a stepsize depending on the parameter
## Once again, if you are like I have no idea what these mean you can hover over a little ? in streamlit and it will give you a small note on the slider

with info_col:
    st.subheader("Diagnostics")

    total_density = matter_density + dark_energy_density
    q0 = compute_deceleration_parameter(matter_density, dark_energy_density)

## the total density should equal 1, addition of both matter and dark energy. This is only accounting for a flat universe
## our function compute_deceleration_parameter was defined in app_utils.py and we call it here to display the actual product of that computation
## depending on the parameters chosen, this all is shown off to the side next to the sliders.

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
            "q\u2080 = \u03A9\u2098/2 - \u03A9\u039B, from Ryden & "
            "Peterson eq. 24.37, neglecting radiation. Negative means "
            "the expansion is accelerating -- the 1998 discovery."
        ),
    )

## There are two things under the diagnostics display, one shows the Omega total, and the gross numbers and letters you see there is code to be 
## able to display the proper subscripts and greel letters.
## The second one displays the deceleration parameter, it will tell you if the universe based on the parameters is accelerating or decelerating and by how much
## If you omega total is above one, it will warn you that we cant really do that well since that would not be a flat universe like we are using.
## So we approximate it with the flat universe, so it is not helpful to have the sliders at anything above a total of 1.

    if abs(total_density - 1.0) > 0.05:
        st.caption(
            ":orange[Note: this model is not spatially flat. The code "
            "silently uses the flat-universe approximation, so curves "
            "shown are approximate for non-flat inputs.]"
        )

## This is where that warning is created

# -- Data and curves ----------------------------------------------------

dataframe = get_supernova_dataframe()
dataframe = get_standardised_distance_moduli(dataframe)
z_data = dataframe["redshift"].to_numpy()
mu_data = dataframe["mu"].to_numpy()

models = SupernovaCosmologyModels()

z_curve = np.logspace(
    np.log10(z_data.min() * 0.9), np.log10(z_data.max() * 1.1), 200
)

if matter_density < 1e-3 and dark_energy_density < 1e-3:
    mu_your_universe = models.calculate_empty_universe_model(
        z_curve, hubble_constant
    )
else:
    mu_your_universe = models.calculate_advanced_cosmological_model(
        z_curve, hubble_constant, matter_density, dark_energy_density,
    )

## when both denisty parameters are equal to 0, then 1/sqrt(0) is infinity, and that is not a good number for us.
## The closed form of calculate empty universe model uses a forumla that does not run into this problem.
## The threshold is 0.001 which is small enough to be effectively zero, so if the user meant 0, then they will get close enough.
## this just handles the case in which everything is set to 0.


mu_milne = models.calculate_empty_universe_model(z_curve, hubble_constant)

## this computes an empty universe with the same Ho that the user pciked as a reference curve always seen in the plot. 
## Without a reference, you cant tell if what you drew was correct or not. The line is always going to be off of the dataset, 
## it's not intended to be the correct fit, but it is for comparison to be able to see the correct fit. 

# -- Plot ---------------------------------------------------------------

fig, ax = plt.subplots(figsize=(11, 6))

## creates our figure!

ax.scatter(
    z_data, mu_data,
    color=COLOR_DATA, s=12, alpha=0.55, edgecolor="none",
    label=f"JLA data (n = {len(dataframe)})",
    zorder=1,
)
ax.plot(
    z_curve, mu_milne,
    color=COLOR_EMPTY, linewidth=1.6, linestyle="--",
    label="Empty universe (Milne)", zorder=2,
)
ax.plot(
    z_curve, mu_your_universe,
    color=COLOR_FIT, linewidth=2.4,
    label="Your universe", zorder=3,
)

## This plots our data as a scatter and then our always there empty universe fit, and then it will plot the universe the user calculated
## it's a lot of the same set up we've been seeing in the other pages. 

ax.set_xscale("log")
ax.set_xlabel("Redshift z")
ax.set_ylabel("Distance modulus $\\mu$")
ax.set_title(format_cosmology_string(
    hubble_constant, matter_density, dark_energy_density
))
ax.legend(loc="lower right")

st.pyplot(fig, clear_figure=True)


# -- Structured experiments --------------------------------------------

st.markdown("### Suggested experiments")
st.markdown(
    "Each block below asks you to try a specific parameter combination "
    "and tells you what to look for. Move the sliders above to match, "
    "then read the expected outcome."
)
 
with st.expander(
    "Experiment 1 -- Turn dark energy OFF (reproduce pre-1998 expectations)",
    expanded=False,
):
    st.markdown(
        """
        **Set:** ``Omega_m = 1.00``,  ``Omega_Lambda = 0.00``,
        ``H_0 = 70``
 
        **Watch:** the yellow curve will drop noticeably below the data
        points at high redshift (``z > 0.3``).
 
        **Why this matters:** this is the "matter-only" or
        Einstein-de Sitter universe, what cosmologists thought the
        universe was like before 1998. The curve fails to reach the
        observed supernovae, meaning a matter-only universe predicts
        those supernovae should look **brighter** than they actually
        do. That disagreement, repeated across dozens of supernovae at
        the time, is what forced the Nobel-prize-winning conclusion
        that dark energy must be real.
 
        **Check your q0:** should be ``+0.50`` (decelerating).
        """
    )
 
with st.expander(
    "Experiment 2 -- Turn dark energy ON (the universe as we think it now)",
    expanded=False,
):
    st.markdown(
        """
        **Set:** ``Omega_m = 0.30``,  ``Omega_Lambda = 0.70``,
        ``H_0 = 70``
 
        **Watch:** the curve lands on top of the data.
 
        **Why this matters:** these are the Dark Energy consensus
        values. Together they predict that the universe contains 30%
        matter and 70% dark energy. The close agreement between
        curve and data is the reason this combination is called the
        "standard model of cosmology."
 
        **Check your q0:** should be ``-0.55`` (accelerating).
        """
    )
 
with st.expander(
    "Experiment 3 -- The Hubble tension",
    expanded=False,
):
    st.markdown(
        """
        **Keep densities at consensus** (``Omega_m = 0.30``,
        ``Omega_Lambda = 0.70``) **and drag H_0 slowly from 67 to 73.**
 
        **Watch:** the curve shifts vertically -- it does not change
        shape, it just moves up or down.
 
        **Why this matters:** both 67 (Planck) and 73 (SH0ES) are
        within the scatter of the data, but their quoted uncertainties
        don't overlap. The shape of the curve doesn't tell you which H_0 is right.
        """
    )
 
with st.expander(
    "Experiment 4 -- An empty universe",
    expanded=False,
):
    st.markdown(
        """
        **Set:** ``Omega_m = 0.00``,  ``Omega_Lambda = 0.00``
 
        **Watch:** the yellow curve collapses onto the blue
        dashed Milne reference curve.
 
        **Why this matters:** with no matter and no dark energy, the
        universe just expands at a steady rate (the Milne model). The
        data sit slightly above this curve at high redshift, telling
        you the universe contains *something* -- it isn't empty. The
        other experiments show *what* it contains.
 
        **Check your q0:** should be ``0.000`` (neither accelerating
        nor decelerating).
        """
    )
 
## finally, this is just an unnecessary but neat little section on suggested universes you could create with the sliders.
## each expierment would show you something about the data, and I feel as though the point is more easilt understood if you get
## to manipulate the variables yourself and see why changing certain ones get you different results
## I took inspiration from our last project with the tour guide and I thought it would be nice to have a similar thing here.