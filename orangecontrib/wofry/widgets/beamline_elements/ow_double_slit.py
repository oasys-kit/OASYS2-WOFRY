from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElementWithDoubleBoundaryShape

from syned.beamline.optical_elements.absorbers.slit import Slit

from wofryimpl.beamline.optical_elements.absorbers.slit import WOSlit

class OWWODoubleSlit(OWWOOpticalElementWithDoubleBoundaryShape):

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

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication
    def get_example_wofry_data():
        from wofryimpl.propagator.light_source import WOLightSource
        from wofryimpl.beamline.beamline import WOBeamline
        from orangecontrib.wofry.util.wofry_objects import WofryData

        light_source = WOLightSource(dimension=2,
                                     initialize_from=0,
                                     range_from_h=-0.0003,
                                     range_to_h=0.0003,
                                     range_from_v=-0.0001,
                                     range_to_v=0.0001,
                                     number_of_points_h=1000,
                                     number_of_points_v=500,
                                     energy=10000.0,
                                     )

        return WofryData(wavefront=light_source.get_wavefront(),
                           beamline=WOBeamline(light_source=light_source))

    a = QApplication(sys.argv)
    ow = OWWODoubleSlit()
    ow.set_input(get_example_wofry_data())

    ow.horizontal_shift = -50e-6
    ow.vertical_shift = -25e-6

    ow.width = 5e-6
    ow.height = 5e-6

    ow.radius = 5e-6

    ow.min_ax = 5e-6
    ow.maj_ax = 5e-6

    # the same for patch 2
    ow.horizontal_shift2 = 50e-6
    ow.vertical_shift2 = 25e-6

    ow.width2 = 5e-6
    ow.height2 = 5e-6

    ow.radius2 = 5e-6

    ow.min_ax2 = 5e-6
    ow.maj_ax2 = 5e-6

    ow.show()
    a.exec_()
    ow.saveSettings()
