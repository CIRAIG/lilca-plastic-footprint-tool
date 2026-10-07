"""
Input Data - PFN Modules
"""

import pandas as pd
import numpy as np
from pathlib import Path

#===============================================================================
# 🛍️ Packaging
#===============================================================================
# Mismanaged Waste Index (MWI)
mw_index = pd.read_parquet('./data/processed/mismanaged_waste_index_countries_iso2_2019_pfn.parquet')

MW_INDEX = (
    mw_index
    .set_index(['country_ecoinvent', 'polymer_category'])['mwi']
    .to_dict())

# For World, we consider the average value across a polymer category
MW_INDEX_AVG_WORLD = {
    polymer_category: np.mean([
        mwi
        for (country, category_), mwi in MW_INDEX.items()
        if category_ == polymer_category
    ])
    for polymer_category in set(polymer_category for country, polymer_category in MW_INDEX)
}



COUNTRIES_MWI = sorted(mw_index['country_ecoinvent'].unique())

POLYMER_TYPES = sorted(mw_index['polymer_category'].unique())

# Release rates to ocean and to land based on residual value
release_rates = pd.read_parquet('./data/processed/release_rates_ocean_land_countries_iso2_2019_pfn.parquet')

RESIDUAL_VALUE_RELEASE_RATES = (
    release_rates
    .set_index(["compartment", "size", "residual_value"])["release_rate"]
    .to_dict()
)

PACKAGING_SIZES = release_rates["size"].unique()

RESIDUAL_VALUES = release_rates["residual_value"].unique()

#===============================================================================
# 👕 Textiles
#===============================================================================

# Loss rates LR (use) - Ratio of microfiber loss per wash 
# (Source PFN in Saadi et al. 2026)
# 🏭 Production phase
textiles_loss_rate = pd.read_parquet('./data/processed/textiles_loss_rates_mg_kg_pfn.parquet')

LOSS_RATE_LEVELS = textiles_loss_rate['level_value'].unique()
TEXTILES_LOSS_RATE_USE = textiles_loss_rate.set_index(['level_value'])['lr'].to_dict()

# Release rates to the environment
textiles_release_rates = pd.read_parquet('./data/processed/textiles_rr_pfn.parquet')

COUNTRIES_RR_TEXTILES = sorted(textiles_release_rates['country_ecoinvent'].unique())

TEXTILES_RELEASE_RATES = (
    textiles_release_rates
    .set_index(['country_ecoinvent', 'compartment'])['release_rate']
    .to_dict()
)

# 🚰 Use phase
TEXTILES_LOSS_RATE_USE_PRODUCT_CAT = pd.read_parquet('./data/processed/textiles_number_washes_lifetime_pfn.parquet')
TEXTILES_PRODUCT_CATS = TEXTILES_LOSS_RATE_USE_PRODUCT_CAT['product_category'].unique()

# End of life
mtw_index = pd.read_parquet('./data/processed/mismanaged_textile_waste_index_countries_iso2_2019_pfn.parquet')

MTW_INDEX = mtw_index.set_index(['country_ecoinvent'])['mtwi'].to_dict()

COUNTRIES_MTWI = sorted(mtw_index['country_ecoinvent'].unique())

ITEMS_SIZES = PACKAGING_SIZES

#===============================================================================
# 🛞 Tires
#===============================================================================

tires_loss_rate = pd.read_parquet('./data/processed/tires_loss_rates_mg_km_pfn.parquet')

VEHICLE_MAIN_CATEGORIES = sorted(
    tires_loss_rate["vehicle_main_category"].dropna().unique()
)

tire_wear_params = pd.read_parquet('./data/processed/tires_loss_rates_parameters_pfn.parquet')
tire_wear_params_def = pd.read_parquet('./data/processed/tires_loss_rates_parameters_definitions_pfn.parquet')

TIRE_WEAR_PARAMS = (
    tire_wear_params
    .set_index(['parameter_classification', 'parameter'])['parameter_value']
    .to_dict()
)


LOSS_RATE_LEVELS = textiles_loss_rate['level_value'].unique()
TEXTILES_LOSS_RATE_USE = textiles_loss_rate.set_index(['level_value'])['lr'].to_dict()

# Release rates to the environment
tires_release_rates = pd.read_parquet('./data/processed/tires_release_rates_pfn.parquet')

ROADS_RR_TIRES = sorted(tires_release_rates['road'].unique())

TIRES_RELEASE_RATES = (
    tires_release_rates
    .set_index(['road', 'compartment'])['rr']
    .to_dict()
)