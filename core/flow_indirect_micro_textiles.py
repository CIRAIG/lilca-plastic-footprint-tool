"""
Flow-entry form renderers - 👕 Textiles
"""

import uuid
import streamlit as st

from core.data_marilca import(
    POLYMERS, PFN_MARILCA_COMPARTMENTS, POLYMERS_SHORTNAME, PFN_MODULES_MAIN_POLYMER, POLYMERS_MAP)
from core.data_pfn import (
    RESIDUAL_VALUE_RELEASE_RATES, RESIDUAL_VALUES,    
    TEXTILES_LOSS_RATE_USE,
    TEXTILES_RELEASE_RATES,
    COUNTRIES_RR_TEXTILES,
    LOSS_RATE_LEVELS,
    TEXTILES_LOSS_RATE_USE_PRODUCT_CAT,
    TEXTILES_PRODUCT_CATS,
    MTW_INDEX,
    COUNTRIES_MTWI,
    ITEMS_SIZES,
)

from core.data_general import MASS_UNITS_POLYMER


# Import common elements
from core.flow_macro_micro_common_elements import (
    default_shape_size_based_on_product,
    select_mass_unit,
    input_stage_polymer_mass)

def render_textiles_macro_to_micro_form(module_key):
    """
    Textiles situation 1: microfiber release is modeled separately for
    three life cycle stages, each with its own mechanism:

    - Production: microfiber loss rate per industrial pre-wash (mg/kg),
      scaled by the number of pre-washes, split across environmental
      compartments (ocean, freshwater, soil, terrestrial) using
      country-specific release rates. No mismanagement step -- fiber
      shedding during washing happens regardless of waste management.
    - Use: same mechanism as Production, but using the loss rate and
      number of washes appropriate to the garment's product category
      over its lifetime, with its own country-specific release rates.
    - End-of-life: garment mass -> mismanaged textile waste index (MTWI)
      -> release rates to ocean/land (by item size and residual value)
      -> a weathering-based fragmentation-equivalent yield (loss rate
      per wash x weathering-to-washing MPF release factor x the 75-wash
      reference count from Pinlova & Nowack, 2023) -> microplastic mass
      per compartment.

    Production and Use report micro_mass_kg directly (fiber shedding has
    no macroplastic intermediate); End-of-life is the only stage with a
    meaningful macro_mass_kg, since it's the only one where mismanaged
    macroplastic precedes a fragmentation-like (weathering) step.
    """
    with st.container(border=True):
                
        st.subheader("Product or component")
        c_product1, c_product2, c_product3 = st.columns(3)

        with c_product1:
            product_name_key = f"product_name_{module_key}"
            
            product_name = st.text_input(
                ":material/category: Product or component *",
                value=st.session_state.get(product_name_key, ""),
                placeholder="e.g. T-shirt",
                help=(
                    "Identify the specific product, item, or component this flow belongs to. "
                    "Use this to group several polymer flows that together make up a single "
                    "product -- e.g. a packaging item made of a cap, body, and label (each a "
                    "different polymer); a garment made of a shell fabric, lining, and trims; "
                    "or a tire's tread versus sidewall compound. For a single-polymer product, "
                    "simply name the product itself (e.g. 'T-shirt')."
                ),
                key=product_name_key,
            )

        st.subheader("**Textile polymer composition**",
                    help="Select the polymer contained in the textile product, then select the reporting mass unit and enter the corresponding polymer mass.")
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
                help=f"Enter the polymer mass in {mass_units_polymer.lower()} ({mass_units}).")
        # Define first row: default shape and size based on product type    
        product_type, particle_shape, particle_size = default_shape_size_based_on_product(module_key)

        with st.container(border=True):
            st.subheader("**:material/factory: Microfiber leakage during the production stage**")


            st.markdown('**Parameters for the microfiber loss rate per wash (mg/kg)**')

            c_pre1, c_pre2, c_pre3 = st.columns(3)
            with c_pre1:
                level_lr_textiles = st.select_slider(
                    ":material/linear_scale: Loss rate level *", LOSS_RATE_LEVELS,
                    help='Select a loss rate level. By default, we use a conservative approach and set the loss rate to the highest available value.',
                    value="High value",
                    key=f"macro_level_lr_textiles_{module_key}",
                )
            with c_pre2:
                lose_rate_prod  = st.number_input(
                    "Loss rate per wash (mg/kg)",
                    value= TEXTILES_LOSS_RATE_USE[level_lr_textiles], 
                    step=0.01,
                    help="Pre-filled from the **loss rate level** as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_lose_rate_prod_{module_key}{level_lr_textiles}"
                )
            with c_pre3:
                number_washes_prod = st.number_input(
                    ":material/local_laundry_service: Number of industrial pre-washes*", 
                    min_value=0, value=5,
                    help="The PLP Guidelines (Quantis & EA, 2020) recommend using a proxy of 5 industrial pre-washes. You can modify this value if more specific or representative data are available."
                    )

            st.markdown("**Release rates to the environment**",
                        help="For microfiber leakage during the production stage, release rates vary by country.")
            c_prod1, c_prod2, c_prod3 = st.columns(3)

            with c_prod1:
                country_production = st.selectbox(
                        ":material/public: Country *", COUNTRIES_RR_TEXTILES + ["World"], 
                        index=COUNTRIES_RR_TEXTILES.index("Canada"),
                        help="Select **World** if the country is unknown or not listed.",
                        key=f"macro_country_production_{module_key}",
                    )
            with c_prod2:
                rr_ocean_prod = st.number_input(
                    ":material/moving: :material/water: Release rate to ocean",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_production, 'Ocean')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_ocean_prod_{module_key}{country_production}"
                )
            with c_prod3:
                rr_frw_prod = st.number_input(
                    ":material/moving: :material/waves: Release rate to freshwater",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_production, 'Freshwater')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_frw_prod_prod_{module_key}{country_production}"
                )

            c_prod4, c_prod5, c_prod6 = st.columns(3)
            with c_prod5:
                rr_soil_prod = st.number_input(
                    ":material/moving: :material/wheat: Release rate to soil",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_production, 'Soil')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_soil_prod_prod_{module_key}{country_production}"
                )
            with c_prod6:
                rr_terenv_prod = st.number_input(
                    ":material/moving: :material/grass: Release rate to terrestrial environment",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_production, 'Terrestrial environment')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_terenv_prod_prod_{module_key}{country_production}"
                )
            # Stop if the addition of ocean and land release rates are superior to 1.
            if rr_ocean_prod + rr_frw_prod + rr_soil_prod + rr_terenv_prod  > 1.0:
                st.error(
                    f"Ocean + Freshwater + Soil + Terrestrial environment release rates must be ≤ 1. "
                    f"Current total: {rr_ocean_prod + rr_frw_prod + rr_soil_prod + rr_terenv_prod:.2f}"
                )
                st.stop()

        with st.container(border=True):
            st.subheader("**:material/local_laundry_service: Microfiber leakage during the use stage**")
            st.markdown("**Parameters for the microfiber loss rate per wash (mg/kg)**")

            c_use_wash1, c_use_wash2, c_use_wash3 = st.columns(3)
            with c_use_wash1:
                textile_product_cat = st.selectbox(
                    ":material/apparel: Product category *", TEXTILES_PRODUCT_CATS,
                    help="Select a product category to determine the **average number of washes over its lifetime**.",
                    key=f"macro_textile_product_cat_{module_key}"
                )
            with c_use_wash2:
                lose_rate_use = st.number_input(
                    "Loss rate per wash (mg/kg)",
                    min_value=0.0,
                    step=0.1,
                    value= float(TEXTILES_LOSS_RATE_USE_PRODUCT_CAT.loc[
                        TEXTILES_LOSS_RATE_USE_PRODUCT_CAT['product_category'] == textile_product_cat,
                        'average_lr_per_wash'].iloc[0]),
                    help ="The average loss rate is based on the Product Environmental Footprint Category Rules (PEFCR) – Apparel and Footwear, Version 1.3 (2022), as implemented in the corresponding PFN module." \
                            " **You can modify this value if you have more specific data**",
                    key=f"macro_lose_rate_use_{module_key}{textile_product_cat}"
                )
            with c_use_wash3:
                number_washes_use = st.number_input(
                    ":material/laundry: Number of washes per lifetime *",
                    min_value=1.0,
                    step=1.0,
                    value= TEXTILES_LOSS_RATE_USE_PRODUCT_CAT.loc[
                        TEXTILES_LOSS_RATE_USE_PRODUCT_CAT['product_category'] == textile_product_cat,
                        'nr_of_washes_per_lifetime'].iloc[0],
                    help ="The average number of washes over a product’s lifetime is based on the Product Environmental Footprint Category Rules (PEFCR) – Apparel and Footwear, Version 1.3 (2022), as implemented in the corresponding PFN module." \
                            " **You can modify this value if you have more specific data or if adjustments are needed to align with your functional unit.** " \
                            "Please note that this value represents the total number of washes over the product’s entire lifetime. **If your functional unit covers a different time period, adjust the value accordingly.**",
                    key=f"macro_number_washes_use_{module_key}{textile_product_cat}"
                )

            st.markdown("**Release rates to the environment**",
                                    help="For microfiber leakage during the use stage, release rates vary by country.")
            c_use1, c_use2, c_use3 = st.columns(3)
            with c_use1:
                country_use = st.selectbox(
                        ":material/public: Country *", COUNTRIES_RR_TEXTILES + ["World"], 
                        index=COUNTRIES_RR_TEXTILES.index("Canada"),
                        help="Select **World** if the country is unknown or not listed.",
                        key=f"macro_country_use_{module_key}",
                    )
            with c_use2:
                rr_ocean_use = st.number_input(
                    ":material/moving: :material/water: Release rate to ocean",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_use, 'Ocean')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_ocean_use_{module_key}{country_use}"
                )
            with c_use3:
                rr_frw_use = st.number_input(
                    ":material/moving: :material/waves: Release rate to freshwater",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_use, 'Freshwater')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_frw_use_{module_key}{country_use}"
                )

            c_use4, c_use5, c_use6 = st.columns(3)
            with c_use5:
                rr_soil_use = st.number_input(
                    ":material/moving: :material/wheat: Release rate to soil",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_use, 'Soil')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_soil_use_use_{module_key}{country_use}"
                )
            with c_use6:
                rr_terenv_use = st.number_input(
                    ":material/moving: :material/grass: Release rate to terrestrial environment",
                    min_value=0.00,
                    max_value=1.00,
                    value= TEXTILES_RELEASE_RATES[(country_use, 'Terrestrial environment')], 
                    step=0.01,
                    help="Pre-filled based on the selected country as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_terenv_use_use_{module_key}{country_use}"
                )
            # Stop if the addition of ocean and land release rates are superior to 1.
            if rr_ocean_use + rr_frw_use + rr_soil_use + rr_terenv_use  > 1.0:
                st.error(
                    f"Ocean + Freshwater + Soil + Terrestrial environment release rates must be ≤ 1. "
                    f"Current total: {rr_ocean_use + rr_frw_use + rr_soil_use + rr_terenv_use:.2f}"
                )
                st.stop()

        with st.container(border=True):
            st.subheader("**:material/delete: Microfiber leakage during the end-of-life stage**")


            c_eol1, c_eol2 = st.columns(2)

            with c_eol1:
                country_eol = st.selectbox(
                    ":material/public: Country *", COUNTRIES_MTWI + ["World"], 
                        index=COUNTRIES_MTWI.index("Canada"),
                        help="Select **World** if the country is unknown or not listed.",
                        key=f"macro_country_eol_{module_key}",
                    )
            with c_eol2:
                # Display the MTWI based on country
                if country_eol == "World":
                    mtwi_default = 0.10
                else:
                    mtwi_default = MTW_INDEX[(country_eol)]
                
                mtwi_value = st.number_input(
                    ":material/arrow_split: Mismanaged textile waste index (MTWI) *", min_value=0.0, max_value=1.0,
                    value=mtwi_default, step=0.01,
                    help="Pre-filled from the MTWI index table for the selected *country* -- "
                        "edit directly if you have more recent or country-specific data.",
                    key=f"macro_mtwi_value_{module_key}_{country_eol}",
                )

            st.markdown("**Release rates to the environment**",
                                    help="For microfiber leakage during the end-of-life stage, release rates are determined by item size and the residual value.")
            c_pre1, c_pre2 = st.columns(2)
            with c_pre1:
                item_size = st.select_slider(
                    ":material/measuring_tape: Item size *", ITEMS_SIZES,
                    help="Together with the *residual value*, this parameter is used to retrieve "
                        "the release rates to the ocean and land from the **release rate matrix**.",
                    value="Large size (>25cm)",
                    key=f"macro_item_size_{module_key}",
                )
                
            with c_pre2:
                residual_value = st.select_slider(
                    ":material/paid: Residual value *", RESIDUAL_VALUES,
                    help="A product/polymer residual value can be assumed to be equal to its market price, "
                    "or recalculated as a function of product homogeneity, time to collect and resale price.",
                    value="Medium",
                    key=f"macro_residual_value_{module_key}",
                )

            # Release rates to water surface (ocean) and natural soil (land)
            rr_ocean_eol_default = RESIDUAL_VALUE_RELEASE_RATES[('Ocean', item_size, residual_value)]
            rr_land_eol_default = RESIDUAL_VALUE_RELEASE_RATES[('Land', item_size, residual_value)]

            c_rr1, c_rr2 = st.columns(2)
            with c_rr1:
                ## Release rates
                rr_ocean_eol = st.number_input(
                    ":material/moving: :material/water: Release rate to ocean", min_value=0.00, max_value=1.00,
                    value=rr_ocean_eol_default, step=0.05,
                    help="Pre-filled from the **release rate matrix** for the selected *item size* and *residual value* -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_ocean_eol_{module_key}_{item_size}_{residual_value}",
                )

            with c_rr2:
                rr_land_eol = st.number_input(
                    ":material/moving: :material/grass: Release rate to land", min_value=0.0, max_value=1.0,
                    value=rr_land_eol_default, step=0.01,
                    help="Pre-filled from the **release rate matrix** for the selected *packaging size* and *residual value* -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_land_{module_key}_{item_size}_{residual_value}",
                )

            # Stop if the addition of ocean and land release rates are superior to 1.
            if rr_ocean_eol + rr_land_eol > 1.0:
                st.error(
                    f"Ocean + Land release rates must be ≤ 1. "
                    f"Current total: {rr_ocean_eol + rr_land_eol:.2f}"
                )
                st.stop()

            

            st.markdown("**Microplastics released from weathered macroplastics (mg microplastic emitted/kg macroplastic emitted)**",
                        help="Pinlova & Nowack (2023) found that one gram of fabric releases **20–40 times more microplastic fibers (MPFs)** during weathering than during washing. Their experimental setup considered **75 washing cycles**. The amount of microplastic released through weathering is calculated as: \n\n **Microplastic release = Loss rate per wash (mg/kg) × Weathering-to-washing MPF release factor × Number of washes**")
            col_weathering1, col_weathering2, col_weathering3  = st.columns(3)

            with col_weathering1:
                lose_rate_eol = st.number_input(
                    "Loss rate per wash (mg/kg) *",
                    min_value=0.0,
                    step=0.1,
                    value= lose_rate_use,
                    help ="The average loss rate used here corresponds to losses occurring during the use stage. You can adjust this value if more specific data are available for the selected product type and polymer.",
                    key=f"macro_lose_rate_eol_{module_key}{textile_product_cat}"
                )
            with col_weathering2:
                weathering_to_washing_mpf_release_factor = st.number_input(
                    "Weathering-to-washing MPF release factor *",
                    min_value=20,
                    value=30,
                    max_value=40,
                    help="Pinlova & Nowack (2023) found that one gram of fabric releases 20–40 times more microplastic fibers (MPFs) during weathering than during washing. Here, the median value of 30 is used as the default.",
                    key=f"macro_weathering_to_washing_mpf_release_factor_{module_key}",
                )

            with col_weathering3:
                # Number of washes in Pinlova & Nowack (2023
                number_washes_eol = st.number_input(
                    ":material/laundry: Number of washes *",
                    min_value=75,
                    max_value=75,
                    step=1,
                    value= 75,
                    help ="The experimental setup of Pinlova & Nowack (2023) considered 75 washing cycles, which is used here as the default value. This parameter is displayed for transparency but cannot be modified.",
                    key=f"macro_number_washes_eol_{module_key}{textile_product_cat}"
                )

            weathering_mp_release_factor = (weathering_to_washing_mpf_release_factor * number_washes_eol * lose_rate_eol) / 1e6

            st.caption(f"Microplastics released from weathered macroplastic : {round(weathering_mp_release_factor, 2)} (kg microplastic/kg macroplastic)")
                


        with st.form(f"add_flow_{module_key}_macro_to_micro", clear_on_submit=True, border=False):
        
            submitted = st.form_submit_button("Add flow", type="primary")
                

    if not submitted:
        return None
    if not product_name:
        st.error("Product or component identification is required.")
        return None

    release_rates_compartment = {
        "Production": {
                PFN_MARILCA_COMPARTMENTS['Ocean']: rr_ocean_prod,
                PFN_MARILCA_COMPARTMENTS['Soil']: rr_soil_prod,
                PFN_MARILCA_COMPARTMENTS['Freshwater']: rr_frw_prod,
                PFN_MARILCA_COMPARTMENTS['Terrestrial environment']: rr_terenv_prod,
        },
        "Use": {
                PFN_MARILCA_COMPARTMENTS['Ocean']: rr_ocean_use,
                PFN_MARILCA_COMPARTMENTS['Soil']: rr_soil_use,
                PFN_MARILCA_COMPARTMENTS['Freshwater']: rr_frw_use,
                PFN_MARILCA_COMPARTMENTS['Terrestrial environment']: rr_terenv_use,
        },
        "End-of-life": {
                PFN_MARILCA_COMPARTMENTS['Ocean']: rr_ocean_eol,
                PFN_MARILCA_COMPARTMENTS['Land']: rr_land_eol,
        }

    }

    number_washes = {
        "Production": number_washes_prod,
        "Use": number_washes_use,
        "End-of-life": number_washes_eol
    }

    loss_rates = {
        "Production": lose_rate_prod,
        "Use": lose_rate_use,
        "End-of-life": lose_rate_eol
    }

    mismanaged_textile_waste_index = {
        "Production": None,
        "Use": None,
        "End-of-life": mtwi_value
    }

    weathering_to_washing_mpf_release_factors = {
        "Production": None,
        "Use": None,
        "End-of-life": weathering_to_washing_mpf_release_factor
    }

    countries_stage = {
        "Production": country_production,
        "Use": country_use,
        "End-of-life": country_eol
    }



    flows = []

    for life_cycle_stage, compartment_rates in release_rates_compartment.items():

        # Values that apply to the whole life-cycle stage
        stage_number_washes = number_washes.get(life_cycle_stage)
        stage_loss_rate = loss_rates.get(life_cycle_stage)
        stage_mtwi = mismanaged_textile_waste_index.get(life_cycle_stage)
        stage_weathering_factor = weathering_to_washing_mpf_release_factors.get(life_cycle_stage)

        # Loop through the environmental compartments for this stage
        for compartment, release_rate in compartment_rates.items():

            # Get the country for this stage
            country = countries_stage[life_cycle_stage]

            # Calculate microplastic mass

            if life_cycle_stage == "End-of-life":
                micro_mass_kg = (
                mass_selected_units
                * conv_fact_to_std_unit
                * stage_loss_rate
                * stage_number_washes
                * release_rate
                * stage_mtwi
                * stage_weathering_factor
                ) / 1e6
            else:
                micro_mass_kg = (
                mass_selected_units
                * conv_fact_to_std_unit
                * stage_loss_rate
                * stage_number_washes
                * release_rate
            ) / 1e6

            flows.append({
                "id": str(uuid.uuid4())[:8],
                "situation": "macro_to_micro",
                "product_name": product_name,
                "life_cycle_stage": life_cycle_stage,
                "product_type": product_type,
                "country": country,
                "polymer": polymer,
                "shape": particle_shape,
                "size": particle_size,
                "macro_mass_kg": mass_selected_units * conv_fact_to_std_unit,

                # Stage-specific values
                "number_washes": stage_number_washes,
                "loss_rate": stage_loss_rate,
                "mtwi": stage_mtwi,
                "stage_weathering_factor": stage_weathering_factor,

                # Compartment-specific values
                "emission_compartment": compartment,
                "release_rate": release_rate,

                # Calculated microplastic mass
                "micro_mass_kg": micro_mass_kg
            })

    if not flows:
        st.warning(
            "No microplastic mass computed for any life-cycle stage "
            "or environmental compartment -- check the inputs above."
        )
        return None

    return flows