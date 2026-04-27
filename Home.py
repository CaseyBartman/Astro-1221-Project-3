
# Type Ia Supernova Hubble Diagram -- Streamlit Application
# =========================================================

# Main entry point and home page for the app!
# Run from the project with::

#     streamlit run Home.py

# Project structure:
#     Home.py                         
#     pages/                         
#       1_Data_Explorer.py         
#       2_Hubble_Diagram.py          
#       3_Model_Comparison.py        
#       4_Interactive_Cosmology.py   
#       5_Methodology.py             
#     src/                           
#     pipeline_tester.py             

#     Lauren Bryant (Streamlit application and astronomical verification).


## This is bascially just visualization for the home page of the Streamlit app. 

import streamlit as st
from src.app_utils import get_supernova_dataframe, COLOR_FIT, COLOR_DATA

# -- Page configuration -- must be the first Streamlit call ---------------

st.set_page_config(
    page_title="Home",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)

## Sets up the title of the page in the sidebar, sets up how I want the page to be set up.

# -- Header --------------------------------------------------------------

st.title("Type 1a Supernova Hubble Diagram")
st.markdown(
    f"<p style='color:{COLOR_FIT}; font-size:1.1rem; font-style:italic; "
    f"margin-top:-0.75rem;'>"
    "The observations that revealed cosmic acceleration."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("---")

## This sets up the Heading and Subheading on the actual page, not the sidebar like the code up above.
## Eveytime you see the st.markdown("---") that's just creating a small bar below the writing to seperate the different parts

# -- Left column: narrative ----------------------------------------------

narrative_col, stats_col = st.columns([3, 2], gap="large")

## st.columns creates two side-by-side containers for whatever, so we put the narrative next to our stats column
## at a 3:2 ratio, the narrative column is 1.5 times wider than the other column

with narrative_col:
    st.header("What is our Project?")
    st.markdown(
        """
        In 1988, findings of Type Ia supernovae showed that these supernovae were fainter than expected
        Type Ia supernovae come from explosions of white dwarfs at the end of their lifespan which produce consistent luminosity.
        They are considered "standard candles", they are predictable. However, with data showing these "standard candles" as fainter
        than calculated IF the universe was not expanding. The teams that worked on this project were able to show that
        the universe was not slowing down due to gravity but rather accelerating due to an unknown force. Dark Energy. In 2011, one half of a Nobel Prize was awarded to 
        Saul Perlmutter, and the other half between Brain P. Schmidt and Adam G. Riess. Their work is observational evidence of what we now call dark energy.

        This project attempts to reproduce this anaylsis using the JLA SN Ia 
        compilation: 580 Type Ia supernovae spanning redshifts from
        ``z = 0.015`` to ``z > 1``. We wanted to make it interactive to be able to see exactly how researchers came to their conclusions.
        You can explore how the matter density and dark-energy density change the predicted relationship between distance and redshift of the standard candles.
        
        """
    )

    st.header("How to Navigate")
    st.markdown(
        """
        Use the sidebar to move between pages.

        - **Data Explorer** -- examine the dataset. Look through the 732 supernovae,
          search by name, filter by redshift, and see the measurements actually mean.
        - **Hubble Diagram** -- the classic plot. Distance modulus versus
          redshift, overlaid with the best-fit expansion model. You can pick between three
          different fits to see how the answer depends on what you assume.
        - **Model Comparison** -- three different universes drawn together.
          This is where the presence of dark energy becomes visually obvious.
        - **Interactive Cosmology** -- drag the sliders for ``H_0``,
          ``Omega_m``, and ``Omega_Lambda`` and watch the predicted curve
          bend. This is the clearest way to understand what the
          1998 discovery actually looked like.
        - **Methodology** -- a written record of the physics with references 
          to Ryden & Peterson, Tripp 1998, Hogg 1999, and the Nobel press release.
        """
    )

## This sets up what is called the narrative column, this tells us about our project and how to navigate 
## our streamlit app. It was very straightforward and the only thing was typing all of the descriptions. 

# -- Right column: quick stats ------------------------------------------

with stats_col:
    st.header("Dataset at a glance")
    try:
        df = get_supernova_dataframe()
        n_supernovae = len(df)
        z_min, z_max = df["redshift"].min(), df["redshift"].max()

        st.metric("Supernovae loaded", f"{n_supernovae:,}")
        st.metric("Minimum redshift", f"z = {z_min:.3f}")
        st.metric("Maximum redshift", f"z = {z_max:.3f}")
        st.caption(
            "Source: Betoule et al. 2014 (JLA), via the Wolfram Data "
            "Repository. See the Methodology page for full citations."
        )
    except Exception as error:
        st.warning(
            "Dataset not yet loaded. Click below to fetch the Union2.1 "
            "compilation from the Wolfram Data Repository."
        )
        st.caption(f"(Details: {error})")
        if st.button("Download dataset now"):
            get_supernova_dataframe.clear()
            st.rerun()

## this one is a little more confusing than our narrative column since it is not just wording.
ADD MORE HERE

# -- Footer --------------------------------------------------------------

st.markdown("---")
st.markdown(
    f"<p style='color:{COLOR_DATA}; font-size:0.9rem;'>"
    "ASTRO 1221 Project 3 &nbsp;|&nbsp; "
    "Casey Bartman, Lauren Bryant, and Andrew Schlemmer"
    "</p>",
    unsafe_allow_html=True,
)

## The last thing on our front page is a small footer, with the title of our Project/our names

# Little script for myself for presenting Wednesday - delete before turn in
# ---Home
# This page is a broad overview of what the project is, the Nobel Prize it was based on, and the findings they uncovered. 
# We want to reproduce the findings that led to the 2011 Nobel Prize by using the Joint Light-curve Analysis or the JLA compilation of about 732 Type Ia supernovae. 
# Since Type Ia supernovae act as standard candles, they are good for determining precise astronomical distances.
# The Chandrasekhar Mass limit is the mass at which a white dwarf reaches exactly 1.44 times the mass of the Sun, collapses, triggers carbon fusion, and then 
# blows up as a Type Ia supernova. Type Ia supernovae are the explosions of these white dwarfs at the end of their lifetime, and their intrinsic peak of luminosity
#  is incredibly predictable, which is why we can make such precise calculations for their distances. JLA specifically combined data from multiple major surveys to 
#  create a more comprehensive range of redshifts than, for example, Union 2.1, which we had previously looked at.
# The Tripp relation was huge in the work determining that the universe was actually accelerating. If astronomers use the raw, uncorrected brightness to calculate
#  distance from the Type Ia supernovae, the data would be noisy so that any kind of signature of dark energy would be drowned out. In 1998, there was an astronomer 
#  named Robert Tripp who found a way to clean the data, and he noticed two things called the stretch factor and the color factor that we will see in the next pages.
# ----Data Explorer
# This is a large table of all of the Type Ia supernovae in the JLA compilation. Each row is home to one supernova by name, and it includes elements of redshift, 
# magnitude, stretch, color, and mu. The mu refers to the distance modulus; it is the Tripp standardized distance using values of magnitude, stretch, and color.
# We see numbers between roughly 38 and 45. A mu of 33 to about 34 is our local universe, so this would be the bottom left of our Hubble diagram that you will see 
# later. This corresponds to supernovae that are roughly 40 to 60 megaparsecs away; they're considered nearby neighbors even though megaparsecs is very not close. 
# A mu of about 44, which is our upper end of supernovae, is the distant universe.
# The stretch parameter refers to the width of the supernova's light curve, which is basically a plot of its brightness over time. A high stretch supernova takes 
# longer to reach its peak brightness and takes longer to fade away. There's a lot of physics that I don't really understand that goes into why broader light curves 
# mean it's intrinsically brighter, but it does. And for the color parameter, the color is the difference between how bright the supernova looks in a blue filter versus
#  a visual green filter. A positive number means it's redder, and a negative number means it's bluer.
# As stated on the homepage, the supernovae have redshifts between about 0.01 to 1.3. Redshift z has a direct relationship to something called a scale factor. The 
# scale factor is the physical size of the universe, and we define the size of the universe today to be a=1. The relationship is 1 + z = 1/a(t). So with a redshift 
# of zero or really close to zero, the universe is 100% or a little less of its current size. Supernovae with really small redshifts are our anchor points towards 
# the bottom left of the Hubble diagram. The light has only been traveling for a few hundred million years. Since the light hasn't been traveling long enough for 
# the expansion of the universe to change its speed much, dark energy is totally invisible here.
# With a redshift of about 0.5, the universe was about 2/3 its current size, meaning the light has been traveling for roughly 5 billion years. This is a critical zone where the matter-only universe curve and the dark energy curve begin to noticeably shift away from each other. And when we get to redshifts of one, maybe a little bit more, the universe is about half the size it was, and our upper end of redshifts was about 1.3, so the universe was even smaller than that. These supernovae are the faintest, most hardest to find; they exploded over 9 billion years ago. If the universe were matter-only and there was no dark energy, these supernovae would still be bright because gravity would keep them relatively close. Since they are faint, this is one thing that helps us prove that the universe is accelerating.
# -----Hubble Diagram
# Here we have the distance modulus graphed against the logarithmic redshift. We use a log scale on the x-axis because if we used a normal linear scale, all our 
# local supernovae would be cramped into a giant blob on the left and we wouldn't be able to see anything. The log scale stretches it out so we can actually see the 
# different universe models start to disagree at higher distances.
# This is really the core of the whole project. We are plotting distance against redshift. Again, redshift is basically a measure of how much the universe has 
# stretched since the supernova exploded. The really important part here is the residuals panel at the bottom. If the universe was just filled with gravity and 
# matter, the data points for the distant supernovae would trend upwards, meaning they would be brighter and closer than they actually are. But they aren't; they
#  are fainter, and that faintness is the direct proof that some weird force is pushing them further away, which later got called dark energy.
# ----Model Comparison
# This tab is here to answer the question: are we sure it's dark energy? We plot three totally different universes over our data: an empty one, a gravity-only 
# one, and our current model which has dark energy.
# For nearby supernovae, all three curves look identical because the light hasn't traveled enough to care about the universe's expansion history. But when you 
# look at the distant stuff, the gravity-only universe completely misses the data points. The only way to make the line fit the data is to add dark energy into 
# the math. We wanted to include an empty universe to act as a baseline; it's a universe that is not slowing down or speeding up, so we can easily compare it to 
# ones we want to look at. Because the data points clearly curve away from that baseline, we know that for a fact this universe has stuff in it actively messing 
# with the expansion rate. So if the empty universe somehow fit the data well, then we knew something was wrong.
# -----Interactive Cosmology
# Instead of just looking at static graphs, this tab lets you build your own universe. You get sliders to change how much matter, dark energy, and how fast it's 
# expanding with the Hubble constant. As you drag sliders, the math recalculates and you can watch the curve bend with the data.
# We also calculate the deceleration parameter, which acts as a speedometer. If it's negative, your universe is actively accelerating, and if it's positive, then
#  it's decelerating. This deceleration parameter basically tells you which force is winning, is it gravity or is it dark energy. If it's positive, then gravity 
#  is winning and the universe is slowing down, and if it's negative, dark energy is winning and the universe is accelerating.
# ----Methodology
# This is the documentation for the actual code running in the background. It explains how we use Python to run the Tripp corrections and integrate the expansion
#  equations. One of the biggest hurdles was dealing with degeneracy in the math. In the formula, the Hubble constant and the absolute brightness of the supernovae 
#  are tangled together. If you let the computer try to solve both at once, it freaks out because it can't tell the difference between the universe is expanding 
#  faster and the star is inherently brighter. To get this code to actually work, we need to make sure that the Hubble constant is a constant and it's set in place.
# When I say that the Hubble constant and the absolute magnitude are degenerate, I mean that in the distance modulus equation they combine into a single term. 
# So the computer can't tell exactly what that term is trying to say, so we fix one of the parameters, then it has to solve for the other parameter.
# We did not include radiation in our calculations of the universe. Radiation mattered right after the Big Bang, but at the time frame we are looking at, 
# it has zero effect for us at least.
