import numpy
from orangewidget.settings import Setting
from oasys2.widget import gui as oasysgui
from oasys2.widget.util import congruence
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from syned.beamline.optical_elements.ideal_elements.ideal_lens import IdealLens

from wofryimpl.beamline.optical_elements.ideal_elements.ideal_lens import WOIdealLens1D

from orangecontrib.wofry.widgets.gui.ow_optical_element_1d import OWWOOpticalElement1D

class OWWOIdealLens1D(OWWOOpticalElement1D):

    name = "Ideal Lens 1D"
    description = "Wofry: Ideal Lens 1D"
    icon = "icons/ideal_lens1d.png"
    priority = 23

    focal_x = Setting(1.0)

    def __init__(self):
        super().__init__()

    def draw_specific_box(self):

        self.filter_box = oasysgui.widgetBox(self.tab_bas, "Ideal Lens Setting", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.filter_box, self, "focal_x", "Horizontal Focal Length [m]", tooltip="focal_x", labelWidth=260, valueType=float, orientation="horizontal")


    def get_optical_element(self):
        return WOIdealLens1D(name=self.oe_name, focal_length=self.focal_x)


    def check_data(self):
        super().check_data()

        congruence.checkStrictlyPositiveNumber(numpy.abs(self.focal_x), "Horizontal Focal Length")

    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            if isinstance(optical_element, IdealLens):
                self.focal_x = optical_element._focal_x
            else:
                raise Exception("Syned Data not correct: Optical Element is not a Slit")
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")

add_widget_parameters_to_module(__name__)