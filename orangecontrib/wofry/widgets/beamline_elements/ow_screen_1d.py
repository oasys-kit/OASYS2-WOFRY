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

if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    def get_example_wofry_data():
        from wofryimpl.propagator.light_source import WOLightSource
        from wofryimpl.beamline.beamline import WOBeamline
        from orangecontrib.wofry.util.wofry_objects import WofryData

        light_source = WOLightSource(dimension=1,
                                     initialize_from=0,
                                     range_from_h=-0.001,
                                     range_to_h=0.001,
                                     number_of_points_h=500,
                                     energy=10000.0,
                                     )

        return WofryData(wavefront=light_source.get_wavefront(),
                           beamline=WOBeamline(light_source=light_source))

    a = QApplication(sys.argv)
    ow = OWWOScreen1D()
    ow.set_input(get_example_wofry_data())

    ow.show()
    a.exec_()
    ow.saveSettings()
