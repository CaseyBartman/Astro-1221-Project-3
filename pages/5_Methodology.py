"""
Methodology page
================

Written record of the physics and computational methodology used in
this project. Functions as the astronomical verification record."""

import streamlit as st

from src.app_utils import configure_plot_style, COLOR_FIT


st.set_page_config(page_title="Methodology", layout="wide")
configure_plot_style()


st.title("Methodology")
st.markdown(
    "A written record of what the code computes, what was checked, and "
    "what had to be corrected. Each physics claim is tied to a reference "
    "and, where the reference is the course textbook (Ryden & Peterson), "
    "to a specific chapter and equation number."
)
st.markdown("---")


# -- Dataset -----------------------------------------------------------
st.header("1. Dataset")
st.markdown(
     """
    This project uses the **JLA compilation** of Type Ia supernovae
    published by Betoule et al. 2014 (A&A 568, A22). (the Joint
    Light-curve Analysis) JLA succeeds the older Union2.1 compilation (Suzuki et al. 2012)
    as the preferred standard for supernova cosmology analyses, and our
    pipeline retrieves it from the Wolfram Data Repository (Bradley
    2022). The compilation extends from local supernovae at
    ``z = 0.01`` through HST discoveries near ``z = 1.3``, which is
    precisely the redshift range needed to detect the signature of
    cosmic acceleration.
 
    After cleaning, 732 supernovae remain in the sample. The raw records
    contain four physical columns for each supernova:
 
    - ``redshift`` -- heliocentric redshift z.
    - ``magnitude`` -- peak apparent brightness in the B band, ``m_B``.
    - ``stretch`` -- the SALT2 light-curve stretch parameter s, measuring
      how slowly the supernova fades after peak. Values are centred
      near one.
    - ``color`` -- the SALT2 Color parameter c, approximately the
      dereddened (B - V) Color at peak. Centred near zero.
    """
)


# -- Standardisation ---------------------------------------------------
st.header("2. Standardising the supernovae: the Tripp relation")
st.markdown(
    """
    Type Ia supernovae are near-standard candles, so their intrinsic peak
    luminosities are similar but not identical. The empirical correlations
    that tighten them into usable standard candles were first formalised
    by Tripp (1998, A&A 331, 815), who showed that supernovae with
    broader light curves (higher stretch) are intrinsically more luminous,
    and supernovae that are redder at peak (higher Color c) are
    intrinsically fainter. Correcting for these two trends reduces the
    scatter in peak luminosity from around 0.3 mag to roughly 0.12 mag.

    The Tripp correction used in this project is implemented in
    ``SupernovaCosmologyModels.calculate_distance_modulus``:
    """
)
st.latex(
    r"\mu \;=\; m_B \;+\; \alpha\,(s - 1) \;-\; \beta\,c \;-\; M"
)
st.markdown(
    """
    with nuisance parameters held at standard SALT2 values
    ``alpha = 0.14``, ``beta = 3.1``, and absolute magnitude
    ``M = -19.3`` mag. The sign convention follows Tripp (1998) and
    Mandel et al. (2017, ApJ 842, 93).

    **note.** The original implementation used ``alpha * s`` rather
    than ``alpha * (s - 1)``. Because the JLA stretch values are
    centred near one rather than zero, this introduced a constant offset
    of ``alpha * 1 = 0.14`` mag which would have been absorbed into an
    effective absolute magnitude during fitting. The correction was made
    to preserve the literal interpretation of M = -19.3 as the true
    absolute peak magnitude.
    """
)


# -- Cosmological distance ---------------------------------------------
st.header("3. Predicting distance modulus from cosmology")
st.markdown(
    """
    Type Ia supernovae tell us cosmology because the distance modulus
    varies with redshift in a way that depends on the geometry and
    contents of the universe. Following Ryden & Peterson eq. 24.35 and
    Hogg 1999 (arXiv:astro-ph/9905116), for a spatially flat universe
    dominated by matter and a cosmological constant, the luminosity
    distance is:
    """
)
st.latex(
    r"d_L(z) \;=\; (1 + z)\,\frac{c}{H_0}"
    r"\int_{0}^{z}\frac{dz'}{E(z')}"
)
st.latex(
    r"E(z) \;=\; \sqrt{\Omega_m (1+z)^3 \;+\; \Omega_\Lambda}"
)
st.markdown(
    """
    and the observed distance modulus follows from the standard
    logarithmic definition (Ryden & Peterson eq. 13.25):
    """
)
st.latex(
    r"\mu \;=\; 5\,\log_{10}\!\left(\frac{d_L}{1\,\text{Mpc}}\right) \;+\; 25"
)
st.markdown(
    """
    This is what ``SupernovaCosmologyModels.calculate_advanced_cosmological_model``
    computes. The integral is evaluated numerically with ``scipy.integrate.quad``.

    **Approximations.** We could take a couple shortcuts. Radiation density ``Omega_r`` is neglected. It
    contributes at the ``10^-5`` level to the total energy budget today
    and never reaches 1% importance below ``z ~ 3400``, far above any
    redshift in the supernova sample. Spatial curvature ``Omega_k`` is
    also assumed to vanish. Lambda-CDM-like fits respect this, but if
    the user explores combinations with ``Omega_m + Omega_Lambda`` far
    from one on the Interactive Cosmology page, the curve shown is a
    flat-universe approximation and not the true non-flat prediction.

    #### The low-redshift (empty-universe) limit

    For very low redshifts the cosmological integral becomes trivial, and
    the luminosity distance reduces to the **empty-universe**
    (**Milne**) closed form:
    """
)
st.latex(
    r"d_L(z) \;=\; \frac{c \, z \, (1 + z)}{H_0} "
    r"\qquad (\Omega_m = \Omega_\Lambda = 0)"
)
st.markdown(
    """
    In the further ``z << 1`` limit this reduces again to
    ``d_L ~ c z / H_0``, recovering the classical Hubble law
    (Ryden & Peterson eq. 20.30). This is what the
    ``calculate_empty_universe_model`` method returns.

    **note.** The original implementation of this method did not use
    the ``(1 + z)`` factor entirely, using only ``d_L = c z / H_0``. The
    missing factor is small at ``z < 0.05`` but reaches
    ``5 log(1.5) ~ 0.88`` mag at ``z = 0.5``. This is larger than the
    dark-energy signature itself (about 0.25 mag at z = 0.5), so the
    uncorrected curve would have been systematically displaced from the
    data in a way that would confound any comparison to the data. The
    correction aligns the function with Ryden & Peterson eq. 24.42.
    """
)


