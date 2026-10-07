import streamlit as st
from PIL import Image
from core.modules import PFN_MODULES

# -----------------------------------------------------------------------------
# Title
# -----------------------------------------------------------------------------
st.title("LiLCA (Litter Impacts in LCA) Plastic Footprint Tool")
st.image("./assets/images/lilca_logo_tool.png", width=250)

st.markdown(
"""
This application is the companion tool to the 
[LiLCA (Litter Impacts in LCA) Plastic Footprint Guide](https://ciraig.github.io/marilca-practitioner-guide/). 
It applies the methods described in the guide to calculate the **plastic footprint** of a product 
or system, following the definition of Corella-Puertas et al. (2026):

- **the mass of plastic litter entering the environment**, with information on polymer type, 
  particle size, and shape (life cycle inventory, LCI); and
- **its potential environmental impacts**, quantified with the **characterization factors (CFs)** 
  developed within the [MarILCA](https://marilca.org/) initiative, which link plastic emissions to 
  potential impacts on **ecosystem quality** through the effects on biota of microplastic 
  ingestion (life cycle impact assessment, LCIA).

The assessment focuses on the **plastic footprint**. Plastic emissions are estimated following the 
[Plastic Footprint Network (PFN)](https://www.plasticfootprint.earth/) guidelines, for conventional 
and biodegradable or bio-based polymers, cellulosic fibres, and tyre and road wear particles. 
Additional CFs will be incorporated in future revisions.

The application is designed to complement conventional LCA software. It supports practitioners in 
cases where the MarILCA CFs are not yet fully integrated into LCA databases and software platforms, 
by streamlining the preparation of the life cycle inventory and the subsequent application of the CFs, 
while keeping the assumptions, data choices, and calculation steps transparent.
""", text_alignment="justify"
)

SECTIONS = {
    "authors": ("group", "Authors"),
    "scope": ("radar", "Scope"),
    "modules": ("deployed_code", "Application modules"),
    "guide": ("book_ribbon", "LiLCA Plastic Footprint Guide"),
    "acknowledgements": ("volunteer_activism", "Acknowledgements"),
    "contact": ("contact_mail", "Contact"),
}

def section_header(key):
    icon, title = SECTIONS[key]
    st.header(f":material/{icon}: {title}", anchor=key)

with st.sidebar:
    st.markdown("**On this page**")
    st.markdown("  \n".join(
        f"[:material/{icon}: {title}](#{key})" for key, (icon, title) in SECTIONS.items()
    ))


# -----------------------------------------------------------------------------
# Authors
# -----------------------------------------------------------------------------

section_header("authors")

st.markdown(
"""
The following contributors participated in the development of this application by providing 
expertise in LCI modelling, the development of CFs,
and software implementation.

Several contributors have been actively involved in the [MarILCA initiative](https://marilca.org/project-framework-and-projects/), and all are 
affiliated with the **International Reference Centre for Life Cycle Assessment and Sustainable Transition** ([CIRAIG](https://ciraig.org/)).

* Anne-Marie Boulay [:material/badge:](https://ciraig.org/index.php/team/anne-marie-boulay/)
* Nadim Saadi [:material/badge:](https://ciraig.org/index.php/team/nadim-saadi/)
* Luc Dauge [:material/badge:](https://ciraig.org/index.php/team/luc-dauge/)
* Jérôme Lavoie [:material/badge:](https://ciraig.org/index.php/team/jerome-lavoie/)
* Ivan Viveros Santos [:material/badge:](https://ciraig.org/index.php/team/ivan-viveros-santos/)

""", text_alignment="justify"
)


# -----------------------------------------------------------------------------
# Scope
# -----------------------------------------------------------------------------

section_header("scope")


st.markdown(
"""
This application enables practitioners to:
- **estimate plastic emissions** (macroplastic leakage and the resulting microplastic emissions) 
  for the sectors covered by the [PFN](https://www.plasticfootprint.earth/) modules, with information 
  on polymer type, particle shape, and size;
- apply the [MarILCA CFs](https://marilca.org/characterization-factors/) to assess **potential impacts 
  on ecosystem quality** associated with the physical effects of microplastic ingestion on biota.

At this stage, the CFs implemented cover only these physical effects on biota. Other impact pathways 
are not assessed by the tool, and additional CFs will be incorporated as they become available.

The application is the companion tool to the 
[LiLCA Plastic Footprint Guide](https://ciraig.github.io/marilca-practitioner-guide/) 
and is intended to complement conventional LCA software. It does not replace the guide: 
the guide explains when plastic impacts should be accounted for in a study, how to interpret 
the results, and how to deal with uncertainties.

**It also does not replace the broader life cycle assessment, which remains the responsibility 
of the practitioner**. Users are responsible for collecting data for the LCI, conducting the 
assessment in accordance with ISO 14040 and ISO 14044, and interpreting the results within the 
context of the study goal and scope.
""", text_alignment="justify"
)

