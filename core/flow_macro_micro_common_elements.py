"""
Flow-entry form renderers - Common elements for both indirect and direct emissions
"""
# Import libraries     
import streamlit as st
from typing import Literal

# Import data
from core.modules import (
    LIFE_CYCLE_STAGES, LIFE_CYCLE_STAGES_MODULES)

from core.data_marilca import(
    PRODUCT_TYPES, PRODUCT_TYPES_SHAPE_MAP, PARTICLE_SHAPES, 
    DEFAULT_SIZE_SHAPE_MAP, DEFAULT_SIZE_SHAPE_TRWP_MAP, AVAILABLE_SIZES, PFN_MODULES_PRODUCT_TYPE, POLYMERS,
    POLYMERS_SHORTNAME, POLYMERS_MAP,
    PFN_MODULES_MAIN_POLYMER
)

from core.data_general import MASS_UNITS_POLYMER

#======================================================================
# Functions for both direct and indirect emissions
#======================================================================

# Define and UI widget to handle unit conversion and conversion factors
def select_mass_unit(
        type_emission: Literal['direct', 'indirect']):
    # Return the mass-unit tooltip text based on the emission type.
    if type_emission == "direct":
        text_type_emission = "microplastics"
    elif type_emission == "indirect":
        text_type_emission = "polymer in the analyzed product"
    else:
        raise ValueError(
            "Please make sure you entered 'direct' or 'indirect' as the emission type."
        )

    text_tooltip_units = (
        f"Select the mass unit used to report the amount of {text_type_emission}.\n"
        "\nBy default, the tool uses kilograms (kg), the standard unit of mass "
        "in the International System of Units (SI)."
    )
    
    mass_units_polymer = st.selectbox(
        ":material/weight: Select the mass unit *",
        list(MASS_UNITS_POLYMER.keys()),
        index=list(MASS_UNITS_POLYMER.keys()).index("Kilograms"),
        help=text_tooltip_units)

    # Get the units from the selected unit (i.e. the abbreviation)
    mass_units = MASS_UNITS_POLYMER[mass_units_polymer]['unit']

    # Get the precision for the selected unit
    precision_mass = MASS_UNITS_POLYMER[mass_units_polymer]['precision']

    # Get the conversion factor to standard units (kg) of the selected unit
    conv_fact_to_std_unit = MASS_UNITS_POLYMER[mass_units_polymer]['conv_fact_to_std_unit']

    return mass_units_polymer, mass_units, precision_mass, conv_fact_to_std_unit

# Define UI widgets to handle default shapes and sizes based on product type.
def default_shape_size_based_on_product(module_key):

    st.subheader("**Particle shape and size selection**",
                help="Select a product type to generate initial recommendations for particle shape and size. These values can be adjusted manually.")
    # Product type determines the suggested shape, and the default size is based on that shape.
    first_row_col1, first_row_col2, first_row_col3 = st.columns(3)
    with first_row_col1:
        product_type = st.selectbox(
            ":material/package: Product type", PRODUCT_TYPES,
            index=PRODUCT_TYPES.index(PFN_MODULES_PRODUCT_TYPE[module_key]),
            help="Used to suggest a default microplastic shape -- override it if you have "
                "better information for this specific product.",
            key=f"macro_product_type_{module_key}",
        )

    with first_row_col2:
        # Determine the suggested default shape based on the product type
        suggested_shape = PRODUCT_TYPES_SHAPE_MAP[product_type]

        if module_key != "transport_tires":
            PARTICLE_SHAPES_LIST = PARTICLE_SHAPES
        else:
            PARTICLE_SHAPES_LIST =  list(DEFAULT_SIZE_SHAPE_TRWP_MAP.keys())

        particle_shape = st.selectbox(
            ":material/circle: Particle shape *", PARTICLE_SHAPES_LIST,
            index=PARTICLE_SHAPES_LIST.index(suggested_shape),
            help=f"Suggested microplastic shape for *{product_type.lower()}*: **{suggested_shape.lower()}** -- override if needed.",
            key=f"macro_particle_shape_{module_key}_{product_type}",
        )

    with first_row_col3:
        # Determine the suggested default size based on the selected shape
        if module_key != "transport_tires":
            suggested_size = DEFAULT_SIZE_SHAPE_MAP[particle_shape]
        else:
            suggested_size = DEFAULT_SIZE_SHAPE_TRWP_MAP[particle_shape]


        particle_size = st.selectbox(
            ":material/straighten: Particle size (μm) *", AVAILABLE_SIZES,
            index=AVAILABLE_SIZES.index(suggested_size),
            help=f"Suggested microplastic size for **{particle_shape.lower()}**: **{suggested_size} μm** -- override if needed.",
            key=f"macro_particle_size_{module_key}_{particle_shape}",
        )

    return product_type, particle_shape, particle_size

#======================================================================
# Functions for indirect emissions
#======================================================================

# Define a function to create UI widgets for selecting the life cycle stage, polymer, and polymer mass.

def input_stage_polymer_mass(module_key, mass_units, 
                             precision_mass, mass_units_polymer,
                             type_emission: Literal['direct', 'indirect']):
    # Return the list of life cycle stages and tooltip according to the emission type.
    if type_emission == "direct":
        # Use a predefined list of life cycle stages
        available_lc_stages = LIFE_CYCLE_STAGES
    elif type_emission == "indirect":
        # Determine the life cycle stages available in the PFN module for which microplastic emissions are calculated.
        available_lc_stages = LIFE_CYCLE_STAGES_MODULES[module_key]
    else:
        raise ValueError(
            "Please make sure you entered 'direct' or 'indirect' as the emission type."
        )
    if len(available_lc_stages) == 1:
        stages_text = available_lc_stages[0].lower()
    elif len(available_lc_stages) == 2:
        stages_text = " and ".join(stage.lower() for stage in available_lc_stages)
    else:
        stages_text = (
            ", ".join(stage.lower() for stage in available_lc_stages[:-1])
            + f", and {available_lc_stages[-1].lower()}"
        )

    if type_emission == "direct":
        tooltip_text_stages = f"For the analysis of results you can select among: {stages_text}"
    else:
        tooltip_text_stages = (
            f"For {module_key}, the PFN module allows you to compute microplastic emissions "
            f"for {stages_text}."
        )
    c1, c2, c3 = st.columns(3)
    with c1:
        life_cycle_stage = st.selectbox(":material/cycle: Life cycle stage *", available_lc_stages,
                                        help=tooltip_text_stages)
    with c2:
        polymer = st.selectbox(":material/gesture: Polymer *", POLYMERS_SHORTNAME, 
                                index=POLYMERS_SHORTNAME.index(PFN_MODULES_MAIN_POLYMER[module_key]),
                                help="Please note that you can scroll up and down the dropdown list to view the full list of polymers.")

        # Display the full polymer name when the user selects an abbreviation.
        if polymer != POLYMERS_MAP[polymer]:
            st.caption(POLYMERS_MAP[polymer])
    with c3:
        mass_selected_units = st.number_input(
            f":material/scale: Mass of polymer ({mass_units}) *",
            min_value=0.0,
            value=1.0,
            step=0.01,
            format=f"%.{precision_mass}f",
            help=f"Enter the polymer mass in {mass_units_polymer.lower()} ({mass_units})."
        )

    return life_cycle_stage, polymer, mass_selected_units