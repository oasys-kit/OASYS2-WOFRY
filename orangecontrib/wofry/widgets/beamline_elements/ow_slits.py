from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangewidget.settings import Setting
from orangecontrib.wofry.widgets.gui.ow_optical_element_2d import OWWOOpticalElement2DWithBoundaryShape

from syned.beamline.optical_elements.absorbers.slit import Slit

from wofryimpl.beamline.optical_elements.absorbers.slit import WOSlit

class OWWOSlit(OWWOOpticalElement2DWithBoundaryShape):

    name = "Slit"
    description = "Wofry: Slit"
    icon = "icons/slit.png"
    priority = 41

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(1e-3)
    height = Setting(1e-4)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOSlit(name=self.oe_name,boundary_shape=self.get_boundary_shape())

    def get_optical_element_python_code(self):
        txt = self.get_boundary_shape_python_code()
        txt += "\n"
        txt += "from wofry.beamline.optical_elements.absorbers.slit import WOSlit"
        txt += "\n"
        txt += "optical_element = WOSlit(boundary_shape=boundary_shape)"
        txt += "\n"
        return txt


    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Slit):
            raise Exception("Syned Data not correct: Optical Element is not a Slit")


add_widget_parameters_to_module(__name__)
