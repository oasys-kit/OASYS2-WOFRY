__author__ = 'srio'

import numpy

from PyQt5.QtGui import QPalette, QColor, QFont
from orangewidget import gui
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class GenericWavefrontViewer2D(WofryWidget):

    name = "Wavefront Viewer 2D"
    id = "WavefrontViewer2D"
    description = "Wavefront Viewer 2D"
    icon = "icons/wv2d.png"
    priority = 2

    category = ""
    keywords = ["data", "file", "load", "read"]

    inputs = [("WofryData", WofryData, "set_input")]

    wavefront2D = None
    accumulated_data = None
    keep_result = Setting(0)
    plot_intensity = Setting(1)
    plot_phase = Setting(0)
    plot_csd = Setting(0)
    plot_iterations = Setting(0)
    phase_unwrap = Setting(0)


    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=True, show_script_tab=False)

        self.accumulated_data = None

        gui.separator(self.controlArea)

        #
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
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT+50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Wavefront Viewer Settings")

        incremental_box = oasysgui.widgetBox(self.tab_sou, "Incremental Result", addSpace=True, orientation="horizontal", height=80)
        gui.checkBox(incremental_box, self, "keep_result", "accumulate")
        gui.button(incremental_box, self, "Clear", callback=self.reset_accumumation)

        incremental_box = oasysgui.widgetBox(self.tab_sou, "Show plots", addSpace=True, orientation="vertical", height=180)
        gui.checkBox(incremental_box, self, "plot_intensity", "Plot Intensity")
        gui.checkBox(incremental_box, self, "plot_phase", "Plot Phase")
        gui.checkBox(incremental_box, self, "plot_csd", "Plot Cross spectral density")
        gui.checkBox(incremental_box, self, "plot_iterations", "Plot Iteration intensities")

        gui.comboBox(self.tab_sou, self, "phase_unwrap",
                    label="Phase unwrap ", addSpace=False,
                    items=['No','H only','V only','First H, then V','First V then H'],
                    valueType=int, orientation="horizontal", callback=self.refresh)


    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = []
        if self.plot_intensity:
            titles.append("Intensity")
        if self.plot_phase:
            titles.append("Phase")
        if self.plot_csd:
            titles.append("W(x1,0,x2,0)")
            titles.append("W(0,y1,0,y2)")
        if self.plot_iterations:
            titles.append("Iterations")

        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def crossSpectralDensityHV(self):

        WF = self.wavefront2D.get_complex_amplitude()
        imodeX = WF[:,int(0.5*WF.shape[1])]
        imodeY = WF[int(0.5*WF.shape[0]),:]

        Wx1x2 =  numpy.outer( numpy.conj(imodeX) , imodeX ) #* self.eigenvalue(i)
        Wy1y2 =  numpy.outer( numpy.conj(imodeY) , imodeY ) #* self.eigenvalue(i)


        return Wx1x2,Wy1y2

    def set_input(self, wofry_data):

        if not wofry_data is None:
            if not self.keep_result:
                self.reset_accumumation()

            self.wavefront2D = wofry_data.get_wavefront()

            Wx1x2,Wy1y2  = self.crossSpectralDensityHV()

            delta = self.wavefront2D.delta()
            if self.accumulated_data is None:
                self.accumulated_data = {}
                self.accumulated_data["counter"] = 1
                self.accumulated_data["intensity"] = self.wavefront2D.get_intensity()
                self.accumulated_data["phase"] = self.wavefront2D.get_phase()

                self.accumulated_data["W_x1_0_x2_0"] = Wx1x2
                self.accumulated_data["W_0_y1_0_y2"] = Wy1y2
                self.accumulated_data["x"] = self.wavefront2D.get_coordinate_x()
                self.accumulated_data["y"] = self.wavefront2D.get_coordinate_y()
                self.accumulated_data["iteration_intensities"] = [self.wavefront2D.get_intensity().sum()*delta[0]*delta[1]]

            else:
                self.accumulated_data["counter"] += 1
                self.accumulated_data["intensity"] += self.wavefront2D.get_intensity()
                self.accumulated_data["phase"] += self.wavefront2D.get_phase()
                self.accumulated_data["W_x1_0_x2_0"] += Wx1x2
                self.accumulated_data["W_0_y1_0_y2"] += Wy1y2
                self.accumulated_data["iteration_intensities"].append( self.wavefront2D.get_intensity().sum()*delta[0]*delta[1])

            self.progressBarInit()
            self.do_plot_results(10) #refresh()

    def refresh(self):
        current_index = self.tabs.currentIndex()
        self.initializeTabs()
        self.do_plot_results(10)  # TODO: check progressBar...
        self.tabs.setCurrentIndex(current_index)

    def do_plot_results(self, progressBarValue):


        if self.accumulated_data is None:
            return
        else:

            self.progressBarInit()
            self.progressBarSet(progressBarValue)

            # titles = ["Wavefront 2D Intensity","W(x1,0,x2,0)","W(0,y1,0,y2)"] #, "Wavefront 2D Phase"]

            tabs_canvas_index = -1
            if self.plot_intensity:
                tabs_canvas_index += 1
                self.plot_data2D(data2D=self.accumulated_data["intensity"],
                                 dataX=1e6*self.accumulated_data["x"],
                                 dataY=1e6*self.accumulated_data["y"],
                                 progressBarValue=progressBarValue+10,
                                 tabs_canvas_index=tabs_canvas_index,
                                 plot_canvas_index=0,
                                 title="Wavefront 2D Intensity",
                                 xtitle="Horizontal [$\mu$m] ( %d pixels)"%(self.accumulated_data["x"].size),
                                 ytitle="Vertical [$\mu$m] (%d pixels)"%(self.accumulated_data["y"].size))

                x,y,txt = self.get_data_iterations()
                if not(self.keep_result):
                    self.wofry_output.setText("")
                self.writeStdOut(txt)


            if self.plot_phase:
                tabs_canvas_index += 1
                phase =self.accumulated_data["phase"] / self.accumulated_data["counter"]

                if self.phase_unwrap > 0:
                    if self.phase_unwrap == 1: # x only
                        phase = numpy.unwrap(phase,axis=0)
                    elif self.phase_unwrap == 2: # y only
                        phase = numpy.unwrap(phase,axis=1)
                    elif self.phase_unwrap == 3: # x and y
                        phase = numpy.unwrap(numpy.unwrap(phase,axis=0),axis=1)
                    elif self.phase_unwrap == 4: # y and x
                        phase = numpy.unwrap(numpy.unwrap(phase,axis=1),axis=0)

                phase *=  180.0 / numpy.pi
                intensity_normalized = self.accumulated_data["intensity"] / self.accumulated_data["intensity"].max()
                phase[numpy.where(intensity_normalized<0.1)] = 0
                self.plot_data2D(data2D=phase,
                                 dataX=1e6*self.accumulated_data["x"],
                                 dataY=1e6*self.accumulated_data["y"],
                                 progressBarValue=progressBarValue+10,
                                 tabs_canvas_index=tabs_canvas_index,
                                 plot_canvas_index=0,
                                 title="Wavefront 2D Averaged Phase [degrees]",
                                 xtitle="Horizontal Coordinate [$\mu$m]",
                                 ytitle="Vertical Coordinate [$\mu$m]")
            if self.plot_csd:
                tabs_canvas_index += 1
                self.plot_data2D(data2D=numpy.abs(self.accumulated_data["W_x1_0_x2_0"]),
                                 dataX=1e6*self.accumulated_data["x"],
                                 dataY=1e6*self.accumulated_data["y"],
                                 progressBarValue=progressBarValue+10,
                                 tabs_canvas_index=tabs_canvas_index,
                                 plot_canvas_index=0,
                                 title="Cross spectral density (horizontal, at y=0)",
                                 xtitle="Horizontal Coordinate x1 [$\mu$m]",
                                 ytitle="Horizontal Coordinate x2 [$\mu$m]")
                tabs_canvas_index += 1
                self.plot_data2D(data2D=numpy.abs(self.accumulated_data["W_0_y1_0_y2"]),
                                 dataX=1e6*self.accumulated_data["x"],
                                 dataY=1e6*self.accumulated_data["y"],
                                 progressBarValue=progressBarValue+10,
                                 tabs_canvas_index=tabs_canvas_index,
                                 plot_canvas_index=0,
                                 title="Cross spectral density (vertical, at x=0)",
                                 xtitle="Vertical Coordinate y1 [$\mu$m]",
                                 ytitle="Vertical Coordinate y2 [$\mu$m]")
            if self.plot_iterations:
                tabs_canvas_index += 1
                x,y,txt = self.get_data_iterations()
                self.plot_data1D(x,y,
                                 progressBarValue=progressBarValue+10,
                                 tabs_canvas_index=tabs_canvas_index,
                                 plot_canvas_index=0,
                                 title="Intensity of beam",
                                 xtitle="iteration index",
                                 ytitle="intensity [arbitrary units]",
                                 calculate_fwhm=False,
                                 xrange=[-1,1+self.accumulated_data["counter"]],
                                 symbol='o')


                self.writeStdOut(txt)


            self.progressBarFinished()

    def get_data_iterations(self):


        x = numpy.arange(self.accumulated_data["counter"])
        y = numpy.array(self.accumulated_data["iteration_intensities"])

        txt = "#########################################################\n"
        txt += "%20s %20s %20s %20s\n"%("iteration","intensity","intensity/I0","intensity/TotalInt")
        for i,xi in enumerate(x):
            txt += "%20d  %20.5g  %20.5f %20.5f \n"%(xi,y[i],y[i]/y[0],y[i]/y.sum())

        txt += "  Total intensity: %g\n"%(y.sum())
        txt += "  Mean intensity: %g\n"%(y.mean())
        txt += "  Standard deviation intensity: %g\n"%(y.std())


        txt += "\n"

        return x,y,txt

    def reset_accumumation(self):

        self.initializeTabs()
        self.accumulated_data = None
        self.wavefront2D = None

        self.wofry_output.setText("")

if __name__ == '__main__':

    from PyQt5.QtWidgets import QApplication


    app = QApplication([])
    ow = GenericWavefrontViewer2D()


    # from orangecontrib.comsyl.util.CompactAFReader import CompactAFReader
    # filename_np = "/users/srio/COMSYLD/comsyl/comsyl/calculations/septest_cm_new_u18_2m_1h_s2.5.npz"
    # af = CompactAFReader.initialize_from_file(filename_np)
    # wf = GenericWavefront2D.initialize_wavefront_from_arrays(af.x_coordinates(),
    #                                                          af.y_coordinates(),
    #                                                          af.mode(0))
    # wf.set_photon_energy(af.photon_energy())

    from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
    from orangecontrib.wofry.util.wofry_objects import WofryData
    wf = GenericWavefront2D.initialize_wavefront_from_range(-1e-3,1e-3,-1e-3,1e-3,(200,200))
    wf.set_gaussian(1e-4,1e-4)


    ow.set_input(WofryData(wavefront=wf))
    ow.show()
    app.exec_()
    ow.saveSettings()
