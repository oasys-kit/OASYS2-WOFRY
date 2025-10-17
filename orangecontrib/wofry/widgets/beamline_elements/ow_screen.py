from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangewidget.settings import Setting

from orangecontrib.wofry.widgets.gui.ow_optical_element_2d import OWWOOpticalElement2D
from syned.beamline.optical_elements.ideal_elements.screen import Screen
from wofryimpl.beamline.optical_elements.ideal_elements.screen import WOScreen

class OWWOScreen(OWWOOpticalElement2D):
    name = "Screen"
    description = "Wofry: Slit"
    icon = "icons/screen.png"
    priority = 40

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0)
    height = Setting(0.0)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOScreen(name=self.oe_name)

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, Screen):
            raise Exception("Syned Data not correct: Optical Element is not a Screen")

    def receive_specific_syned_data(self, optical_element):
        pass

add_widget_parameters_to_module(__name__)