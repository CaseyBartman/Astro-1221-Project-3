"""
Domain constants and file configurations.
"""

# -------------- API & File Paths --------------
SUPERNOVA_JSON_URL = "https://www.wolframcloud.com/download/da019e5f-cb37-4061-b899-cbca009a6b51?filename=Type-Ia-Supernova-Data.json"
JSON_FILENAME = "supernovas.json"
LOG_FILENAME = "supernovas_log.txt"

# -------------- Wolfram Parsing Constants --------------
WOLFRAM_STRING_QUOTE = "'"

# -------------- Supernova Data Columns --------------
SUPERNOVA_KEYS = {
    'NAME': 'supernova name',
    'REDSHIFT': 'redshift',
    'MAGNITUDE': 'magnitude',
    'STRETCH': 'stretch',
    'COLOR': 'color'
}

NUMERICAL_PHYSICS_COLUMNS = [
    SUPERNOVA_KEYS['REDSHIFT'],
    SUPERNOVA_KEYS['MAGNITUDE'],
    SUPERNOVA_KEYS['STRETCH'],
    SUPERNOVA_KEYS['COLOR']
]

# -------------- Physics & Cosmological Constants --------------
# -------------- Physics & Cosmological Constants --------------
SPEED_OF_LIGHT_KM_S = 299792.458 

# Distance Modulus Formula Constants (\mu = 5 * log10(d) + 25)
DISTANCE_MODULUS_LOG_MULTIPLIER = 5.0
DISTANCE_MODULUS_OFFSET = 25.0

# Standardization (Tripp Relation) Baseline Guesses
# These are standard initial approximations for Type Ia supernovae
TRIPP_ALPHA = 0.14
TRIPP_BETA = 3.1
ABSOLUTE_MAGNITUDE_M = -19.3

# -------------- Optimizer Initial Guesses --------------
# Best current estimates from Planck 2018 / local distance ladder
INITIAL_HUBBLE_CONSTANT_GUESS = 70.0 ## km/s/Mpc
INITIAL_MATTER_DENSITY_GUESS = 0.3 ## Omega_m (no dimensions)
INITIAL_DARK_ENERGY_DENSITY_GUESS = 0.7 ## Omega_Lambda (no dimensions)
