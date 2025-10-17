from orangewidget.settings import Setting
from oasys2.widget import gui as oasysgui
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1DWithBoundaryShape
from syned.beamline.optical_elements.absorbers.beam_stopper import BeamStopper

from wofryimpl.beamline.optical_elements.absorbers.beam_stopper import WOBeamStopper1D

class OWWOStop1D(OWWOOpticalElement1DWithBoundaryShape):

    name = "BeamStopper 1D"
    description = "Wofry: BeamStopper 1D"
    icon = "icons/stop1d.png"
    priority = 22

    vertical_shift = Setting(0.0)

    height = Setting(0.0001)

    def __init__(self):
        super().__init__()

    def get_optical_element(self):
        return WOBeamStopper1D(name=self.oe_name,boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, BeamStopper):
            raise Exception("Syned Data not correct: Optical Element is not a BeamStopper")


    # overwrite this method to adapt labels
    def draw_specific_box(self):
        self.shape_box = oasysgui.widgetBox(self.tab_bas, "Boundary Shape", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.shape_box, self, "vertical_shift", "Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.rectangle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.rectangle_box, self, "height", "Obstruction [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.circle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        self.set_Shape()

    def get_optical_element(self):
        return WOBeamStopper1D(boundary_shape=self.get_boundary_shape())

    def check_syned_instance(self, optical_element):
        if not isinstance(optical_element, BeamStopper):
            raise Exception("Syned Data not correct: Optical Element is not a BeamStopper")

add_widget_parameters_to_module(__name__)