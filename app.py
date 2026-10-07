import streamlit as st


# -----------------------------------------------------------------------------
# Page title
# -----------------------------------------------------------------------------

st.set_page_config(page_title="LiLCA Plastic Footprint Tool", 
                   page_icon="./assets/images/seahorse_logo.png", layout="wide")


# -----------------------------------------------------------------------------
# Sidebar logo
# -----------------------------------------------------------------------------

st.logo(
    image="./assets/images/lilca_logo_tool_crop.png",
    size = "large"
)



# ------------------------------------------------------------------
# Session state: one "study" is a full product-assessment case
# Scenario comparison works by duplicating a study, so studies are keyed
# by id from the start rather than assuming a single global study.
# ------------------------------------------------------------------
if "studies" not in st.session_state:
    st.session_state.studies = {}
if "current_study_id" not in st.session_state:
    st.session_state.current_study_id = None

# -----------------------------------------------------------------------------
# Pages setup
# -----------------------------------------------------------------------------

pages = [
    st.Page("pages/0_Welcome_page.py", title="Welcome page", icon=":material/waving_hand:"),
    st.Page("pages/1_Study_setup.py", title="Study setup", icon=":material/settings:"),
    st.Page("pages/2_Module_flows.py", title="Module flows", icon=":material/input:"),
    st.Page("pages/3_Results.py", title="Results", icon=":material/bar_chart:"),
    st.Page("pages/4_Export.py", title="Export", icon=":material/download:"),
]

nav = st.navigation(pages, position='hidden')

with st.sidebar:
    st.markdown("**LiLCA Plastic Footprint Tool**")
    for page in pages:
        st.page_link(page)

nav.run()