# -----------------------------------------------------------------------------
# Modules
# -----------------------------------------------------------------------------

section_header("modules")


st.markdown(
    "The application includes the sector modules developed by the "
    "[Plastic Footprint Network (PFN)](https://www.plasticfootprint.earth/), which provide emission "
    "factors for activities prone to plastic leakage. Each module estimates the microplastic "
    "emissions of a product or system, either from the amount of plastic used (where a PFN "
    "estimation method is available) or from microplastic emissions already known to the practitioner:",
    text_alignment="justify"
)

# Generate a string for the PFN modules (unordered list)
module_lines = "\n".join(
    f"- :material/{m['icon']}: **{m['label']}**" for m in PFN_MODULES.values()
)
st.markdown(module_lines)

st.markdown("Additional modules may be added as the PFN methodology continues to evolve.")


# -----------------------------------------------------------------------------
# Practitioner Guide
# -----------------------------------------------------------------------------

section_header("guide")


st.markdown(
"""
This tool is designed to be used together with the 
[LiLCA (Litter Impacts in LCA) Plastic Footprint Guide](https://ciraig.github.io/marilca-practitioner-guide/), 
which provides the methodological background and step-by-step support for assessing 
plastic impacts in LCA, from the preparation of inventory flows to the interpretation of results.

The guide is organized to follow the stages of an assessment:
- **Before you start**: the rationale behind the CFs and guidance on when plastic impacts should be 
  accounted for in a study, including screening questions to decide whether further assessment 
  is relevant and feasible.
- **While using the tool**: step-by-step guidance for the LCI, LCIA, and interpretation phases, 
  and the data sources available to quantify plastic emissions, including the Plastic Leak Project and 
  the Plastic Footprint Network, with their current coverage and gaps.
- **To see it applied**: case studies from selected industrial sectors, and a list of published 
  studies that include plastic impacts.
- **When you have questions**: recurring questions, frequently encountered issues, and 
  methodological uncertainties.

Developed jointly under the [MarILCA](https://marilca.org/) initiative and the 
[Plastocene research initiative](https://www.polymtl.ca/carrefour-actualite/en/news/new-funding-will-help-accelerate-market-impact-research-plastics-environmental-impact), 
the guide and this tool support the operational implementation of plastic impact assessment 
methods within LCA studies.
""", text_alignment="justify"
)


# -----------------------------------------------------------------------------
# Acknowledgements
# -----------------------------------------------------------------------------

section_header("acknowledgements")


st.markdown(
"""
The CFs implemented in this tool were developed within the [MarILCA](https://marilca.org/) initiative. 
The MarILCA working group was created in 2018 with the support of the 
[Life Cycle Initiative of UN Environment](https://www.lifecycleinitiative.org/) and the 
[Forum for Sustainability through Life Cycle Innovation (FSLCI)](https://fslci.org/).

The estimation of plastic emissions builds on the work of the 
[Plastic Footprint Network (PFN)](https://www.plasticfootprint.earth/) and the 
[Plastic Leak Project](https://quantis.com/services-solutions/consortium-building-and-management/plastic-leakage-project/), 
which developed emission factors for activities and sectors prone to plastic leakage.

This tool and the accompanying [LiLCA Plastic Footprint Guide](https://ciraig.github.io/marilca-practitioner-guide/) 
were developed to facilitate the practical implementation of these CFs within LCA studies. Their development 
was made possible through the [generous support](https://www.polymtl.ca/carrefour-actualite/en/news/new-funding-will-help-accelerate-market-impact-research-plastics-environmental-impact) 
of [Builders Vision Philanthropy](https://www.buildersvision.com/) to the Plastocene research initiative, 
led by CIRAIG at Polytechnique Montréal.
""", text_alignment="justify"
)

# -----------------------------------------------------------------------------
# Contact
# -----------------------------------------------------------------------------

section_header("contact")


st.markdown(
"""
For questions, bug reports, or suggestions regarding this tool, please contact the LiLCA team by email:
"""
)

with st.expander(":material/contact_mail: Contact"):
    st.markdown(
        "Email: [lilca@ciraig.org](mailto:lilca@ciraig.org?subject=LiLCA%20Plastic%20Footprint%20Tool)"
    )