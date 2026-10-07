"""
Input Data - General
"""

# Define a dictionary for the allowed units to entered the mass of polymer
MASS_UNITS_POLYMER = {
    "Grams": {
        "unit": "g", 
        "precision": 2,
        "conv_fact_to_std_unit": 1/1000},
    "Kilograms": {
        "unit": "kg", 
        "precision": 2,
        "conv_fact_to_std_unit": 1}
}
