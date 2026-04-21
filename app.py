"""
Type Ia Supernova Hubble Diagram -- Streamlit Application
=========================================================

Main entry point and home page for the app!
Run from the project with::

    streamlit run app.py

Project structure:
    app.py                         
    pages/                         
      1_Data_Explorer.py         
      2_Hubble_Diagram.py          
      3_Model_Comparison.py        
      4_Interactive_Cosmology.py   
      5_Methodology.py             
    src/                           
    pipeline_tester.py             

    Lauren Bryant (Streamlit application and astronomical verification).
"""

import streamlit as st
from src.app_utils import get_supernova_dataframe, Color_FIT, Color_DATA


# -- Page configuration -- must be the first Streamlit call ---------------
st.set_page_config(
    page_title="Type Ia Supernova Hubble Diagram",
    page_icon=None,
    layout="wide",
    initial_sidebar_state="expanded",
)


# -- Header --------------------------------------------------------------
st.title("Type Ia Supernova Hubble Diagram")
st.markdown(
    f"<p style='color:{Color_FIT}; font-size:1.1rem; font-style:italic; "
    f"margin-top:-0.75rem;'>"
    "The observations that revealed cosmic acceleration."
    "</p>",
    unsafe_allow_html=True,
)

st.markdown("---")


# -- Left column: narrative ----------------------------------------------
narrative_col, stats_col = st.columns([3, 2], gap="large")

with narrative_col:
    st.header("What is our Project?")
    st.markdown(
        """
        In 1988, findings of Type 1a supernovae showed that these supernovae were fainter than expected
        Type 1a supernovae come from explosions of white dwarfs at the end of their lifespan which produce consistent luminosity.
        They are considered "standard candles", they are predictable. However, with data showing these "standard candles" as fainter
        than calculated IF the universe was not expanding. The teams that worked on this project were able to show that
        the universe was not slowing down due to gravity but rather accelerating due to an unknown force. Dark Energy. In 2011, one half of a Nobel Prize was awarded to 
        Saul Perlmutter, and the other half between Brain P. Schmidt and Adam G. Riess. Their work is observational evidence of what we now call dark energy.

        This project attempts to reproduce this anaylsis using the JLA SN 1a 
        compilation: 580 Type Ia supernovae spanning redshifts from
        ``z = 0.015`` to ``z > 1``. We wanted to make it interactive to be able to see exactly how researchers came to their conclusions.
        You can explore how the matter density and dark-energy density change the predicted relationship between distance and redshift of the standard candles.
        
        """
    )

    st.header("How to Navigate")
    st.markdown(
        """
        Use the sidebar to move between pages.

        - **Data Explorer** -- examine the dataset. Lokk through the 732 supernovae,
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


# -- Footer --------------------------------------------------------------
st.markdown("---")
st.markdown(
    f"<p style='color:{Color_DATA}; font-size:0.9rem;'>"
    "ASTRO 1221 Project 3 &nbsp;|&nbsp; "
    "Casey Bartman, Lauren Bryant, and Andrew Schlemmer"
    "</p>",
    unsafe_allow_html=True,
)
