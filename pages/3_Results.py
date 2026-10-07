import pandas as pd
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go

from core.color_palette import LCI_LCIA_COLOR_PALETTE
from core.data_marilca import(
    CF_TABLE, COUNTRIES_USEtox_REGIONS, CF_INDICATOR_LEVEL
)

from core.results_viz import(
    AGGREGATION_COLS_LCI, AGGREGATION_COLS_LCIA, OPTIONS_DISPLAY_RESULTS,
    aggregate_lci, plot_lci, aggregate_lcia, plot_lcia, sankey_lcia, sankey_lcia_all_products, 
    sankey_lci, sankey_lci_all_products, aggregate_lcia_uncertainty, plot_lcia_uncertainty

)


# Define sections in the sidebar
SECTIONS_RESULTS = {
    "lci": ("data_table", "Life Cycle Inventory: Microplastic emissions"),
    "lcia": ("stacked_bar_chart", "Potential impacts on ecosystem quality"),
}

def section_header(key):
    icon, title = SECTIONS_RESULTS[key]
    st.header(f":material/{icon}: {title}", anchor=key)

with st.sidebar:
    st.markdown("**On this page**")
    st.markdown("  \n".join(
        f"[:material/{icon}: {title}](#{key})" for key, (icon, title) in SECTIONS_RESULTS.items()
    ))


# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------
st.title(":material/bar_chart: Results")

study_id = st.session_state.current_study_id
if study_id is None:
    st.warning("Create or select a study on the :material/settings: **Study setup** page first.")
    st.stop()

study = st.session_state.studies[study_id]
st.markdown(f"#### :material/label: Study: **{study['study_name']}** | :material/straighten: Functional unit: **{study['functional_unit']}**")

# # ------------------------------------------------------------------
# # Generate LCI table
# # ------------------------------------------------------------------

all_flows = [(m, f) for m in study["modules"] for f in study["flows"][m]]
if not all_flows:
    st.info("No flows entered yet. Add some on the **Module flows** page.")
    st.stop()

@st.cache_data
def build_lci_df(all_flows, study_name, study_functional_unit):
    lci_df = pd.DataFrame([
        {
            "study_name": study["study_name"],
            "functional_unit": study["functional_unit"],
            "module": m,
            **f,
        }
        for m, f in all_flows
    ])

    # Join USEtox regions
    lci_df = (
        lci_df.merge(
            COUNTRIES_USEtox_REGIONS,
            left_on="country",
            right_on="country_ecoinvent",
            how='left'
        )
        .drop(columns="country_ecoinvent")
    )
    return lci_df

lci_df = build_lci_df(all_flows, study["study_name"], study["functional_unit"])

st.divider()
section_header('lci')
st.caption("Life cycle inventory (LCI) results: mass of microplastics released across the life cycle, by country, stage, and compartment.")

# Define three columns for the groupping columns
lci_col1, lci_col2, lci_col3 = st.columns(3)
with lci_col1:
    lci_aggregation_mode = st.radio(
    "Show results",
    OPTIONS_DISPLAY_RESULTS,
    index=OPTIONS_DISPLAY_RESULTS.index("Aggregate by"),
    horizontal=True,
    key="radio_lci")

with lci_col2:
    # UI widget to select the grouping variable
    if lci_aggregation_mode == "Aggregate by":
        lci_agg_col = st.selectbox(
            ":material/table_chart: Aggregate by", 
            AGGREGATION_COLS_LCI.keys(), 
            index=4,
            help="Select the variable used to group the results in the chart below.")
    else:
        lci_agg_col = None

with lci_col3:
    pass



plot_lci_df, title_lci = aggregate_lci(lci_df, lci_agg_col)


fig_lci = plot_lci(lci_agg_col, LCI_LCIA_COLOR_PALETTE, plot_lci_df, title_lci, y_col="product_name")

st.plotly_chart(fig_lci, width='stretch')

