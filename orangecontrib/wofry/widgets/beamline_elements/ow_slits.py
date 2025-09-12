from orangewidget.settings import Setting
from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElementWithBoundaryShape

from syned.beamline.optical_elements.absorbers.slit import Slit

from wofryimpl.beamline.optical_elements.absorbers.slit import WOSlit

class OWWOSlit(OWWOOpticalElementWithBoundaryShape):

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


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    def get_example_wofry_data():
        from wofryimpl.propagator.light_source import WOLightSource
        from wofryimpl.beamline.beamline import WOBeamline
        from orangecontrib.wofry.util.wofry_objects import WofryData

        light_source = WOLightSource(dimension=2,
                                     initialize_from=0,
                                     range_from_h=-0.002,
                                     range_to_h=0.002,
                                     range_from_v=-0.0001,
                                     range_to_v=0.0001,
                                     number_of_points_h=200,
                                     number_of_points_v=200,
                                     energy=10000.0,
                                     )

        return WofryData(wavefront=light_source.get_wavefront(),
                           beamline=WOBeamline(light_source=light_source))

    a = QApplication(sys.argv)
    ow = OWWOSlit()
    ow.set_input(get_example_wofry_data())

    ow.show()
    a.exec_()
    ow.saveSettings()
