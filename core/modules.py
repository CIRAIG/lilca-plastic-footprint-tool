"""
Registry of PFN modules.

Keeping this in one place means the sidebar, the flow builder, and the
LCI engine all agree on what a "module" is.
"""
# PFN modules in scope
# `lci_ready` marks whether core/flow_forms.py has a real estimation function
# for it yet, vs. the generic placeholder.
PFN_MODULES = {
    "agriculture": {
        "label": "Agriculture", "icon": "agriculture",
        "lci_ready": False, "situations": ["direct_micro"],
    },
    "textiles": {
        "label": "Textiles and apparel", "icon": "laundry",
        "lci_ready": True, "situations": ["macro_to_micro", "direct_micro"],
    },
    "fishing_gear": {
        "label": "Fishing and gear", "icon": "phishing",
        "lci_ready": False, "situations": ["macro_to_micro", "direct_micro"],
    },
    "packaging": {
        "label": "Packaging", "icon": "shopping_bag",
        "lci_ready": True, "situations": ["macro_to_micro", "direct_micro"],
    },
    "transport_tires": {
        "label": "Transport (tires)", "icon": "local_shipping",
        "lci_ready": True, "situations": ["macro_to_micro", "direct_micro"],
    },
    "waste": {
        "label": "Waste", "icon": "recycling",
        "lci_ready": False, "situations": ["direct_micro"],
    },
}

# Life cycle stages that are accounted for in each PFN module
LIFE_CYCLE_STAGES_MODULES = {
    "agriculture": ["Use", "End-of-life"],
    "textiles": ["Production", "Use", "End-of-life"],
    "fishing_gear": ["End-of-life"],
    "packaging" : ["End-of-life"],
    "transport_tires": ["Transport"],
    "waste": ["End-of-life"]
}

LIFE_CYCLE_STAGES = ["Production", "Use", "Transport","End-of-life"]