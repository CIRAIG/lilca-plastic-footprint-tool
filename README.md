# LiLCA Plastic Footprint Tool

A web application that helps life cycle assessment (LCA) practitioners estimate microplastic emissions and characterize their potential impacts on ecosystem quality. It is the companion tool to the [LiLCA (Litter Impacts in LCA) Plastic Footprint Guide](https://ciraig.github.io/marilca-practitioner-guide/).

**Live app:** <https://lilca-plastic-footprint-tool.streamlit.app>

## What it does

The tool follows the plastic footprint definition used in the guide: (1) the mass of plastic entering the environment, with its polymer, size and shape, and (2) the resulting environmental impacts.

1. **Life cycle inventory (LCI).** Estimate microplastic emissions (kg) for the sector modules of the Plastic Footprint Network (PFN). Flows can be entered directly as microplastic emissions, or calculated from macroplastic mass (e.g. packaging, textiles, tires) using fragmentation, shape and size assumptions.
2. **Life cycle impact assessment (LCIA).** Characterize the inventory with MarILCA characterization factors (CFs) for the physical effects of microplastic ingestion on biota, for the available impact methods and indicator levels. The potential impact of each flow is calculated as:

   **potential impact = inventory (kg) × CF**

3. **Results and export.** Explore results by product, polymer, country, life cycle stage, emission compartment, shape, size and ecosystem, using stacked bar charts, Sankey diagrams and an uncertainty range figure. Export the study setup, LCI, LCIA and a column dictionary to Excel.

## Application modules

Agriculture, Textiles and apparel, Fishing and gear, Packaging, Transport (tires) and Waste, aligned with the PFN sectors. See the app for the modules whose calculations are currently available.

## Uncertainty range

The uncertainty figure shows the sum, across flows, of the lower and upper 95% limits of the CFs. It is **not** the result of a Monte Carlo simulation and is not a 95% confidence interval of the total. It reflects only CF uncertainty; inventory masses and macro-to-micro parameters are treated as exact.

## Run locally

Requires Python 3.11 or newer.

```bash
git clone https://github.com/ciraig/lilca-plastic-footprint-tool.git
cd lilca-plastic-footprint-tool
python -m venv .venv
.venv\Scripts\activate        # macOS/Linux: source .venv/bin/activate
pip install -r requirements.txt
streamlit run app.py
```

## Project structure

```
app.py          Entry point and navigation
pages/          App pages (welcome, study setup, module flows, results, export)
core/           Calculation, data loading, forms, visualization and styling code
data/           Input data (characterization factors, region mapping, defaults)
assets/         Images and custom CSS
.streamlit/     Theme configuration
```

## Data privacy

Studies are kept in your browser session only and are not stored on the server. Use the Excel export to save your work.

## Citation

If you use this tool, please cite the guide and the tool:

> *Authors.* LiLCA Plastic Footprint Tool, version X.Y (year). <https://github.com/ciraig/lilca-plastic-footprint-tool>

## Acknowledgements

Developed at [CIRAIG](https://ciraig.org/). Characterization factors were developed within the MarILCA working group.

## License

The source code is released under the [GNU General Public License v3.0](LICENSE). Data files, the MarILCA characterization factors, and the CIRAIG and MarILCA logos may be subject to their own terms and are not covered by the GPL.

## Contact

*Email*: lilca@ciraig.org