# Display the underlying data of the above chart
with st.expander(":material/table_view: Show underlying aggregated data"):
    st.markdown(title_lci)
    st.dataframe(plot_lci_df, width="stretch")
    st.download_button(
        "Download CSV",
        plot_lci_df.to_csv(index=False),
        file_name=f"{title_lci.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )


# Sankey - LCI
st.divider()
st.subheader(":material/waterfall_chart: Sankey diagram of elementary flows")
st.caption("Explore how mass or impact is distributed across the life cycle, from source to receiving compartment.")

n_products = lci_df["product_name"].nunique()

SANKEY_ALL_PRODUCTS = "All products"
SANKEY_ONE_PRODUCT = "One product at a time"
SANKEY_PRODUCT_ICONS = {
    SANKEY_ALL_PRODUCTS: ":material/hub: All products",
    SANKEY_ONE_PRODUCT: ":material/filter_alt: One product at a time",
}

if n_products > 1:
    lci_sankey_options = st.radio(
        "**Sankey diagram display**",
        list(SANKEY_PRODUCT_ICONS),
        horizontal=True,
        key="radio_lci_sankey_options",
        format_func=lambda opt: SANKEY_PRODUCT_ICONS[opt],
        help="Aggregate all products into one diagram, or view them one at a time.",
    )
    if lci_sankey_options == SANKEY_ALL_PRODUCTS:
        fig_sankey_lci = sankey_lci_all_products(lci_df, LCI_LCIA_COLOR_PALETTE, "kg")
    else:
        selected_product_lci = st.selectbox(
            ":material/category: Product", sorted(lci_df["product_name"].dropna().unique()),
            key="sankey_product_lci",
            help="Select a product to display its contribution flow in the Sankey diagram.")
        fig_sankey_lci = sankey_lci(lci_df, selected_product_lci, LCI_LCIA_COLOR_PALETTE, "kg")
else:
    fig_sankey_lci = sankey_lci_all_products(lci_df, LCI_LCIA_COLOR_PALETTE, "kg")

if fig_sankey_lci is not None:
    st.plotly_chart(fig_sankey_lci, width="stretch")


# ------------------------------------------------------------------
# Characterization
# ------------------------------------------------------------------

st.divider()
section_header('lcia')
st.caption("Life cycle impact assessment (LCIA) results, expressed as potential damage to ecosystem quality.")

# Define columns to select the indicator
ind_col1, ind_col2, ind_col3 = st.columns(3)
with ind_col1:
    impact_indicator_level = st.selectbox(
        ":material/line_end: Impact indicator level", 
        CF_INDICATOR_LEVEL,
        help = "Select the impact indicator level to characterize the LCI of microplastics.",
        key="impact_indicator_level"
    )

    TEMPORAL_REPRESENTATION = (CF_TABLE[CF_TABLE['impact_indicator_level'] == impact_indicator_level]['temporal_representation']).unique().tolist()

with ind_col2:
    temporal_representation = st.selectbox(
        ":material/timer: Temporal representation",
        TEMPORAL_REPRESENTATION,
        help = 'Select the temporal representation of the characterization factors.',
        key = f"temporal_representation_{impact_indicator_level}"  
    )

with ind_col3:
    # Define three columns for the groupping columns
    IMPACT_METHODS = (CF_TABLE[(CF_TABLE['impact_indicator_level'] == impact_indicator_level)
                           & (CF_TABLE['temporal_representation'] == temporal_representation)]['impact_method']).unique().tolist()

    if not IMPACT_METHODS:
        st.warning("No characterization factors are available for this combination.")
        st.stop()

    DEFAULT_IMPACT_METHOD = "IMPACT World+"

    default_method_idx = (
        IMPACT_METHODS.index(DEFAULT_IMPACT_METHOD)
        if DEFAULT_IMPACT_METHOD in IMPACT_METHODS
        else 0
    )

    # UI widget to select the LCIA method
    impact_method = st.selectbox(
        ":material/energy_program_time_used: Impact method", IMPACT_METHODS,
        help = "Select the life cycle impact assessment method used to characterize the LCI of microplastics.",
        index = default_method_idx,
        key = f"impact_method_{impact_indicator_level}_{temporal_representation}")

if impact_indicator_level == "Midpoint":
    st.caption("The midpoint CFs are labeled here as **IMPACT World+**; however, they are also applicable to **GLAM** and **EF**.")

lcia_col1, lcia_col2, lcia_col3 = st.columns(3)

with lcia_col1:
    # 
    lcia_aggregation_mode = st.radio(
    "Show results",
    OPTIONS_DISPLAY_RESULTS,
    index= OPTIONS_DISPLAY_RESULTS.index("Aggregate by"),
    horizontal=True,)
        
with lcia_col2:
    # UI widget to select the grouping variable
    if lcia_aggregation_mode == "Aggregate by":
        lcia_agg_col = st.selectbox(
            ":material/table_chart: Aggregate by", 
            AGGREGATION_COLS_LCIA.keys(),
            help="Select the variable used to group the results in the chart below.",
            key="radio_lcia")
    else:
        lcia_agg_col = None




@st.cache_data
def build_lcia_df(lci_df, impact_method, impact_indicator_level, temporal_representation):
    cf_filtered = CF_TABLE[
        (CF_TABLE["impact_method"] == impact_method)
        & (CF_TABLE["impact_indicator_level"] == impact_indicator_level)
        & (CF_TABLE["temporal_representation"] == temporal_representation)
    ]

    lcia_df = lci_df.merge(cf_filtered, 
                        left_on=['USEtox_region', 'polymer', 'size', 'shape', 'emission_compartment'],
                        right_on=['region', 'polymer', 'size', 'shape', 'emission_compartment'],
                        how='left')

    # Compute potential impacts
    lcia_df['impact_score'] = lcia_df['micro_mass_kg'] * lcia_df['cf_value']
    lcia_df['impact_score_ll_95'] = lcia_df['micro_mass_kg'] * lcia_df['cf_ll_95']
    lcia_df['impact_score_ul_95'] = lcia_df['micro_mass_kg'] * lcia_df['cf_ul_95']
    return lcia_df

lcia_df = build_lcia_df(lci_df, impact_method, impact_indicator_level, temporal_representation)


# Reactive title: pulls the units straight from the DataFrame
unit_lcia = lcia_df["unit"].dropna().unique()[0]

# Make the tables available to the Export page
st.session_state.setdefault("last_results", {})
st.session_state["last_results"][study_id] = {
    "impact_method": impact_method,
    "unit": unit_lcia,
    "flow_ids": tuple(f["id"] for _, f in all_flows),
    "lci_df": lci_df,
    "lcia_df": lcia_df,
}

title_lcia = f"Potential impacts on ecosystem quality - {impact_method} ({unit_lcia})"

plot_lcia_df = aggregate_lcia(lcia_df, lcia_agg_col)
fig_lcia = plot_lcia(lcia_agg_col, LCI_LCIA_COLOR_PALETTE, plot_lcia_df, title_lcia)

st.plotly_chart(fig_lcia, width='stretch')

with st.expander(":material/table_view: Underlying aggregated data"):
    st.markdown(title_lcia)
    st.dataframe(plot_lcia_df, width="stretch")
    st.download_button(
        "Download CSV",
        plot_lcia_df.to_csv(index=False),
        file_name=f"{title_lcia.lower().replace(' ', '_')}.csv",
        mime="text/csv",
    )

# Uncertainty

show_uncertainty = st.checkbox(
    ":material/scatter_plot: Show uncertainty range",
    key="show_lcia_uncertainty",
    help="Shows the total mean impact score of each product with the range between the lower and "
        "upper 95% limits of the characterization factors.",
)


if show_uncertainty:
    unc_df, n_excluded, inconsistent = aggregate_lcia_uncertainty(lcia_df)

    if unc_df.empty:
        st.info("No product has a non-zero impact score with uncertainty limits.")
    else:
        log_scale = st.radio(
            "X-axis scale", ["Logarithmic", "Linear"], horizontal=True, key="radio_lcia_uncertainty_scale",
            help="Impacts of different products often differ by orders of magnitude; a logarithmic axis "
                 "keeps all products and their ranges readable.",
        ) == "Logarithmic"

        fig_unc = plot_lcia_uncertainty(
            unc_df, unit_lcia,
            f"Mean impact score and uncertainty range - {impact_method} ({unit_lcia})",
            log_x=log_scale,
        )
        st.plotly_chart(fig_unc, width="stretch")

        if n_excluded:
            st.caption(f":material/info: {n_excluded} row(s) without a characterization factor or without "
                       "uncertainty limits are not included in this figure.")
        if inconsistent:
            st.warning("For these products the mean falls outside its own range, check the CF limits: "
                       + ", ".join(inconsistent))

        with st.expander(":material/help: How to read this figure"):
            st.markdown(
                """
                The potential impact of each flow is calculated as:

                $$
                \\text{Potential impact} = \\text{Inventory (kg)} \\times \\text{CF}
                $$

                Each marker shows the total potential impact of a product, obtained by summing this
                result across all of its flows, using the central CF values. The horizontal bars show a
                range obtained by applying the lower and upper 95% limits of the CFs in the same way
                (inventory × lower or upper CF limit) and summing across all flows.

                **This range is not the result of a Monte Carlo simulation and is not a 95% confidence
                interval of the total.** It reflects only the uncertainty of the characterization
                factors; inventory masses and the parameters of the macro-to-micro calculations are
                treated as exact.

                Because it assumes all CFs reach their limits at once, it usually overstates the spread,
                but it is not guaranteed to do so for strongly skewed CFs. Use it to compare orders of
                magnitude between products. Do not use it to test whether two products differ
                significantly.
            """)

# Sankey - LCIA
st.divider()
st.subheader(":material/waterfall_chart: Contribution flow to potential impacts on ecosystem quality")
st.caption("Trace how impact score flows through product, polymer, country, life cycle stage, emission compartment, particle shape, size, and ecosystem.")

# Only products that actually have an impact score (flows without a matching CF are excluded)
products_lcia = sorted(
    lcia_df.loc[lcia_df["impact_score"].fillna(0) != 0, "product_name"].dropna().unique()
)

if len(products_lcia) > 1:
    lcia_sankey_options = st.radio(
        "**Sankey diagram display**",
        list(SANKEY_PRODUCT_ICONS),
        horizontal=True,
        key="radio_lcia_sankey_options",
        format_func=lambda opt: SANKEY_PRODUCT_ICONS[opt],
        help="Aggregate all products into one diagram, or view them one at a time.",
    )
    if lcia_sankey_options == SANKEY_ALL_PRODUCTS:
        fig_sankey_lcia = sankey_lcia_all_products(lcia_df, LCI_LCIA_COLOR_PALETTE, unit_lcia)
    else:
        selected_product_lcia = st.selectbox(
            ":material/category: Product", products_lcia,
            key="sankey_product_lcia",
            help="Select a product to display its contribution flow in the Sankey diagram.",
        )
        fig_sankey_lcia = sankey_lcia(lcia_df, selected_product_lcia, LCI_LCIA_COLOR_PALETTE, unit_lcia)
else:
    fig_sankey_lcia = sankey_lcia_all_products(lcia_df, LCI_LCIA_COLOR_PALETTE, unit_lcia)

if fig_sankey_lcia is not None:
    st.plotly_chart(fig_sankey_lcia, width="stretch")
