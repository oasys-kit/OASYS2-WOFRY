from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangewidget.settings import Setting

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1DWithBoundaryShape
from syned.beamline.optical_elements.absorbers.slit import Slit

from wofryimpl.beamline.optical_elements.absorbers.slit import WOGaussianSlit1D

class OWWOGaussianSlit1D(OWWOOpticalElement1DWithBoundaryShape):

    name = "Gaussian Slit 1D"
    description = "Wofry: Gaussian Slit 1D"
    icon = "icons/slit1d.png"
    priority = 22

    vertical_shift = Setting(0.0)

    height = Setting(0.0001)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOGaussianSlit1D(name=self.oe_name,boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Slit):
            raise Exception("Syned Data not correct: Optical Element is not a Slit")

add_widget_parameters_to_module(__name__)