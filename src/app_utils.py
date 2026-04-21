"""
Shared helpers for the Streamlit application.

All Streamlit pages import from this module so that data loading is cached
(avoiding repeated downloads and re-parsing of the Union2.1 JSON file) and
so that plots across pages share a consistent visual style.

Author:
    Lauren Bryant 
Contents:
    get_supernova_dataframe   
    configure_plot_style        
    format_cosmology_string     
    compute_deceleration_param  
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import streamlit as st

from src.data_loader import SupernovaDataLoader
from src.data_processor import SupernovaDataProcessor
from src.models import SupernovaCosmologyModels
from src.constants import SUPERNOVA_KEYS, JSON_FILENAME


# -- Colour palette (matches .streamlit/config.toml) ----------------------
COLOUR_BACKGROUND = "#0a1628"
COLOUR_PANEL      = "#13233a"
COLOUR_TEXT       = "#e8eef5"
COLOUR_MUTED      = "#7a8ba3"
COLOUR_DATA       = "#4ecdc4"   # teal -- observed supernovae
COLOUR_FIT        = "#ffa62b"   # amber -- best-fit / consensus
COLOUR_EMPTY      = "#a17cd9"   # violet -- empty (Milne) universe
COLOUR_MATTER     = "#e65a7a"   # rose   -- matter-only (Einstein-de Sitter)
COLOUR_GRID       = "#1f3350"


@st.cache_data(show_spinner="Fetching the Union2.1 supernova compilation...")
def get_supernova_dataframe():
    """
    Load, parse, and clean the Type Ia supernova dataset. Downloads the
    Wolfram-hosted JSON if it is not already present in the project root,
    then flattens it into a Pandas DataFrame with numeric physics columns.

    The result is cached by Streamlit so repeat page navigations do not
    re-trigger the download.

    Returns
    -------
    pd.DataFrame
        Columns: ``supernova name``, ``redshift``, ``magnitude``,
        ``stretch``, ``color``. All physical columns are ``float``.
    """
    loader = SupernovaDataLoader()
    processor = SupernovaDataProcessor()

    # Only download if the file does not already exist locally; this keeps
    # subsequent runs fast and lets the app work offline after first use.
    if not Path(JSON_FILENAME).exists():
        loader.fetch_and_save_json()

    raw_records = loader.parse_supernova_objects()
    dataframe = processor.process_raw_records(raw_records)
    return dataframe


@st.cache_data
def get_standardised_distance_moduli(dataframe):
    """
    Apply the Tripp relation to the cleaned dataset and return distance moduli.

    This wraps ``SupernovaCosmologyModels.calculate_distance_modulus`` and
    attaches the result as a new column ``mu`` without mutating the input
    DataFrame.

    Parameters
    ----------
    dataframe : pd.DataFrame
        The output of ``get_supernova_dataframe``.

    Returns
    -------
    pd.DataFrame
        Copy of the input with an added ``mu`` column (Tripp-standardised
        distance modulus, dimensionless / magnitudes).
    """
    models = SupernovaCosmologyModels()
    result = dataframe.copy()
    result["mu"] = models.calculate_distance_modulus(
        result[SUPERNOVA_KEYS["MAGNITUDE"]],
        result[SUPERNOVA_KEYS["STRETCH"]],
        result[SUPERNOVA_KEYS["COLOR"]],
    )
    return result


def configure_plot_style():
    """
    Apply the observatory dark theme to matplotlib so plots blend with the
    Streamlit dark background.

    Should be called once at the top of each page, after ``st.set_page_config``.
    """
    plt.rcParams.update({
        "figure.facecolor":  COLOUR_BACKGROUND,
        "axes.facecolor":    COLOUR_PANEL,
        "axes.edgecolor":    COLOUR_MUTED,
        "axes.labelcolor":   COLOUR_TEXT,
        "axes.titlecolor":   COLOUR_TEXT,
        "axes.grid":         True,
        "grid.color":        COLOUR_GRID,
        "grid.linestyle":    ":",
        "grid.alpha":        0.6,
        "xtick.color":       COLOUR_MUTED,
        "ytick.color":       COLOUR_MUTED,
        "text.color":        COLOUR_TEXT,
        "legend.facecolor":  COLOUR_PANEL,
        "legend.edgecolor":  COLOUR_MUTED,
        "legend.labelcolor": COLOUR_TEXT,
        "font.family":       "serif",
        "font.size":         11,
        "axes.titlesize":    13,
        "axes.titleweight":  "normal",
    })


def format_cosmology_string(hubble_constant, matter_density, dark_energy_density):
    """
    Build a short human-readable label describing a cosmological model.

    Parameters
    ----------
    hubble_constant : float
        H0 in km/s/Mpc.
    matter_density : float
        Omega_m (dimensionless).
    dark_energy_density : float
        Omega_Lambda (dimensionless).

    Returns
    -------
    str
        E.g. ``"H0 = 70.0 | Omega_m = 0.30 | Omega_L = 0.70"``.
    """
    return (
        f"H\u2080 = {hubble_constant:.1f} km/s/Mpc   "
        f"\u03A9\u2098 = {matter_density:.2f}   "
        f"\u03A9\u039B = {dark_energy_density:.2f}"
    )


def compute_deceleration_parameter(matter_density, dark_energy_density):
    """
    Compute the present-day deceleration parameter q0.

    From Ryden & Peterson eq. 24.37, neglecting radiation (which is valid
    for all supernova redshifts), the acceleration of the scale factor at
    the present epoch is proportional to ``-Omega_m/2 + Omega_Lambda``.
    The deceleration parameter is conventionally defined with a sign
    flip so that q0 > 0 means the expansion is slowing down:

        q0 = Omega_m / 2 - Omega_Lambda

    A negative q0 indicates an accelerating universe -- which is exactly
    what the 1998 Type Ia supernova observations discovered.

    Parameters
    ----------
    matter_density : float
        Omega_m (dimensionless).
    dark_energy_density : float
        Omega_Lambda (dimensionless).

    Returns
    -------
    float
        Deceleration parameter at the present epoch (dimensionless).
    """
    return matter_density / 2.0 - dark_energy_density
