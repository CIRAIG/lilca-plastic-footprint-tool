"""
Definition of functions and objects for cross-module result visualization
"""

import pandas as pd
import numpy as np
import streamlit as st
import plotly.express as px
import plotly.graph_objects as go


# Define a dictionary to perform an aggregation of results (LCI)
AGGREGATION_COLS_LCI = {
    'Life cycle stage': 'life_cycle_stage',
    'Country': 'country',
    'Shape': 'shape',
    'Size (μm)': 'size',
    'Emission compartment': 'emission_compartment',
    'Polymer': 'polymer'

}

# Define a dictionary to perform an aggregation of results (LCIA)
AGGREGATION_COLS_LCIA = {
    'Ecosystem': 'ecosystem',
    'Life cycle stage': 'life_cycle_stage',
    'Country': 'country',
    'Shape': 'shape',
    'Size (μm)': 'size',
    'Emission compartment': 'emission_compartment'}

# Define a list of radio button options for displaying the results
OPTIONS_DISPLAY_RESULTS = ["Total", "Aggregate by"]

OPTIONS_DISPLAY_SANKEY = ["All polymers", "One polymer at a time"]

# Define font sizes for the plots
small_font_size = 16
medium_font_size = 18
big_font_size = 20

# Define some colors for the plots
very_dark = "#222222"
color_text = "#696969" # dimgray 

#======================================================================================
# LCI
#======================================================================================

# Define a function to aggregate the LCI results based on the selected grouping column.
def aggregate_lci(lci_df, lci_agg_col=None, y_col="product_name"):

    if y_col not in lci_df.columns:
        raise KeyError(
            f"Column '{y_col}' not found in the LCI table. "
            "Make sure product names are set (see label_products in build_lci_df)."
        )

    # No aggregation column selected:
    # keep one row per y_col value (product by default) and sum all microplastic emissions.
    if lci_agg_col is None:
        plot_lci_df = (
            lci_df.groupby(y_col, as_index=False)["micro_mass_kg"]
            .sum()
        )

        # Create a dummy column so that plot_lci() can still use Plotly's
        # color argument consistently.
        plot_lci_df["aggregation"] = "Total"

        title_lci = "Total microplastic emissions"

        return plot_lci_df, title_lci

    # Aggregation column selected
    agg_col_lci = AGGREGATION_COLS_LCI[lci_agg_col]

    # Aggregating by the column already shown on the y-axis is redundant: each bar would be a
    # single segment colored by its own label. The page should not offer this combination.
    if agg_col_lci == y_col:
        raise ValueError(
            f"Cannot aggregate by '{lci_agg_col}' when the y-axis already shows '{y_col}'."
        )

    # Aggregate first: multiple flow-level rows can share the same
    # (y_col, aggregation column) pair.
    plot_lci_df = (
        lci_df.groupby(
            [y_col, agg_col_lci],
            as_index=False
        )["micro_mass_kg"]
        .sum()
    )

    # Convert size to strings if using it for grouping.
    if agg_col_lci == "size":
        plot_lci_df[agg_col_lci] = plot_lci_df[agg_col_lci].astype(str)

    # Reactive title
    title_lci = f"Microplastic emissions grouped by {lci_agg_col.lower()}"

    return plot_lci_df, title_lci


