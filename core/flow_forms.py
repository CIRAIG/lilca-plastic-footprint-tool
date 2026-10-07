"""
📝 Registry: which module keys have a dedicated situation-1 (macro-to-micro)
form. 

Modules not listed here only offer situation 2 (direct entry).
"""

from core.flow_indirect_micro_packaging import render_packaging_macro_to_micro_form
from core.flow_indirect_micro_textiles import render_textiles_macro_to_micro_form
from core.flow_indirect_micro_tires import render_tires_macro_to_micro_form


SITUATION_1_FORM_RENDERERS = {
    "packaging": render_packaging_macro_to_micro_form,
    "textiles": render_textiles_macro_to_micro_form,
    "transport_tires": render_tires_macro_to_micro_form
}