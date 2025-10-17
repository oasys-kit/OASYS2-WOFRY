from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1D
from syned.beamline.optical_elements.ideal_elements.screen import Screen


from wofryimpl.beamline.optical_elements.ideal_elements.screen import WOScreen1D

class OWWOScreen1D(OWWOOpticalElement1D):

    name = "Screen 1D"
    description = "Wofry: Screen 1D"
    icon = "icons/screen1d.png"
    priority = 20


    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOScreen1D(name=self.oe_name)

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Screen):
            raise Exception("Syned Data not correct: Optical Element is not a Screen")

add_widget_parameters_to_module(__name__)