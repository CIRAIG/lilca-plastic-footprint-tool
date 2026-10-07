"""
Input Data - MarILCA
"""

import pandas as pd

#==================================================================
# 🎚️ Characterization Factors (CFs) at endpoint
#==================================================================

CF_TABLE = pd.read_parquet("./data/processed/cfs_endpoint_midpoint.parquet")

# Derived data from CFs table
COMPARTMENTS =  sorted(CF_TABLE['emission_compartment'].unique())

PARTICLE_SHAPES = sorted(CF_TABLE['shape'].unique())

AVAILABLE_SIZES = CF_TABLE['size'].unique().tolist()

CF_INDICATOR_LEVEL = sorted(CF_TABLE['impact_indicator_level'].unique())

POLYMERS_SHORTNAME = sorted(CF_TABLE['polymer'].unique())
POLYMERS = sorted(CF_TABLE['polymer_fullname'].unique())

POLYMERS_MAP = (
    CF_TABLE[['polymer', 'polymer_fullname']]
    .drop_duplicates()
    .set_index('polymer')['polymer_fullname']
    .to_dict()
)

REGIONS = sorted(CF_TABLE['region'].unique())

# Default size by shape
DEFAULT_SIZE_SHAPE_MAP = (
    pd.read_parquet("./data/processed/cfs_endpoint_shape_default_size.parquet")
    .set_index("shape")["size"]
    .to_dict()
)

DEFAULT_SIZE_SHAPE_TRWP_MAP = {
    'Fiber': 100, 
    'Sphere': 10}

#==================================================================
# 🌎 Countries and USEtox regions
#==================================================================
# Reminder, here we named the list COUNTRIES_MARILCA, which uses 
# the country names employed in ecoinvent.
COUNTRIES_USEtox_REGIONS = pd.read_parquet('./data/processed/countries_usetox_regions.parquet')
COUNTRIES_USEtox_REGIONS = COUNTRIES_USEtox_REGIONS[['country_ecoinvent', 'USEtox_region']]
COUNTRIES_MARILCA = sorted(COUNTRIES_USEtox_REGIONS['country_ecoinvent'].unique())

#==================================================================
# 🌱 Mapping PFN compartments to MarILCA compartments
#==================================================================
# Source: Guide - Table 3.6: Recommended alignment between PFN release
# compartments and the available CFs, by sector.
PFN_MARILCA_COMPARTMENTS = {
    'Ocean' : 'Continental seawater surface',
    'Soil' : 'Continental agricultural soil',
    'Land' : 'Continental natural soil',
    'Terrestrial environment': 'Continental natural soil',
    'Freshwater': 'Continental riverwater', 
}

#==================================================================
# ⌛ Fragmentation rates
#==================================================================
# Source: Guide - Table 3.9: Recommended fragmentation rates by 
# material type and emission compartment.
FRAGMENTATION_RATES = (
    pd.read_excel('./data/fragmentation_rates_material_emission_compartment.xlsx')
    .set_index(['polymer_category', 'emission_compartment'])['fragmentation']
    .to_dict())

# Used in the Packaging Module (Ocean and Land compartments)
PFN_FRAGMENTATION_COMPARTMENTS = {
    'Ocean' : 'Water surface',
    'Soil' : 'Topsoil',
    'Land' : 'Topsoil',
    'Terrestrial environment': 'Topsoil',
    'Freshwater': 'Water surface', 
}


#==================================================================
# 🟢 Shape
#==================================================================
# Source: Guide - Table 3.12: Recommended particle shape by product type, 
# after Corella-Puertas et al. (2023).
PRODUCT_TYPES_SHAPE_MAP = (
    pd.read_excel("./data/particle_shape_by_product_type.xlsx")
    .set_index("product_type")["shape"]
    .to_dict())

PRODUCT_TYPES = sorted(PRODUCT_TYPES_SHAPE_MAP.keys())

# Product type listed in priority for each PFN module -
# Used to set default product type, the user can select other product type
# Available product types:

# Wrappings, bags, and other film-like materials
# Textiles, ropes, and other fiber-containing MAPs
# Foam and microbeads
# Unspecified, unknown, default

PFN_MODULES_PRODUCT_TYPE = {
    "agriculture": "Wrappings, bags, and other film-like materials",
    "textiles": "Textiles, ropes, and other fiber-containing MAPs",
    "fishing_gear": "Textiles, ropes, and other fiber-containing MAPs",
    "packaging" : "Wrappings, bags, and other film-like materials",
    "transport_tires": "TRWP",
    "waste": "Unspecified, unknown, default"
}

# Default polymer by PFN module
# The user can still select another polymer, this
# is only to display a default polymer that makes sense
# for the corresponding mode
PFN_MODULES_MAIN_POLYMER = {
    "agriculture": "LDPE",
    "textiles": "PET",
    "fishing_gear": "PA",
    "packaging": "LDPE",
    "transport_tires": "TRWP",
    "waste": "Default all density",
}