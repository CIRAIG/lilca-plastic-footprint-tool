import uuid

import streamlit as st

from core.modules import PFN_MODULES


# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------

st.markdown("# :material/settings: Study setup")


# -----------------------------------------------------------------------------
# Description
# -----------------------------------------------------------------------------

st.markdown(
    """
    :material/tooltip: Define a study and select the **PFN modules** relevant
    to it; the modules selected here determine which options are displayed in
    the sidebar of the :material/input: **Module flows** page.
    """
)


# -----------------------------------------------------------------------------
# Form
# -----------------------------------------------------------------------------

with st.form("new_study_form"):
    study_name = st.text_input(
        ":material/label: **Study name**",
        max_chars=100,
        placeholder="e.g. Polyester-cotton t-shirt, baseline",
        help=(
            "Enter a unique name for the study. This name is used to identify "
            "the study throughout the application, including in results and "
            "exported files."
        ),
    )

    functional_unit = st.text_input(
        ":material/straighten: **Functional unit**",
        placeholder="e.g. 1 Polyester-cotton t-shirt used over its full lifetime",
        help=(
            "Define the reference unit used to quantify the product system being assessed, "
            "for example, one product over its full lifetime. "
            "**Users are responsible for scaling their inputs to match the defined functional unit.**"
        ),
    )

    selected_modules = st.multiselect(
        ":material/deployed_code: **PFN modules included in this study**",
        options=list(PFN_MODULES.keys()),
        format_func=lambda key: PFN_MODULES[key]["label"],
        help=(
            "Select the PFN modules that are relevant to this study. "
            "The selected modules determine which flow options are available "
            "on the :material/input: **Module flows** page."
        ),
    )

    submitted = st.form_submit_button(
        "Create study",
        help="Create the study using the information entered above.",
    )


# -----------------------------------------------------------------------------
# Session initialization
# -----------------------------------------------------------------------------

if submitted:
    existing_names = {
        study["study_name"].strip().lower()
        for study in st.session_state.studies.values()
    }

    normalized_name = study_name.strip()

    if not normalized_name or not selected_modules:
        st.error("A study name and at least one module are required.")

    elif normalized_name.lower() in existing_names:
        st.error(
            f"Study name '{normalized_name}' is already in use. "
            "Study names must be unique so studies can be distinguished "
            "in results."
        )

    else:
        study_id = str(uuid.uuid4())[:8]

        st.session_state.studies[study_id] = {
            "study_name": normalized_name,
            "functional_unit": functional_unit.strip(),
            "modules": selected_modules,
            "flows": {module: [] for module in selected_modules},
        }

        st.session_state.current_study_id = study_id

        st.success(
            f"Study '{normalized_name}' created and set as current."
        )


# -----------------------------------------------------------------------------
# Existing studies
# -----------------------------------------------------------------------------

st.divider()
st.subheader("Existing studies")

if not st.session_state.studies:
    st.info("No studies yet — create one above.")

else:
    for study_id, study in st.session_state.studies.items():
        columns = st.columns([3, 3, 3, 2])

        columns[0].write(f"**{study['study_name']}**")
        columns[1].write(study["functional_unit"])
        columns[2].write(
            ", ".join(
                PFN_MODULES[module]["label"]
                for module in study["modules"]
            )
        )

        is_current = (
            study_id == st.session_state.current_study_id
        )

        if columns[3].button(
            "Current" if is_current else "Set as current",
            key=f"set_{study_id}",
            disabled=is_current,
            help=(
                "This is the study currently used throughout the application."
                if is_current
                else "Set this study as the current study."
            ),
        ):
            st.session_state.current_study_id = study_id
            st.rerun()