# Define a function to generate a bar chart for LCI results.
def plot_lci(
    lci_agg_col=None,
    LCI_LCIA_COLOR_PALETTE=None,
    plot_lci_df=None,
    title_lci="",
    y_col="product_name",
):
    # Work on a copy so the caller's DataFrame is not modified
    plot_lci_df = plot_lci_df.copy()

    # Label shown for the y-axis
    y_label = {"product_name": "Product", "polymer": "Polymer"}.get(y_col, y_col)

    # Determine the column used for coloring/stacking
    if lci_agg_col is None:
        # No aggregation selected, thus one total bar per product
        agg_col_lci = "aggregation"
    else:
        agg_col_lci = AGGREGATION_COLS_LCI[lci_agg_col]

    # Define color dictionary
    kwargs_lci = {}

    if (
        LCI_LCIA_COLOR_PALETTE is not None
        and agg_col_lci in LCI_LCIA_COLOR_PALETTE
    ):
        kwargs_lci["color_discrete_map"] = (
            LCI_LCIA_COLOR_PALETTE[agg_col_lci]
        )

    # Total emissions per product (or per y_col)
    # Sort the y-axis by total emissions
    y_order_lci = (
        plot_lci_df.groupby(y_col)["micro_mass_kg"]
        .sum()
        .sort_values(ascending=True)
        .index
        .tolist()
    )

    # Order the stacked bars by total contribution
    stack_order_lci = (
        plot_lci_df.groupby(agg_col_lci)["micro_mass_kg"]
        .sum()
        .sort_values(ascending=False)
        .index
        .tolist()
    )

    # Convert the column to an ordered categorical column before plotting
    plot_lci_df[agg_col_lci] = pd.Categorical(
        plot_lci_df[agg_col_lci],
        categories=stack_order_lci,
        ordered=True,
    )

    # Labels
    if lci_agg_col is None:
        aggregation_label = "Total"
    else:
        aggregation_label = lci_agg_col

    # Create figure
    fig_lci = px.bar(
        plot_lci_df,
        x="micro_mass_kg",
        y=y_col,
        color=agg_col_lci,
        orientation="h",
        barmode="stack",
        title=title_lci,
        labels={
            agg_col_lci: aggregation_label,
            "micro_mass_kg": "Microplastics (kg)",
            y_col: y_label,
        },
        category_orders={
            y_col: y_order_lci,
            agg_col_lci: stack_order_lci,
        },
        **kwargs_lci,
    )

    # Axes
    fig_lci.update_xaxes(
        tickfont=dict(
            size=small_font_size,
            color=color_text,
        ),
    )

    fig_lci.update_yaxes(
        categoryorder="array",
        categoryarray=y_order_lci,
        automargin=True,  # leave room for long product names
        tickfont=dict(
            size=small_font_size,
            color=color_text,
        ),
    )

    # Layout
    fig_lci.update_layout(
        font=dict(
            size=small_font_size,
            color=very_dark,
        ),
        title=dict(
            font=dict(size=big_font_size)
        ),
        xaxis_title=dict(
            text="Microplastic emissions (kg)",
            font=dict(
                size=medium_font_size,
                color=color_text,
            ),
        ),
        yaxis_title=dict(
            text=y_label,
            font=dict(
                size=medium_font_size,
                color=color_text,
            ),
        ),
        legend=dict(
            title_font=dict(
                size=medium_font_size,
                color=color_text,
            ),
            font=dict(
                size=small_font_size,
                color=color_text,
            ),
        ),
    )

    fig_lci.update_traces(
        hoverlabel=dict(
            font_size=small_font_size,
        )
    )

    return fig_lci

# Sankey - LCI (one polymer at a time)
# LCI and LCIA Sankey diagrams by product.

DEFAULT_PALETTE = px.colors.qualitative.Plotly

# Flow levels shown after the (optional) product level. Polymer is kept because a product can
# contain several polymers (and the CFs are polymer-specific); dropping it would silently merge them.
FLOW_DIMS = ["polymer", "country", "life_cycle_stage", "emission_compartment", "shape", "size"]

# Synthetic last level of the LCIA diagrams
SINK_DIM = "total_impact_score"
SINK_LABEL = "Total potential impact"

DIM_DISPLAY_NAMES = {
    "product_name": "Product",
    "polymer": "Polymer",
    "country": "Country",
    "life_cycle_stage": "Life cycle stage",
    "emission_compartment": "Emission compartment",
    "shape": "Shape",
    "size": "Size (μm)",
    "ecosystem": "Ecosystem",
    SINK_DIM: "",          # empty: the sink tooltip shows only its label
}


def _size_label(value):
    """10.0 -> '10', so labels match the palette keys ('1', '10', '100', ...) even when a missing
    value has turned the size column into floats. Non-numeric values (e.g. 'Unknown') pass through."""
    if isinstance(value, (int, float, np.integer, np.floating)) and not isinstance(value, bool):
        return f"{value:g}"
    return str(value)


def _nonzero(df, value_col):
    return df.loc[(df[value_col] != 0) & (df[value_col].notna())].copy()


