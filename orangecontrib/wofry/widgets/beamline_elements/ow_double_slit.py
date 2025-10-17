from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangecontrib.wofry.widgets.gui.ow_optical_element_2d import OWWOOpticalElement2DWithDoubleBoundaryShape
from syned.beamline.optical_elements.absorbers.slit import Slit
from wofryimpl.beamline.optical_elements.absorbers.slit import WOSlit

class OWWODoubleSlit(OWWOOpticalElement2DWithDoubleBoundaryShape):

    name = "DoubleSlit"
    description = "Wofry: DoubleSlit"
    icon = "icons/double_slit.png"
    priority = 42

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOSlit(name=self.oe_name,boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Slit):
            raise Exception("Syned Data not correct: Optical Element is not a Slit")

add_widget_parameters_to_module(__name__)