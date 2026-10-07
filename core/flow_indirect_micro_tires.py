"""
Flow-entry form renderers - 🛞 Tires
"""

import uuid
import streamlit as st
import pandas as pd
import plotly.express as px

from collections import defaultdict

from core.data_marilca import(
    PFN_MARILCA_COMPARTMENTS, COUNTRIES_MARILCA)
from core.data_pfn import (
    TIRES_RELEASE_RATES,
    TIRE_WEAR_PARAMS,
    ROADS_RR_TIRES,
    VEHICLE_MAIN_CATEGORIES,
    tires_loss_rate,
    tire_wear_params,
    tire_wear_params_def
)

# Import common elements
from core.flow_macro_micro_common_elements import (
    default_shape_size_based_on_product,
    select_mass_unit,
    input_stage_polymer_mass)

def render_tires_macro_to_micro_form(module_key):
    """
    Tires situation 1: a vehicle's tire wear (TRWP) is allocated to the
    specific transport demand entered by the user -- scaled to the
    passengers or cargo mass actually represented by the functional
    unit, rather than the vehicle's full capacity.

    Cascade: generic tire loss rate (mg/km, by vehicle category) ->
    adjusted loss rate (scaled by road, driving, and tire condition
    multiplier factors) -> allocated to the user's specific demand
    (amount of passengers/goods relative to the vehicle's average
    occupancy/load) over the travelled distance -> split across
    environmental compartments using road-type-dependent release
    rates -> microplastic mass per compartment.

    Unlike the packaging and textiles end-of-life modules, there is no
    mismanaged-waste-index or fragmentation step here: tire wear is a
    continuous abrasion process generated during normal vehicle use,
    not a waste-management outcome, so TRWP is treated as already
    microplastic at the point of generation.
    """
    with st.container(border=True):
        
        st.subheader("Product or component")
        c_product1, c_product2, c_product3 = st.columns(3)

        with c_product1:
            product_name_key = f"product_name_{module_key}"
            
            product_name = st.text_input(
                ":material/category: Product or component *",
                value=st.session_state.get(product_name_key, ""),
                placeholder="e.g. Transport of 1 passenger",
                help=(
                    "Identify the specific product, item, or component this flow belongs to. "
                    "Use this to group several polymer flows that together make up a single "
                    "product -- e.g. a packaging item made of a cap, body, and label (each a "
                    "different polymer); a garment made of a shell fabric, lining, and trims; "
                    "or a tire's tread versus sidewall compound. For a single-polymer product, "
                    "simply name the product or the service itself (e.g. 'Transport of 1 passenger')."
                ),
                key=product_name_key,
            )
        with st.container(border=True):
            st.subheader("Transport type selection",
                        help=f"Select a transport type (goods or passengers) to choose a more specific vehicle category and its corresponding average transported load (kg) or average occupancy.")
            col1, col2 = st.columns([1, 2.3])
            with col1:
                selected_main_vehicle_category = st.radio(
                    ":material/local_shipping: :material/directions_car: Vehicle main category *",
                    VEHICLE_MAIN_CATEGORIES,
                    horizontal=True
                )

                filtered_vehicles = tires_loss_rate[
                    tires_loss_rate["vehicle_main_category"] == selected_main_vehicle_category]['vehicle_category']

            # Define labels and indexes for vehicle categories
            if selected_main_vehicle_category == "Transport of goods":
                label_selected_vehicle_category = ":material/local_shipping: Vehicle category *"
        
            else:
                label_selected_vehicle_category = ":material/directions_car: Vehicle category *"

            with col2:
                selected_vehicle_category = st.selectbox(
                    label_selected_vehicle_category,
                    filtered_vehicles,
                    index= 2,
                    help="Select a vehicle category that best corresponds to your case study. Its description will appear below."
                )

                vehicle_definition = tires_loss_rate[
                    (tires_loss_rate["vehicle_main_category"] == selected_main_vehicle_category)
                    & (tires_loss_rate["vehicle_category"] == selected_vehicle_category)]['definition'].unique()[0]

            colsub1, colsub2 = st.columns([1, 2.3])
            with colsub2:
                st.caption(f"**Vehicle description**: {vehicle_definition}")

            
            if selected_main_vehicle_category == "Transport of goods":
                label_occupancy_load = ":material/local_shipping: Average transported load value (kg)"
                tooltip_occupancy_load = "Default load value (kg): the average cargo mass this vehicle category carries, as defined by the PFN. Replace it with a more recent or case-specific value if available."
                value_occupancy_load = tires_loss_rate[
                    (tires_loss_rate["vehicle_main_category"] == selected_main_vehicle_category)
                    & (tires_loss_rate["vehicle_category"] == selected_vehicle_category)]['average_transported_load_kg'].unique()[0]
                step_occupancy_load = 10.0
            else:
                label_occupancy_load = ":material/directions_car: Average occupancy (-)"
                tooltip_occupancy_load = "Average occupancy (–) assumed for this vehicle category (PFN default). Replace if a more accurate value is available for your case study."
                value_occupancy_load = tires_loss_rate[
                                (tires_loss_rate["vehicle_main_category"] == selected_main_vehicle_category)
                                & (tires_loss_rate["vehicle_category"] == selected_vehicle_category)]['average_vehicle_occupancy'].unique()[0]
                step_occupancy_load = 1.0

            colsub3, colsub4 = st.columns([1, 2.3])
            with colsub4:
                avg_occupancy_or_load = st.number_input(
                    label_occupancy_load,
                    value=round(value_occupancy_load, 0),
                    step=step_occupancy_load,
                    min_value=1.0,
                    help=tooltip_occupancy_load,
                    key=f"avg_occ_load_{module_key}_{selected_vehicle_category}"

                )

        with st.container(border=True):
            if selected_main_vehicle_category == "Transport of goods":
                passenger_goods_section = "Definition of transported goods"
                label_passenger_goods_amount = ":material/package_2: Mass of transported goods (kg)"
                tooltip_passenger_goods_amount = "Enter the mass of the transported good (kg), scaled to your functional unit."
                tooltip_passenger_goods_distance = "Enter the distance (km) travelled by the good."
                step_amount_passenger_goods = 0.1
            else:
                passenger_goods_section = "Definition of transported passengers"
                label_passenger_goods_amount = ":material/person: Number of passengers"
                tooltip_passenger_goods_amount = "Enter the number of passengers, scaled to your functional unit."
                tooltip_passenger_goods_distance = "Enter the distance (km) travelled by the passenger(s)."
                step_amount_passenger_goods = 1.0

            st.subheader(passenger_goods_section)

            col_passenger_goods1, col_passenger_goods2, col_passenger_goods3 = st.columns(3)
            with col_passenger_goods1:
                amount_passenger_goods = st.number_input(
                    label_passenger_goods_amount,
                    min_value=0.0,
                    value=1.0,
                    step= step_amount_passenger_goods,
                    help=tooltip_passenger_goods_amount
                ) 
            with col_passenger_goods2:
                km_distance = st.number_input(
                    ":material/distance: Travelled distance (km)",
                    min_value=1.0,
                    value=10.0,
                    step = 0.1,
                    help=tooltip_passenger_goods_distance
                )

            with col_passenger_goods3:
                country = st.selectbox(
                    ":material/public: Country *", COUNTRIES_MARILCA + ["World"], 
                    index=COUNTRIES_MARILCA.index("Canada"),
                    help="Select **World** if the country is unknown or not listed.",
                    key=f"macro_country_production_{module_key}"
                )
            
        with st.container(border=True):
            st.subheader(
                "Vehicle tire loss rate",
                help="The loss rate is estimated based on the selected vehicle type and parameters influencing tire wear."
            )

            # Default value of loss rate for the selected vehicle
            loss_rate_selected =tires_loss_rate[
                    (tires_loss_rate["vehicle_main_category"] == selected_main_vehicle_category)
                    & (tires_loss_rate["vehicle_category"] == selected_vehicle_category)]['loss_rate'].unique()[0]

            col_loss_rate1, col_loss_rate2, col_loss_rate3 = st.columns(3)

            with col_loss_rate1:
                loss_rate_generic = st.number_input(
                    "Loss rate (mg/km)",
                    value=loss_rate_selected,
                    min_value=0.0,
                    help=f"Default average loss rate (mg/km) for {selected_vehicle_category.lower()} based on PFN data.",
                    key=f"loss_rate_generic_{module_key}_{selected_vehicle_category}"
                )

            with st.expander("**Tire wear influencing parameters**"):

                st.markdown("""
                Ospital et al. [(2025)](https://doi.org/10.1016/j.jhazmat.2025.138986) parametrized the emission factor for TRWP, which is equivalent
                to the loss rate (LR). The adjusted loss rate ($LR_{\\mathrm{adjusted}}$) is calculated
                by multiplying the generic loss rate ($LR_{\\mathrm{generic}}$) by the product of the
                dimensionless multiplier factors ($f_p$) associated with the parameters described below.
                """)
                st.latex(r"LR_{adjusted} = LR_{generic} \times \prod_p f_p")

                st.markdown("The parameters below are provided with default values. " \
                "You can adjust these values if the road surface, driving or operating conditions, "
                "or vehicle and tire characteristics differ from those of your case study.",
                    help=(
                        "**How to use these parameters**\n\n"
                        "The figure below updates automatically based on the values you enter "
                        "for each parameter. The resulting **multiplier factor** is then used "
                        "to adjust the loss rate to reflect the conditions of your case study."))
                col_params1, col_params2, col_params3 = st.columns(3)
                with col_params1:
                    st.markdown("**:material/road: Road surface**")

                    pavement = tire_wear_params[tire_wear_params['parameter_classification'] == "Pavement"]['parameter']

                    help_pavement = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Pavement"]['tooltip'].iloc[0]

                    selected_pavement = st.radio("Pavement", 
                                            pavement,
                                            horizontal=True,
                                            help=help_pavement)

                    selected_pavement_value = tire_wear_params.loc[tire_wear_params['parameter'] == selected_pavement, 'parameter_value'].iloc[0]
                    

                    if selected_pavement == "Paved road":
                        microtexture = tire_wear_params[tire_wear_params['parameter_classification'] == "Microtexture"]['parameter']

                    else:
                        microtexture = tire_wear_params[
                            (tire_wear_params["parameter_classification"] == "Microtexture") &
                            (tire_wear_params["parameter"] != "Smooth/polished surface")]["parameter"]

                    help_microtexture = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Microtexture"]['tooltip'].iloc[0]

                    selected_microtexture = st.radio("Microtexture", 
                                                microtexture, 
                                                horizontal=True, 
                                                help=help_microtexture)

                    selected_microtexture_value = tire_wear_params.loc[tire_wear_params['parameter'] == selected_microtexture, 'parameter_value'].iloc[0]

                    
                    road_wetness = tire_wear_params[tire_wear_params['parameter_classification'] == "Road wetness"]['parameter']

                    help_wetness = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Road wetness"]['tooltip'].iloc[0]

                    selected_road_wetness = st.radio("Road wetness", 
                                                road_wetness,
                                                horizontal=True,
                                                help=help_wetness)

                    selected_road_wetness_value = tire_wear_params.loc[tire_wear_params['parameter'] == selected_road_wetness, 'parameter_value'].iloc[0]

                with col_params2:
                    st.markdown("**:material/swap_driving_apps_wheel: Driving/operation**")

                    driving_environment = tire_wear_params[tire_wear_params['parameter_classification'] == "Driving environment"]['parameter']
                    
                    help_driving_environment  = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Driving environment"]['tooltip'].iloc[0]
                    
                    selected_driving_environment = st.radio("Driving environment", 
                                                        driving_environment, 
                                                        horizontal=True,
                                                        help=help_driving_environment)
                    
                    selected_driving_environment_value = tire_wear_params[tire_wear_params['parameter'] == selected_driving_environment]['parameter_value'].iloc[0]

                    driving_style = tire_wear_params[tire_wear_params['parameter_classification'] == "Driving style"]['parameter']

                    help_driving_style = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Driving style"]['tooltip'].iloc[0]

                    selected_driving_style = st.radio("Driving style", 
                                                    driving_style,
                                                    horizontal=True,
                                                    help=help_driving_style)

                    selected_driving_style_value = tire_wear_params[tire_wear_params['parameter'] == selected_driving_style]['parameter_value'].iloc[0]
                    

                    speed = tire_wear_params[tire_wear_params['parameter_classification'] == "Speed"]['parameter'].iloc[0]

                    help_speed = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Speed"]['tooltip'].iloc[0]

                    if selected_driving_environment == "Urban":
                        selected_speed = st.checkbox(speed,
                                            help=help_speed)
                    else:
                        selected_speed = False

                    if selected_speed:
                        selected_speed_value = tire_wear_params.loc[tire_wear_params['parameter'] == 'Speed +10 km/h (alone)', 'parameter_value'].iloc[0]
                    else:
                        selected_speed_value = 1
                    
                    temperature = tire_wear_params[tire_wear_params['parameter_classification'] == "Temperature"]['parameter'].iloc[0]

                    help_temperature  = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Temperature"]['tooltip'].iloc[0]

                    selected_temperature = st.checkbox(
                                                temperature, 
                                                help=help_temperature)

                    if selected_temperature:
                        selected_temperature_value = tire_wear_params[tire_wear_params['parameter'] == "Temperature +10°C"]['parameter_value'].iloc[0]
                    else:
                        selected_temperature_value = 1

                with col_params3:
                    st.markdown("**:material/tire_repair: Vehicle and tires**")

                    tire_type = tire_wear_params[tire_wear_params['parameter_classification'] == "Tire type"]['parameter']

                    help_tire_type  = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Tire type"]['tooltip'].iloc[0]

                    selected_tire_type = st.radio("Tire type", 
                                                tire_type, 
                                                horizontal=True, 
                                                help=help_tire_type)

                    selected_tire_type_value = tire_wear_params[tire_wear_params['parameter'] == selected_tire_type]['parameter_value'].iloc[0]

                    additional_load = tire_wear_params[tire_wear_params['parameter_classification'] == "Additional load"]['parameter'].iloc[0]

                    help_additional_load  = tire_wear_params_def[tire_wear_params_def['parameter_classification'] == "Additional load"]['tooltip'].iloc[0]

                    if selected_main_vehicle_category == "Transport of passengers":
                        selected_additional_load = st.checkbox(additional_load,
                                                        help=help_additional_load)
                    else:
                        selected_additional_load =  False
                        

                    if selected_additional_load:
                        selected_additional_load_value = tire_wear_params.loc[tire_wear_params['parameter'] == "Load +20 kg", 'parameter_value'].iloc[0]
                    else:
                        selected_additional_load_value = 1

                # Generate a dictionary to handle the values for the tire wear influencing parameters
                dict_multiplier_factors = [
                        {
                            "category": "Pavement",
                            "label": selected_pavement,
                            "value": selected_pavement_value,
                        },
                        {
                            "category": "Microtexture",
                            "label": selected_microtexture,
                            "value": selected_microtexture_value,
                        },
                        {
                            "category": "Road wetness",
                            "label": selected_road_wetness,
                            "value": selected_road_wetness_value,
                        },
                        {
                            "category": "Driving environment",
                            "label": selected_driving_environment,
                            "value": selected_driving_environment_value,
                        },
                        {
                            "category": "Driving style",
                            "label": selected_driving_style,
                            "value": selected_driving_style_value,
                        },
                        {
                            "category": "Speed",
                            "label": selected_speed,
                            "value": selected_speed_value,
                        },
                        {
                            "category": "Temperature",
                            "label": selected_temperature,
                            "value": selected_temperature_value,
                        },
                        {
                            "category": "Tire type",
                            "label": selected_tire_type,
                            "value": selected_tire_type_value,
                        },
                        {
                            "category": "Additional load",
                            "label": selected_additional_load,
                            "value": selected_additional_load_value,
                        },
                    ]

                # Convert the dictionary into a data frame
                df_multiplier_factors = pd.DataFrame(dict_multiplier_factors)

                # Compute the multiplier factor
                multiplier_factor = round(df_multiplier_factors["value"].prod(), 2)

                # Display the multiplier factor
                st.caption(f"The overall multiplier factor ($\\prod_p f_p$) is **{multiplier_factor}**.")


                fig = px.bar(
                    df_multiplier_factors,
                    x="value",
                    y="category",
                    orientation="h",
                    custom_data=["label"],
                    category_orders={"category": df_multiplier_factors["category"].tolist()},
                    color_discrete_sequence=["#00A1C0"])

                fig.update_traces(
                    hovertemplate="<b>%{y}</b><br>"
                                "Selection: %{customdata[0]}<br>"
                                "fp: %{x}<extra></extra>"
                )

                fig.update_xaxes(title_text="Dimensionless multiplier factor")
                fig.update_yaxes(title_text="Parameter")

                st.plotly_chart(fig, width='stretch')

            # Adjusted loss rate (mg/km)
            loss_rate_adjusted = loss_rate_generic * multiplier_factor
            st.markdown(f"**Adjusted loss rate:** {round(loss_rate_adjusted, 2)} mg/km")

        with st.container(border=True):
            st.subheader("Release rates to the environment",
                         help="For TRWP, release rates to the environment are determined by the selected road type.")
            c_prod1, c_prod2, c_prod3 = st.columns(3)
            with c_prod1:
                road_type = st.selectbox(
                        ":material/public: Road *", ROADS_RR_TIRES, 
                        index=ROADS_RR_TIRES.index("Urban road"),
                        help="Select a road archetype.",
                        key=f"macro_road_type_{module_key}",
                    )
            with c_prod2:
                rr_ocean = st.number_input(
                    ":material/moving: :material/water: Release rate to ocean",
                    min_value=0.00,
                    max_value=1.00,
                    value= TIRES_RELEASE_RATES[(road_type, 'Ocean')], 
                    step=0.01,
                    help="Pre-filled based on the selected road type as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_ocean_{module_key}{road_type}"
                )
            with c_prod3:
                rr_frw = st.number_input(
                    ":material/moving: :material/waves: Release rate to freshwater",
                    min_value=0.00,
                    max_value=1.00,
                    value= TIRES_RELEASE_RATES[(road_type, 'Freshwater')], 
                    step=0.01,
                    help="Pre-filled based on the selected road type as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_frw_prod_{module_key}{road_type}"
                )

            c_prod4, c_prod5, c_prod6 = st.columns(3)
            with c_prod5:
                rr_soil = st.number_input(
                    ":material/moving: :material/wheat: Release rate to soil",
                    min_value=0.00,
                    max_value=1.00,
                    value= TIRES_RELEASE_RATES[(road_type, 'Soil')], 
                    step=0.01,
                    help="Pre-filled based on the selected road type as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_soil_prod_{module_key}{road_type}"
                )
            with c_prod6:
                rr_terenv = st.number_input(
                    ":material/moving: :material/grass: Release rate to terrestrial environment",
                    min_value=0.00,
                    max_value=1.00,
                    value= TIRES_RELEASE_RATES[(road_type, 'Terrestrial environment')], 
                    step=0.01,
                    help="Pre-filled based on the selected road type as defined by the PFN -- "
                        "edit directly if you have more recent or polymer-specific data.",
                    key=f"macro_rr_terenv_prod_{module_key}{road_type}"
                )
            # Stop if the addition of ocean and land release rates are superior to 1.
            if rr_ocean + rr_frw + rr_soil + rr_terenv  > 1.0:
                st.error(
                    f"Ocean + Freshwater + Soil + Terrestrial environment release rates must be ≤ 1. "
                    f"Current total: {rr_ocean + rr_frw + rr_soil + rr_terenv:.2f}"
                )
                st.stop()

        with st.container(border=True):
            product_type, particle_shape, particle_size = default_shape_size_based_on_product(module_key)


        with st.form(f"add_flow_{module_key}_macro_to_micro", clear_on_submit=True, border=False):
            # Set the default polymer
            polymer = "TRWP"

            # Set the default life cycle stage
            life_cycle_stage = "Transport"

            submitted = st.form_submit_button("Add flow", type="primary")
             

    if not submitted:
        return None
    if not product_name:
        st.error("Product or component identification is required.")
        return None

    release_rates_compartment = {
        PFN_MARILCA_COMPARTMENTS['Ocean']: rr_ocean,
        PFN_MARILCA_COMPARTMENTS['Soil']: rr_soil,
        PFN_MARILCA_COMPARTMENTS['Freshwater']: rr_frw,
        PFN_MARILCA_COMPARTMENTS['Terrestrial environment']: rr_terenv}
    

    flows = []

    for compartment, release_rate in release_rates_compartment.items():
        flows.append({
            "id": str(uuid.uuid4())[:8],
            "situation": "macro_to_micro",
            "product_name": product_name,
            "life_cycle_stage": life_cycle_stage,
            "country": country,
            "polymer": "TRWP",
            "shape": particle_shape,
            "size": particle_size,
            "selected_main_vehicle_category": selected_main_vehicle_category,
            "selected_vehicle_category": selected_vehicle_category,
            "avg_occupancy_or_load": avg_occupancy_or_load,
            "amount_passenger_goods": amount_passenger_goods,
            "km_distance": km_distance,
            "loss_rate_generic": loss_rate_generic,
            "selected_pavement": selected_pavement,
            "selected_pavement_value": selected_pavement_value,
            "selected_microtexture": selected_microtexture,
            "selected_microtexture_value": selected_microtexture_value,
            "selected_road_wetness": selected_road_wetness,
            "selected_road_wetness_value": selected_road_wetness_value, 
            "selected_driving_environment": selected_driving_environment,
            "selected_driving_environment_value": selected_driving_environment_value,
            "selected_driving_style": selected_driving_style,
            "selected_driving_style_value": selected_driving_style_value,
            "selected_speed": selected_speed,
            "selected_speed_value": selected_speed_value,
            "selected_temperature": selected_temperature,
            "selected_temperature_value": selected_temperature_value,
            "selected_tire_type": selected_tire_type,
            "selected_tire_type_value": selected_tire_type_value,
            "selected_additional_load": selected_additional_load,
            "selected_additional_load_value": selected_additional_load_value,
            "overall_multiplier_factor": multiplier_factor,
            "loss_rate_adjusted": loss_rate_adjusted,
            "emission_compartment": compartment,
            "release_rate": release_rate,
            "micro_mass_kg": amount_passenger_goods * km_distance  * loss_rate_adjusted * (1/1e6) * (1 / avg_occupancy_or_load) * release_rate,
        })
    if not flows:
        st.warning("No microplastic mass computed for either compartment -- check the inputs above.")
        return None
    return flows