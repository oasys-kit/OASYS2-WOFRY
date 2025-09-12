__author__ = 'labx'

import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from PyQt5.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class GenericWavefrontViewer1D(WofryWidget):

    name = " Generic Wavefront Viewer 1D"
    id = "GenericWavefrontViewer1D"
    description = "Generic Wavefront Viewer 1D"
    icon = "icons/wv1d.png"
    priority = 1

    category = "Wofry Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("WofryData", WofryData, "set_input")]

    wofry_data = None
    accumulated_data = None
    keep_result = Setting(0)
    phase_unwrap = Setting(0)
    titles = ["Wavefront 1D Intensity", "Wavefront 1D Phase","Wavefront Real(Amplitude)","Wavefront Imag(Amplitude)"]

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=False, show_script_tab=False)

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Refresh", callback=self.refresh)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)



        gui.separator(self.controlArea)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT + 50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Wavefront Viewer Settings")

        incremental_box = oasysgui.widgetBox(self.tab_sou, "Incremental Result", addSpace=True, orientation="horizontal", height=80)

        gui.comboBox(incremental_box, self, "keep_result",
                    label="Keep results", addSpace=False,
                    items=['No','Accumulate intensity','Accumulate electric field'],
                    valueType=int, orientation="horizontal", callback=self.refresh)
        # gui.checkBox(incremental_box, self, "keep_result", "Keep Result")
        gui.button(incremental_box, self, "Clear", callback=self.reset_accumumation)

        amplitude_and_phase_box = oasysgui.widgetBox(self.tab_sou, "Amplitude and phase settings",
                                                     addSpace=True, orientation="horizontal", height=80)

        gui.comboBox(amplitude_and_phase_box, self, "phase_unwrap",
                    label="Phase unwrap ", addSpace=False,
                    items=['No','Yes'],
                    valueType=int, orientation="horizontal", callback=self.refresh)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        self.tab = []
        self.plot_canvas = []

        # for index in range(0, len(self.titles)):
        # intensity
        self.tab.append(gui.createTabPage(self.tabs, self.titles[0]))
        self.plot_canvas.append(None)
        # phase
        if self.keep_result != 1:
            self.tab.append(gui.createTabPage(self.tabs, self.titles[1]))
            self.plot_canvas.append(None)
            # real
            self.tab.append(gui.createTabPage(self.tabs, self.titles[2]))
            self.plot_canvas.append(None)
            # imag
            self.tab.append(gui.createTabPage(self.tabs, self.titles[3]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def set_input(self, wofry_data):
        if not wofry_data is None:
            self.wofry_data = wofry_data

            if self.keep_result ==0:
                self.accumulated_data = None

            if self.accumulated_data is None:
                self.accumulated_data = {}
                self.accumulated_data["counter"] = 1
                self.accumulated_data["intensity"] = self.wofry_data.get_wavefront().get_intensity()
                self.accumulated_data["complex_amplitude"] = self.wofry_data.get_wavefront().get_complex_amplitude()

                self.accumulated_data["x"] = self.wofry_data.get_wavefront().get_abscissas()

            else:
                self.accumulated_data["counter"] += 1
                self.accumulated_data["intensity"] += self.wofry_data.get_wavefront().get_intensity()
                self.accumulated_data["complex_amplitude"] += self.wofry_data.get_wavefront().get_complex_amplitude()


            self.refresh()

    def refresh(self):
        self.progressBarInit()

        try:
            if self.wofry_data is not None:
                current_index = self.tabs.currentIndex()
                self.initializeTabs()
                self.plot_results()
                self.tabs.setCurrentIndex(current_index)
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)


    def do_plot_results(self, progressBarValue):
        if self.accumulated_data is None:
            return
        else:

            self.progressBarSet(progressBarValue)


            if self.keep_result < 2:
                self.plot_data1D(x=1e6*self.accumulated_data["x"],
                                 y=self.accumulated_data["intensity"],
                                 progressBarValue=progressBarValue + 10,
                                 tabs_canvas_index=0,
                                 plot_canvas_index=0,
                                 title=self.titles[0],
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Intensity")
            elif self.keep_result == 2:
                self.plot_data1D(x=1e6*self.accumulated_data["x"],
                                 y=numpy.abs(self.accumulated_data["complex_amplitude"])**2,
                                 progressBarValue=progressBarValue + 10,
                                 tabs_canvas_index=0,
                                 plot_canvas_index=0,
                                 title=self.titles[0],
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Intensity")
            else:
                raise ValueError("Non recognised flag: keep_results")

            if ((self.keep_result == 0) or (self.keep_result == 2)):
                phase = numpy.angle(self.accumulated_data['complex_amplitude'])
                if self.phase_unwrap:
                    phase = numpy.unwrap(phase)
                self.plot_data1D(x=1e6*self.accumulated_data['x'],
                                 y=phase,
                                 progressBarValue=progressBarValue + 10,
                                 tabs_canvas_index=1,
                                 plot_canvas_index=1,
                                 title=self.titles[1],
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Phase (rad)")

                self.plot_data1D(x=1e6*self.accumulated_data['x'],
                                 y=numpy.real(self.accumulated_data['complex_amplitude']),
                                 progressBarValue=progressBarValue + 10,
                                 tabs_canvas_index=2,
                                 plot_canvas_index=2,
                                 title=self.titles[2],
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Real(Amplitude)")

                self.plot_data1D(x=1e6*self.accumulated_data['x'],
                                 y=numpy.imag(self.accumulated_data['complex_amplitude']),
                                 progressBarValue=progressBarValue + 10,
                                 tabs_canvas_index=3,
                                 plot_canvas_index=3,
                                 title=self.titles[3],
                                 xtitle="Spatial Coordinate [$\mu$m]",
                                 ytitle="Imag(Amplitude)")


            self.progressBarFinished()

    def reset_accumumation(self):

        self.initializeTabs()
        self.accumulated_data = None
        self.wofry_data = None

if __name__ == '__main__':

    from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
    from PyQt5.QtWidgets import QApplication

    app = QApplication([])
    ow =GenericWavefrontViewer1D()

    wf = GenericWavefront1D.initialize_wavefront_from_arrays(numpy.linspace(-1e-3,1e-3,300),
                                                             numpy.linspace(-1e-3,1e-3,300)**2 )

    ow.set_input(WofryData(wavefront=wf))
    ow.show()
    app.exec_()
    ow.saveSettings()
