"""
Flow-entry form renderer.

render_direct_micro_form() returns a single dict or None (not submitted).

"""

import uuid
import streamlit as st

from core.data_general import MASS_UNITS_POLYMER

from core.modules import (
    LIFE_CYCLE_STAGES)


from core.data_marilca import(
    COMPARTMENTS, COUNTRIES_MARILCA, POLYMERS_SHORTNAME, PFN_MODULES_MAIN_POLYMER, POLYMERS_MAP)

# Import common elements
from core.flow_macro_micro_common_elements import (
    default_shape_size_based_on_product,
    select_mass_unit,
    input_stage_polymer_mass)

def render_direct_micro_form(module_key):
    """The user already knows the microplastic mass directly."""

    with st.container(border=True):

        # Outside the form on purpose since widgets inside a form only report new values on submit
        # particle_size's default react live to a shape change, 
        # particle shape's default react live to product type

        st.subheader("Product or component")
        c_product1, c_product2, c_product3 = st.columns(3)

        with c_product1:
            product_name_key = f"product_name_{module_key}"
            
            product_name = st.text_input(
                ":material/category: Product or component *",
                value=st.session_state.get(product_name_key, ""),
                placeholder="e.g. Product A",
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

        st.subheader("**Microplastics polymer composition**",
                    help="Select the polymer type, choose the reporting mass unit, and enter the corresponding polymer mass.")
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

        product_type, particle_shape, particle_size = default_shape_size_based_on_product(module_key)

        st.subheader("Emission context")
        # Define additional parameters for mass units and to display a figure of compartments
        col_additional_params1, col_additional_params2, col_additional_params3 = st.columns(3)

        with col_additional_params1:
            # Ask for a country, so the corresponding CF is employed
            country = st.selectbox(
                ":material/public: Country *", COUNTRIES_MARILCA + ["World"], 
                index=COUNTRIES_MARILCA.index("Canada"),
                help="Select **World** if the country is unknown or not listed.\n" \
                "\nPlease note that you can scroll up and down the dropdown list to view the full list of countries.",
            )
        with col_additional_params2:
            # For direct emissions, the default emission compartment is set to continental seawater surface
            compartment = st.selectbox(
                ":material/water: Emission compartment *", 
                COMPARTMENTS,
                index=COMPARTMENTS.index("Continental seawater surface"),
                help="For additional guidance, expand the section below to view a representation" \
                " of the emission compartments for which characterization factors (CFs) are defined.")

        with col_additional_params3:
            # Use the predefined list of life cycle stages
            available_lc_stages = LIFE_CYCLE_STAGES

            if len(available_lc_stages) == 1:
                stages_text = available_lc_stages[0].lower()
            elif len(available_lc_stages) == 2:
                stages_text = " and ".join(stage.lower() for stage in available_lc_stages)
            else:
                stages_text = (
                    ", ".join(stage.lower() for stage in available_lc_stages[:-1])
                    + f", and {available_lc_stages[-1].lower()}"
                )

            tooltip_text_stages = (
                f"For the analysis of results you can select among: {stages_text}"
            )

            # Select the life cycle stage
            life_cycle_stage = st.selectbox(":material/cycle: Life cycle stage *", available_lc_stages,
                                                    help=tooltip_text_stages)
            

        with st.expander(":material/image: Display a diagram of emission compartments", type="compact"):
                        # Define link section in the user's guide
            link_env_compartment = "https://ciraig.github.io/lilca-plastic-footprint-guide/03_applying-cfs-in-lca.html#environmental-compartment"
            st.markdown(f"You can also consult the [Environmental compartment]({link_env_compartment}) section of the user guide for the recommended alignment between PFN release compartments and those defined for MarILCA’s CFs.")
            st.image("./assets/images/emission_compartments.jpg")
            st.markdown("**Source**: [Louvet et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0959652625025740)")


        # Define a row for the life cycle stage, polymer and amount of polymer

        # Define a form, so the user can submit a new flow
        with st.form(f"add_flow_{module_key}_direct_micro", clear_on_submit=True, border=False):

            submitted = st.form_submit_button("Add flow", type="primary")

    if not submitted:
        return None
    if not product_name:
        st.error("Product or component identification is required.")
        return None

    return {
        "id": str(uuid.uuid4())[:8],
        "situation": "direct_micro",
        "product_name": product_name,
        "life_cycle_stage": life_cycle_stage,
        "product_type": product_type,
        "country": country,
        "polymer": polymer,
        "shape": particle_shape,
        "size": particle_size,
        "micro_mass_kg": mass_selected_units * conv_fact_to_std_unit,
        "emission_compartment": compartment
    }