def _sankey_figure(sankey_df, dims, value_col, LCI_LCIA_COLOR_PALETTE, unit, title, empty_message,
                   sink_dim=None, sink_label=None):
    """Shared builder: one node per (level, value), links between consecutive levels.
    If sink_dim is given, a constant final level is added so everything flows into one total node."""
    if sankey_df.empty:
        st.info(empty_message)
        return None

    if sink_dim:
        sankey_df[sink_dim] = sink_label
    flow_dims = [d for d in dims if d != sink_dim]

    # Flag missing values instead of letting groupby silently drop those rows.
    # Fill BEFORE converting size to str, otherwise NaN becomes the string "nan".
    missing = sankey_df[flow_dims].isna().any(axis=1).sum()
    if missing:
        st.warning(f"{missing} row(s) had a missing value in one of the flow dimensions -- "
                   "labeled 'Unknown' below rather than dropped.")
    sankey_df[flow_dims] = sankey_df[flow_dims].fillna("Unknown")
    if "size" in flow_dims:
        sankey_df["size"] = sankey_df["size"].map(_size_label)

    # Levels that have a color palette, derived from dims (no hardcoded level indexes to keep in sync)
    level_to_color_map = {i: dim for i, dim in enumerate(dims) if dim in LCI_LCIA_COLOR_PALETTE}

    labels, node_levels = [], []
    label_to_idx = {}

    def get_idx(level, val):
        key = (level, val)
        if key not in label_to_idx:
            label_to_idx[key] = len(labels)
            labels.append(str(val))
            node_levels.append(level)
        return label_to_idx[key]

    sources, targets, values = [], [], []
    for i in range(len(dims) - 1):
        col_a, col_b = dims[i], dims[i + 1]
        grouped = sankey_df.groupby([col_a, col_b], as_index=False)[value_col].sum()
        for _, row in grouped.iterrows():
            sources.append(get_idx(i, row[col_a]))
            targets.append(get_idx(i + 1, row[col_b]))
            values.append(row[value_col])

    node_colors = []
    default_counters = {}
    missing_from_map = []
    for level, label in zip(node_levels, labels):
        map_key = level_to_color_map.get(level)
        color_map = LCI_LCIA_COLOR_PALETTE.get(map_key, {}) if map_key else {}
        if label in color_map:
            node_colors.append(color_map[label])
        else:
            if map_key:  # a palette exists for this level, but this label isn't in it
                missing_from_map.append((map_key, label))
            idx = default_counters.get(level, 0)
            node_colors.append(DEFAULT_PALETTE[idx % len(DEFAULT_PALETTE)])
            default_counters[level] = idx + 1

    if missing_from_map:
        st.caption(
            f":material/warning: {len(missing_from_map)} node label(s) had a color palette defined "
            f"for their level but no exact match -- fell back to a default color: {missing_from_map}"
        )

    node_customdata = [
        f"{DIM_DISPLAY_NAMES[dims[level]]}: " if DIM_DISPLAY_NAMES[dims[level]] else ""
        for level in node_levels
    ]

    fig = go.Figure(data=[go.Sankey(
        valueformat=".2e",
        valuesuffix=f" {unit}",
        textfont=dict(size=14, color="black"),
        link=dict(
            source=sources, target=targets, value=values,
            hovertemplate="%{source.label} → %{target.label}<br>%{value:.2e} " + unit + "<extra></extra>",
            color="#e5e5e5",
        ),
        node=dict(
            label=labels, color=node_colors, customdata=node_customdata, pad=15, thickness=20,
            hovertemplate="%{customdata}%{label}<br>%{value:.2e} " + unit + "<extra></extra>",
        ),
    )])
    fig.update_layout(title=title, font=dict(size=16))
    fig.update_traces(hoverlabel=dict(font_size=16))
    return fig


# LCI

def sankey_lci_all_products(lci_df, LCI_LCIA_COLOR_PALETTE, unit_lci):
    return _sankey_figure(
        _nonzero(lci_df, "micro_mass_kg"),
        ["product_name"] + FLOW_DIMS,
        "micro_mass_kg", LCI_LCIA_COLOR_PALETTE, unit_lci,
        title=f"Life cycle inventory flow ({unit_lci})",
        empty_message="No flows to display.",
    )


