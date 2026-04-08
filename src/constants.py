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
# Expected CSV Column Names
columnSupernovaName = "name"
columnRedshiftValue = "redshift"
columnApparentMagnitude = "magnitude"
columnStretchFactor = "stretch"
columnColorValue = "color"

# Expected Output Data Columns (After Standardization)
columnDistanceModulus = "distance_modulus"
columnDistanceModulusError = "distance_modulus_error"

# Physics Constants
speedOfLightKilometersPerSecond = 299792.458

