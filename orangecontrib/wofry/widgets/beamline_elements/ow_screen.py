from orangewidget.settings import Setting

from orangecontrib.wofry.widgets.gui.ow_optical_element import OWWOOpticalElement

from syned.beamline.optical_elements.ideal_elements.screen import Screen

from wofryimpl.beamline.optical_elements.ideal_elements.screen import WOScreen

class OWWOScreen(OWWOOpticalElement):

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
    ow = OWWOScreen()
    ow.set_input(get_example_wofry_data())

    ow.show()
    a.exec_()
    ow.saveSettings()
