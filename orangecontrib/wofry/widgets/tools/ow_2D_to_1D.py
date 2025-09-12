__author__ = 'labx'

from PyQt5.QtGui import QPalette, QColor, QFont
from orangewidget import gui
from orangewidget import widget
from orangewidget.settings import Setting
from oasys.widgets import gui as oasysgui

from wofry.propagator.wavefront1D.generic_wavefront import GenericWavefront1D
from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from orangecontrib.wofry.util.wofry_objects import WofryData

from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

class OW2Dto1D(WofryWidget):

    name = "Wavefront 2D to 1D"
    id = "Wavefront2Dto1D"
    description = "Wavefront 2D to 1D"
    icon = "icons/2d_to_1d.png"
    priority = 4

    category = "Wofry Tools"
    keywords = ["data", "file", "load", "read"]

    inputs = [("WofryData", WofryData, "set_input"),
              ("GenericWavefront2D", GenericWavefront2D, "set_input")]

    outputs = [{"name":"WofryData",
                "type":WofryData,
                "doc":"WofryData",
                "id":"WofryData"},
               {"name": "GenericWavefront1D",
                "type": GenericWavefront1D,
                "doc": "GenericWavefront1D",
                "id": "GenericWavefront1D"}
               ]

    section_axis  = Setting(0)
    section_coordinate = Setting(0.0)

    wavefront2D = None

    def __init__(self):
        super().__init__(is_automatic=True, show_script_tab=False)

        self.runaction = widget.OWAction("Send Data", self)
        self.runaction.triggered.connect(self.send_data)
        self.addAction(self.runaction)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Send Data", callback=self.send_data)
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
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Wavefront Projection Setting")

        gui.comboBox(self.tab_sou, self, "section_axis", label="Section Axis", labelWidth=220,
                     items=["Horizontal (0)", "Vertical (1)"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.tab_sou, self, "section_coordinate", "Section at", labelWidth=260, valueType=float, orientation="horizontal")

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Wavefront 2D", "Wavefront 1D"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

    def set_input(self, wofry_data):
        if not wofry_data is None:
            if isinstance(wofry_data, WofryData):
                self.wavefront2D = wofry_data.get_wavefront()
            else:
                self.wavefront2D = wofry_data

            if self.is_automatic_execution: self.send_data()

    def send_data(self):
        if not self.wavefront2D is None:
            self.progressBarInit()

            self.wavefront1D = self.wavefront2D.get_Wavefront1D_from_profile(self.section_axis, self.section_coordinate)

            self.plot_results()

            self.progressBarFinished()

            self.send("WofryData", WofryData(wavefront=self.wavefront1D))
            self.send("GenericWavefront1D", self.wavefront1D)

    def do_plot_results(self, progressBarValue):
        if not self.wavefront2D is None and not self.wavefront1D is None:

            self.progressBarSet(progressBarValue)

            titles = ["Wavefront 2D Intensity", "Wavefront 1D Intensity"]

            self.plot_data2D(data2D=self.wavefront2D.get_intensity(),
                             dataX=1e6 * self.wavefront2D.get_coordinate_x(),
                             dataY=1e6 * self.wavefront2D.get_coordinate_y(),
                             progressBarValue=progressBarValue+25,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=titles[0],
                             xtitle="Horizontal Coordinate [$\mu$m]",
                             ytitle="Vertical Coordinate [$\mu$m]")

            self.plot_data1D(x=1e6*self.wavefront1D.get_abscissas(),
                             y=self.wavefront1D.get_intensity(),
                             progressBarValue=progressBarValue + 25,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             title=titles[1],
                             xtitle="Horizontal Coordinate [$\mu$m]" if self.section_axis == 0 else "Vertical Coordinate [$\mu$m]",
                             ytitle="Intensity")