def sankey_lci(lci_df, selected_product, LCI_LCIA_COLOR_PALETTE, unit_lci):
    return _sankey_figure(
        _nonzero(lci_df.loc[lci_df["product_name"] == selected_product], "micro_mass_kg"),
        FLOW_DIMS,
        "micro_mass_kg", LCI_LCIA_COLOR_PALETTE, unit_lci,
        title=f"Life cycle inventory flow ({unit_lci}) - {selected_product}",
        empty_message="No flows for this product.",
    )


# LCIA

def sankey_lcia_all_products(lcia_df, LCI_LCIA_COLOR_PALETTE, unit_lcia):
    return _sankey_figure(
        _nonzero(lcia_df, "impact_score"),
        ["product_name"] + FLOW_DIMS + ["ecosystem", SINK_DIM],
        "impact_score", LCI_LCIA_COLOR_PALETTE, unit_lcia,
        title=f"Contribution flow to potential impacts on ecosystem quality ({unit_lcia})",
        empty_message="No flows to display.",
        sink_dim=SINK_DIM, sink_label=SINK_LABEL,
    )


def sankey_lcia(lcia_df, selected_product, LCI_LCIA_COLOR_PALETTE, unit_lcia):
    return _sankey_figure(
        _nonzero(lcia_df.loc[lcia_df["product_name"] == selected_product], "impact_score"),
        FLOW_DIMS + ["ecosystem", SINK_DIM],
        "impact_score", LCI_LCIA_COLOR_PALETTE, unit_lcia,
        title=f"Contribution flow to potential impacts on ecosystem quality ({unit_lcia}) - {selected_product}",
        empty_message="No flows for this product.",
        sink_dim=SINK_DIM, sink_label=SINK_LABEL,
    )

#======================================================================================
# LCIA
#======================================================================================

# Define a function to aggregate the LCIA results based on the selected grouping column.
def aggregate_lcia(lcia_df, lcia_agg_col=None):
    group_cols = ["polymer", "impact_method", "unit"]

    if lcia_agg_col is not None:
        agg_col_lcia = AGGREGATION_COLS_LCIA[lcia_agg_col]
        group_cols.insert(1, agg_col_lcia)

    plot_lcia_df = (
        lcia_df
        .groupby(group_cols, as_index=False)["impact_score"]
        .sum()
    )

    # Convert size to strings if using it for aggregation
    if lcia_agg_col is not None and agg_col_lcia == "size":
        plot_lcia_df[agg_col_lcia] = plot_lcia_df[agg_col_lcia].astype(str)

    return plot_lcia_df



def plot_lcia(lcia_agg_col, LCI_LCIA_COLOR_PALETTE, plot_lcia_df, title_lcia):

    # Total results
    if lcia_agg_col is None:

        polymer_order_lcia = (
            plot_lcia_df
            .groupby("polymer")["impact_score"]
            .sum()
            .sort_values(ascending=True)
            .index
            .tolist()
        )

        unit_lcia = plot_lcia_df["unit"].dropna().unique()[0]

        fig_lcia = px.bar(
            plot_lcia_df,
            x="impact_score",
            y="polymer",
            orientation="h",
            title=title_lcia,
            labels={
                "impact_score": f"Impact score ({unit_lcia})",
                "polymer": "Polymer",
            },
            category_orders={
                "polymer": polymer_order_lcia,
            },
            color_discrete_sequence=["orange"],
        )

    # Aggregated results
    else:

        agg_col_lcia = AGGREGATION_COLS_LCIA[lcia_agg_col]

        kwargs_lcia = {}
        if agg_col_lcia in LCI_LCIA_COLOR_PALETTE:
            kwargs_lcia["color_discrete_map"] = (
                LCI_LCIA_COLOR_PALETTE[agg_col_lcia]
            )

        polymer_order_lcia = (
            plot_lcia_df
            .groupby("polymer")["impact_score"]
            .sum()
            .sort_values(ascending=True)
            .index
            .tolist()
        )

        unit_lcia = plot_lcia_df["unit"].dropna().unique()[0]

        stack_order_lcia = (
            plot_lcia_df
            .groupby(agg_col_lcia)["impact_score"]
            .sum()
            .sort_values(ascending=False)
            .index
            .tolist()
        )

        plot_lcia_df[agg_col_lcia] = pd.Categorical(
            plot_lcia_df[agg_col_lcia],
            categories=stack_order_lcia,
            ordered=True,
        )

        fig_lcia = px.bar(
            plot_lcia_df,
            x="impact_score",
            y="polymer",
            color=agg_col_lcia,
            orientation="h",
            barmode="stack",
            title=title_lcia,
            labels={
                agg_col_lcia: lcia_agg_col,
                "impact_score": f"Impact score ({unit_lcia})",
                "polymer": "Polymer",
            },
            category_orders={
                "polymer": polymer_order_lcia,
                agg_col_lcia: stack_order_lcia,
            },
            **kwargs_lcia,
        )

    # Common formatting
    fig_lcia.update_xaxes(
        tickformat=".2e",
        tickfont=dict(
            size=small_font_size,
            color=color_text,
        ),
    )

    fig_lcia.update_yaxes(
        categoryorder="array",
        categoryarray=polymer_order_lcia,
        tickfont=dict(
            size=small_font_size,
            color=color_text,
        ),
    )

    fig_lcia.update_layout(
        font=dict(
            size=small_font_size,
            color=very_dark,
        ),
        title=dict(
            font=dict(size=big_font_size),
        ),
        xaxis_title=dict(
            text=f"Impact score ({unit_lcia})",
            font=dict(size=medium_font_size, color=color_text),
        ),
        yaxis_title=dict(
            text="Polymer",
            font=dict(size=medium_font_size, color=color_text),
        ),
        legend=dict(
            title_font=dict(size=medium_font_size, color=color_text),
            font=dict(size=small_font_size, color=color_text),
        ),
    )

    fig_lcia.update_traces(
        hoverlabel=dict(
            font_size=small_font_size,
        )
    )

    return fig_lcia


