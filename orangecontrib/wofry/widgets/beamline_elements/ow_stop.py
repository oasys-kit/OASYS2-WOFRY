from orangewidget.settings import Setting
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangecontrib.wofry.widgets.gui.ow_optical_element_2d import OWWOOpticalElement2DWithBoundaryShape

from syned.beamline.optical_elements.absorbers.beam_stopper import BeamStopper

from wofryimpl.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper

class OWWOStop(OWWOOpticalElement2DWithBoundaryShape):

    name = "BeamStopper"
    description = "Wofry: BeamStopper"
    icon = "icons/stop.png"
    priority = 42

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0002)
    height = Setting(0.0001)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOBeamStopper(name=self.oe_name,boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, BeamStopper):
            raise Exception("Syned Data not correct: Optical Element is not a BeamStopper")


add_widget_parameters_to_module(__name__)