# -- Fitting -----------------------------------------------------------
st.header("4. Fitting the data")
st.markdown(
    """
    With the distance-modulus-versus-redshift relation in hand, the task
    is to find the cosmological parameters ``(H_0, Omega_m, Omega_Lambda)``
    that best reproduce the observed ``(z_i, mu_i)`` points from the
    JLA compilation. This is a standard non-linear least-squares
    problem, which in this project is solved using ``scipy.optimize.curve_fit``. The
    optimiser returns the best-fit parameters and their covariance
    matrix, parameter uncertainties are the square roots of the diagonal
    covariance entries.

     **Three fit strategies.** ``src/optimizer.py`` provides three
    complementary fits:
 
    - ``fit_empty_universe_hubble`` -- one free parameter (``H_0``)
      using the closed-form empty-universe model. The classical
      benchmark.
    - ``fit_density_parameters`` -- two free parameters
      (``Omega_m``, ``Omega_Lambda``) with ``H_0`` held fixed. This
      matches the standard Perlmutter/Riess 1998 analyses, for a
      specific physical reason: ``H_0`` and the absolute magnitude
      ``M`` of the standardised supernovae enter the predicted
      ``mu(z)`` only through the combination ``M - 5*log10(H_0)``.
      They are perfectly degenerate in a supernova-only fit.
      Attempting to fit both at once produces a near-singular
      covariance matrix and uncertainty estimates that blow up.
      Fixing ``H_0`` is the principled solution.
    - ``fit_flat_universe`` -- one free parameter (``Omega_m``)
      with flatness enforced (``Omega_Lambda = 1 - Omega_m``). The
      tightest one-number answer the data can give.

    Whether it was a good fit is characterised by reduced chi-squared: the sum of
    squared residuals weighted by the per-point uncertainty, divided by
    the number of degrees of freedom. JLA
    reports per-supernova distance-modulus uncertainties in the
    0.12-0.25 mag range; a single-number stand-in of ``sigma_mu =
    0.15`` mag is used here. Incorporating the per-point
    uncertainties is a future enhancement.
    """
)


# -- References --------------------------------------------------------
st.header("5. References")
st.markdown(
    f"""
    <div style='border-left:4px solid {COLOR_FIT}; padding-left:1rem;'>
    <p>
    <strong>Ryden, B. &amp; Peterson, B. M.</strong> (2010).
    <em>Foundations of Astrophysics</em>. Pearson.
    </p>
    <p>
    <strong>Tripp, R.</strong> (1998). "A two-parameter luminosity
    correction for Type Ia supernovae,"
    <em>Astronomy and Astrophysics</em>, 331, 815.
    </p>
    <p>
    <strong>Hogg, D. W.</strong> (1999). "Distance measures in cosmology,"
    arXiv:astro-ph/9905116.
    </p>
    <p>
    <strong>Mandel, K. S., Scolnic, D. M., Shariff, H., Foley, R. J., &amp;
    Kirshner, R. P.</strong> (2017). "The Type Ia supernova
    color-magnitude relation and host galaxy dust: a simple
    hierarchical Bayesian model,"
    <em>The Astrophysical Journal</em>, 842, 93.
    </p>
    <p>
    <strong>Betoule, M., et al.</strong> (2014). "Improved
    cosmological constraints from a joint analysis of the SDSS-II and
    SNLS supernova samples,"
    <em>Astronomy &amp; Astrophysics</em>, 568, A22. arXiv:1401.4064.
    </p>
    <p>
    <strong>Bradley, M.</strong> (2022). "Type Ia Supernova Data,"
    <em>Wolfram Data Repository</em>.
    https://datarepository.wolframcloud.com/resources/Type-Ia-Supernova-Data/
    </p>
    <p>
    <strong>The Royal Swedish Academy of Sciences</strong> (2011).
    "The 2011 Nobel Prize in Physics -- press release."
    https://www.nobelprize.org/prizes/physics/2011/press-release/
    </p>
    </div>
    """,
    unsafe_allow_html=True,
)
