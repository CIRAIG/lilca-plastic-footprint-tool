import streamlit as st

from core.modules import PFN_MODULES
from core.flow_form_direct_micro import render_direct_micro_form
from core.flow_forms import (
    SITUATION_1_FORM_RENDERERS,
)


# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------

st.title(":material/input: Module flows")

# -----------------------------------------------------------------------------
# Initialize page based on study_id (as defined at study setup)
# -----------------------------------------------------------------------------

study_id = st.session_state.current_study_id
if study_id is None:
    st.warning("Create or select a study on the :material/settings: **Study setup** page first.")
    st.stop()

study = st.session_state.studies[study_id]
st.markdown(f"## :material/label: Study: **{study['study_name']}**")

# ------------------------------------------------------------------
# Sidebar: pick which module you're adding flows to. Only modules
# chosen at study setup show up here.
# ------------------------------------------------------------------
with st.sidebar:
    st.header("PFN modules")
    module_key = st.radio(
        "Add flows to:",
        options=study["modules"],
        format_func=lambda k: f":material/{PFN_MODULES[k]['icon']}: {PFN_MODULES[k]['label']}",
    )
    for m in study["modules"]:
        n_flows = len(study["flows"][m])
        st.caption(f":material/{PFN_MODULES[m]['icon']}: {PFN_MODULES[m]['label']}: {n_flows} flow(s)")

module_label = PFN_MODULES[module_key]["label"]
st.markdown(f"### :material/{PFN_MODULES[module_key]['icon']}: {module_label}: add a flow")

if not PFN_MODULES[module_key]["lci_ready"]:
    st.info(f"No dedicated LCI model for **{module_label}** yet.")

# ------------------------------------------------------------------
# Situation selector. 
# Modules should support estimating microplastics from a macroplastic input (situation 1)
# in addition to direct microplastic-mass entry (situation 2).
# ------------------------------------------------------------------
situations = PFN_MODULES[module_key].get("situations", ["direct_micro"])
situations = [s for s in situations if s == "direct_micro" or module_key in SITUATION_1_FORM_RENDERERS]

situation_labels = {
    "macro_to_micro": ":material/conversion_path: From macroplastics (leakage and fragmentation)",
    "direct_micro": ":material/grain: Direct microplastic mass (already known)",
}

if len(situations) > 1:
    situation = st.radio(
        "How will you provide this flow's data?",
        options=situations,
        format_func=lambda s: situation_labels[s],
        horizontal=True,
        key=f"situation_{module_key}",
    )
else:
    situation = situations[0]

st.divider()

# ------------------------------------------------------------------
# Dispatch to the right form. Both paths return flow dict(s) using the
# same schema, so the storage/display logic below doesn't need to know
# which situation produced them. render_direct_micro_form() returns a
# single dict or None; situation-1 renderers return a list of dicts
# (one per compartment with non-zero leakage) or None.
# ------------------------------------------------------------------
if situation == "macro_to_micro":
    new_flows = SITUATION_1_FORM_RENDERERS[module_key](module_key)
else:
    result = render_direct_micro_form(module_key)
    new_flows = [result] if result is not None else None

if new_flows:
    study["flows"][module_key].extend(new_flows)
    st.success(f"{len(new_flows)} flow(s) added.")
    st.rerun()

st.divider()
st.subheader(f"{module_label}: flows in this study")

flows = study["flows"][module_key]
if not flows:
    st.info("No flows added yet for this module.")
else:
    for i, flow in enumerate(flows):
        cols = st.columns([5, 1])
        situation_tag = " :material/conversion_path:" if flow.get("situation") == "macro_to_micro" else ":material/grain:"
        if situation_tag == ":material/grain:":
            cols[0].write(
                f"{situation_tag} **{flow['polymer']}** -- {flow['micro_mass_kg']:.4g} kg, {flow['country']}, "
                f"{flow['life_cycle_stage']}, {flow['emission_compartment']}, "
                f"{flow['shape']} / {flow['size']} μm"
            )
        else:
            cols[0].write(
                f"{situation_tag} **{flow['polymer']}** -- {flow['micro_mass_kg']:.4g} kg, {flow['country']}, "
                f"{flow['life_cycle_stage']}, {flow['emission_compartment']}, "
                f"{flow['shape']} / {flow['size']} μm"
            )
        if cols[1].button("Remove", key=f"rm_{module_key}_{i}"):
            flows.pop(i)
            st.rerun()