#Mean impact score per product with its uncertainty range.

SCORE_COLS = ["impact_score", "impact_score_ll_95", "impact_score_ul_95"]

def aggregate_lcia_uncertainty(lcia_df, y_col="product_name"):
    """Total mean impact and range per product.

    Returns (df, n_rows_excluded, products_with_mean_outside_range).
    Only rows that have the mean AND both limits are used, so the dot and the range always come
    from the same set of rows. Products whose total impact is 0 are dropped (nothing to show,
    and 0 cannot be drawn on a log axis).
    """
    complete = lcia_df.dropna(subset=SCORE_COLS)
    n_excluded = len(lcia_df) - len(complete)

    out = complete.groupby(y_col, as_index=False)[SCORE_COLS].sum()
    out = out[out["impact_score"] != 0].copy()

    inconsistent = out.loc[
        (out["impact_score"] < out["impact_score_ll_95"]) | (out["impact_score"] > out["impact_score_ul_95"]),
        y_col,
    ].tolist()
    return out, n_excluded, inconsistent


def plot_lcia_uncertainty(unc_df, unit_lcia, title, y_col="product_name", log_x=True):
    df = unc_df.copy()
    # asymmetric error bars: distance from the mean to each limit
    # (clipped at 0: if a mean ever falls outside its own range, no negative bar is drawn)
    df["err_plus"] = (df["impact_score_ul_95"] - df["impact_score"]).clip(lower=0)
    df["err_minus"] = (df["impact_score"] - df["impact_score_ll_95"]).clip(lower=0)

    y_label = {"product_name": "Product", "polymer": "Polymer"}.get(y_col, y_col)
    y_order = df.sort_values("impact_score")[y_col].tolist()      # largest on top, as in plot_lci

    fig = px.scatter(
        df, x="impact_score", y=y_col,
        error_x="err_plus", error_x_minus="err_minus",
        log_x=log_x, title=title,
        category_orders={y_col: y_order},
        custom_data=["impact_score_ll_95", "impact_score_ul_95"],
        labels={"impact_score": f"Impact score ({unit_lcia})", y_col: y_label},
    )
    fig.update_traces(
        marker=dict(symbol="circle", size=11, color="#006f9f"),
        error_x=dict(color="#006f9f", thickness=1.8, width=7),
        hovertemplate=(
            "<b>%{y}</b><br>Mean: %{x:.2e} " + unit_lcia +
            "<br>Lower limit: %{customdata[0]:.2e}<br>Upper limit: %{customdata[1]:.2e}<extra></extra>"
        ),
    )
    fig.update_yaxes(categoryorder="array", categoryarray=y_order, automargin=True)
    fig.update_xaxes(exponentformat="power", showexponent="all")
    return fig