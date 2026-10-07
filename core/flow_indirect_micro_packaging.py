"""
Flow-entry form renderers - 🛍️ Packaging
"""
# Import libraries 
import uuid
import numpy as np
import streamlit as st

# Import data
from core.data_general import MASS_UNITS_POLYMER

from core.data_marilca import(
    FRAGMENTATION_RATES, PFN_FRAGMENTATION_COMPARTMENTS, PFN_MARILCA_COMPARTMENTS,
    POLYMERS_SHORTNAME, PFN_MODULES_MAIN_POLYMER, POLYMERS_MAP)

from core.data_pfn import (
    MW_INDEX, MW_INDEX_AVG_WORLD, RESIDUAL_VALUE_RELEASE_RATES, PACKAGING_SIZES, RESIDUAL_VALUES,
    COUNTRIES_MWI,
    POLYMER_TYPES, )


# Import common elements
from core.flow_macro_micro_common_elements import (
    default_shape_size_based_on_product,
    select_mass_unit,
    input_stage_polymer_mass)

# Define a function to render the form to compute microplastic emissions from packaging.
def render_packaging_macro_to_micro_form(module_key):
    """
    Packaging situation 1: macroplastic mass -> mismanaged waste index ->
    residual-value-dependent release rates (ocean, land) -> fragmentation
    rate per (polymer, compartment) -> microplastic mass per compartment.
    """

    with st.container(border=True):
        st.subheader("Product or component")
        c_product1, c_product2, c_product3 = st.columns(3)

        with c_product1:
            product_name_key = f"product_name_{module_key}"
            
            product_name = st.text_input(
                ":material/category: Product or component *",
                value=st.session_state.get(product_name_key, ""),
                placeholder="e.g. Yogurt cup, 500 mL",
                help=(
                    "Identify the specific product, item, or component this flow belongs to. "
                    "Use this to group several polymer flows that together make up a single "
                    "product -- e.g. a packaging item made of a cap, body, and label (each a "
                    "different polymer); a garment made of a shell fabric, lining, and trims; "
                    "or a tire's tread versus sidewall compound. For a single-polymer product, "
                    "simply name the product itself (e.g. 'Yogurt cup, 500 mL')."
                ),
                key=product_name_key,
            )
        # Outside the form: product type drives the shape suggestion, and
        # (together with country) drives the MWI default -- both need to
        # react live to a change, which forms don't allow mid-form.
        st.subheader("**Packaging polymer composition**",
                    help="Select the polymer contained in the packaging product, then select the reporting mass unit and enter the corresponding polymer mass.")
        cgeneral_1, cgeneral_2, cgeneral_3 = st.columns(3)
        with cgeneral_1:
            polymer = st.selectbox(":material/gesture: Polymer *", 
                                   POLYMERS_SHORTNAME, 
                                index=POLYMERS_SHORTNAME.index(PFN_MODULES_MAIN_POLYMER[module_key]),
                                help="Please note that you can scroll up and down the dropdown list to view the full list of polymers.")

            # Display the full polymer name when the user selects an abbreviation.
            if polymer != POLYMERS_MAP[polymer]:
                st.caption(POLYMERS_MAP[polymer])
        with cgeneral_2:
            text_tooltip_units = (
                f"Select the mass unit used to report the amount of polymer in the analyzed product.\n"
                "\nBy default, the tool uses kilograms (kg), the standard unit of mass "
                "in the International System of Units (SI).")
                
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
 
        with cgeneral_3:
            mass_selected_units = st.number_input(
                f":material/scale: Mass of polymer ({mass_units}) *",
                min_value=0.0,
                value=1.0,
                step=0.01,
                format=f"%.{precision_mass}f",
                key=f"mass_input_{module_key}_{mass_units_polymer}",
                help=f"Enter the polymer mass in {mass_units_polymer.lower()} ({mass_units}).")
        
        # Define first row: default shape and size based on product type    
        product_type, particle_shape, particle_size = default_shape_size_based_on_product(module_key)

        with st.container(border=True):
            # Hard-coded life cycle stage
            life_cycle_stage = "End-of-life"
            st.subheader("**:material/delete: Microplastic leakage during the end-of-life stage**")
            st.markdown("**Release rates to the environment**",
                        help="For microplastic leakage during the end-of-life stage of packaging, release rates are determined by item size and the residual value.")
            # Define second row: packaging size and residual value
            second_row_col1, second_row_col2, second_row_col3 = st.columns(3)
            with second_row_col1:
                packaging_size = st.select_slider(
                    ":material/measuring_tape: Packaging size *", PACKAGING_SIZES,
                    help="Together with the *residual value*, this parameter is used to retrieve "
                        "the release rates to the ocean and land from the **release rate matrix**.",
                    value="Medium size (5-25cm)",
                    key=f"macro_packaging_size_{module_key}",
                )
                
            with second_row_col2:
                residual_value = st.select_slider(
                    ":material/paid: Residual value *", RESIDUAL_VALUES,
                    help="A product/polymer residual value can be assumed to be equal to its market price, "
                    "or recalculated as a function of product homogeneity, time to collect and resale price.",
                    value="Medium",
                    key=f"macro_residual_value_{module_key}",
                )
            with second_row_col3:
                pass

            # Define third row
            # Release rates to water surface (ocean) and natural soil (land)
            rr_ocean_default = RESIDUAL_VALUE_RELEASE_RATES[('Ocean', packaging_size, residual_value)]
            rr_land_default = RESIDUAL_VALUE_RELEASE_RATES[('Land', packaging_size, residual_value)]

            third_row_col1, third_row_col2, third_row_col3 = st.columns(3)
            with third_row_col1:
                ## Release rates
                rr_ocean = st.number_input(
                    ":material/moving: :material/water: Release rate to ocean", min_value=0.00, max_value=1.00,
                    value=rr_ocean_default, step=0.05,
                    help="Pre-filled from the **release rate matrix** for the selected *packaging size* and *residual value* -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_ocean_{module_key}_{packaging_size}_{residual_value}",
                )

            with third_row_col2:
                rr_land = st.number_input(
                    ":material/moving: :material/grass: Release rate to land", min_value=0.0, max_value=1.0,
                    value=rr_land_default, step=0.01,
                    help="Pre-filled from the **release rate matrix** for the selected *packaging size* and *residual value* -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_land_{module_key}_{packaging_size}_{residual_value}",
                )

            # Stop if the addition of ocean and land release rates are superior to 1.
            if rr_ocean + rr_land > 1.0:
                st.error(
                    f"Ocean + Land release rates must be ≤ 1. "
                    f"Current total: {rr_ocean + rr_land:.2f}"
                )
                st.stop()

            with third_row_col3:
                pass


            st.markdown("**Mismanaged waste index (MWI)**")
            # Define fourth row
            fourth_row_col1, fourth_row_col2, fourth_row_col3 = st.columns(3)

            with fourth_row_col1:
                country = st.selectbox(
                    ":material/public: Country *", COUNTRIES_MWI + ["World"],
                    index= COUNTRIES_MWI.index("Canada"),
                    help="Select **World** if the country is unknown or not listed. \n\n"
                    "Together with the *packaging polymer type*, determines the default **mismanaged waste index** (MWI)",
                    key=f"macro_country_{module_key}",
                )

            with fourth_row_col2:
                polymer_category = st.selectbox(
                    ":material/inventory_2: Packaging polymer type *", POLYMER_TYPES,
                    help="This parameter corresponds to the packaging categories defined by the **MacArthur Foundation's Global Commitment (GC)**. For examples, please visit this [site](https://www.e-a.earth/insights/the-plasteax-model-a-top-down-mass-balance-approach/).\n\n"
                    "Together with the *country* parameter, determines the default **mismanaged waste index** (MWI). "
                    "In addition, this parameter determines the default fragmentation rates in both the ocean and on land.",
                    key=f"macro_polymer_category_{module_key}",
                )
            with fourth_row_col3:
                # Display the MWI based on country and packaging polymer type
                # For World, we considered the average value across a polymer category
                if country == "World":
                    mwi_default = MW_INDEX_AVG_WORLD[polymer_category]
                else:
                    mwi_default = MW_INDEX[(country, polymer_category)]

                # Editable, pre-filled with the looked-up default.
                mwi_value = st.number_input(
                    ":material/arrow_split: Mismanaged waste index (MWI) *", min_value=0.0, max_value=1.0,
                    value=mwi_default, step=0.01,
                    help="Pre-filled from the MWI index table for the selected *country* and *packaging polymer type* -- "
                        "edit directly if you have more recent or country-specific data.",
                    key=f"macro_mmw_{module_key}_{country}_{polymer_category}",
                )

            st.markdown("**Fragmentation rates in the environment**")
            # Define the columns in the fifth row
            fifth_row_col1, fifth_row_col2, fifth_row_col3 = st.columns(3)

            # Fragmentation rates in ocean and land
            frag_r_ocean_default = FRAGMENTATION_RATES[(polymer_category, PFN_FRAGMENTATION_COMPARTMENTS['Ocean'])]

            frag_r_land_default = FRAGMENTATION_RATES[(polymer_category, PFN_FRAGMENTATION_COMPARTMENTS['Land'])]

            with fifth_row_col1:
                ## Fragmentation rates - Ocean
                frag_r_ocean = st.number_input(
                    ":material/grain: :material/water: Fragmentation rate (ocean)", min_value=0.00, max_value=1.00,
                    value=frag_r_ocean_default, step=0.01,
                    help="Pre-filled based on the selected *packaging polymer type*. -- "
                        "Edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_frag_r_ocean_{module_key}_{polymer_category}",
                )

            with fifth_row_col2:
                ## Fragmentation rates - Land
                frag_r_land = st.number_input(
                    ":material/grain: :material/grass: Fragmentation rate (land)", min_value=0.00, max_value=1.00,
                    value=frag_r_land_default, step=0.01,
                    help="Pre-filled based on the selected *packaging polymer type*. -- "
                        "Edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_frag_r_land_{module_key}_{polymer_category}",
                )

            with fifth_row_col3:
                # Select the mass unit
                pass

        with st.form(f"add_flow_{module_key}_macro_to_micro", clear_on_submit=True, border=False):
            submitted = st.form_submit_button("Add flow", type="primary")

    if not submitted:
        return None
    if not product_name:
        st.error("Product or component identification is required.")
        return None

    release_rates_compartment = {
    PFN_MARILCA_COMPARTMENTS['Ocean']: rr_ocean,
    PFN_MARILCA_COMPARTMENTS['Land']: rr_land}

    frag_rates_compartment = {
    PFN_MARILCA_COMPARTMENTS['Ocean']: frag_r_ocean,
    PFN_MARILCA_COMPARTMENTS['Land']: frag_r_land}

    flows = []

    for compartment, release_rate in release_rates_compartment.items():
        frag_rate = frag_rates_compartment[compartment]
        flows.append({
            "id": str(uuid.uuid4())[:8],
            "situation": "macro_to_micro",
            "product_name": product_name,
            "life_cycle_stage": life_cycle_stage,
            "product_type": product_type,
            "country": country,
            "polymer": polymer,
            "packaging_polymer_type": polymer_category,
            "shape": particle_shape,
            "size": particle_size,
            "macro_mass_kg": mass_selected_units * conv_fact_to_std_unit,
            "packaging_size": packaging_size,
            "residual_value": residual_value,
            "mwi": mwi_value,
            "emission_compartment": compartment,
            "release_rate": release_rate,
            "frag_rate": frag_rate,
            "micro_mass_kg": mass_selected_units * conv_fact_to_std_unit * mwi_value * release_rate * frag_rate,
        })
    if not flows:
        st.warning("No microplastic mass computed for either compartment -- check the inputs above.")
        return None
    return flows