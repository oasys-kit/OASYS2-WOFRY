import sys

from AnyQt.QtCore import QRect
from AnyQt.QtWidgets import QApplication
from AnyQt.QtGui import QTextCursor

from orangewidget import gui
from orangewidget.widget import Input
from oasys2.widget.widget import OWWidget
from oasys2.widget import gui as oasysgui
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.python_script import PythonScript

class OWWOInfo(OWWidget):

    name = "Info"
    description = "Display Data: Info"
    icon = "icons/info.png"
    maintainer = "M Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 300
    category = "Data Display Tools"
    keywords = ["data", "file", "load", "read"]

    class Inputs:
        wofry_data  = Input("Wofry Data", WofryData, default=True, auto_summary=False)

    WIDGET_WIDTH = 950
    WIDGET_HEIGHT = 650

    want_main_area = 1
    want_control_area = 0

    input_data = None

    def __init__(self):
        super().__init__()

        geom = QApplication.primaryScreen().geometry()
        self.setGeometry(QRect(round(geom.width()*0.05),
                               round(geom.height()*0.05),
                               round(min(geom.width()*0.98, self.WIDGET_WIDTH)),
                               round(min(geom.height()*0.95, self.WIDGET_HEIGHT))))


        gen_box = gui.widgetBox(self.mainArea, "Beamline Info", addSpace=True, orientation="horizontal")

        tabs_setting = oasysgui.tabWidget(gen_box)
        tabs_setting.setFixedHeight(self.WIDGET_HEIGHT-60)
        tabs_setting.setFixedWidth(self.WIDGET_WIDTH-60)

        tab_sys = oasysgui.createTabPage(tabs_setting, "Sys Info")
        tab_dis = oasysgui.createTabPage(tabs_setting, "Distances Summary")
        tab_scr = oasysgui.createTabPage(tabs_setting, "Python Script")
        tab_out = oasysgui.createTabPage(tabs_setting, "System Output")

        self.sysInfo = oasysgui.textArea()
        self.sysInfo.setMaximumHeight(self.WIDGET_HEIGHT-100)
        sys_box = oasysgui.widgetBox(tab_sys, "", addSpace=True, orientation="horizontal", height = self.WIDGET_HEIGHT-80, width = self.WIDGET_WIDTH-80)
        sys_box.layout().addWidget(self.sysInfo)

        self.distancesSummary = oasysgui.textArea()
        self.distancesSummary.setMaximumHeight(self.WIDGET_HEIGHT-100)
        dist_box = oasysgui.widgetBox(tab_dis, "", addSpace=True, orientation="horizontal", height = self.WIDGET_HEIGHT-80, width = self.WIDGET_WIDTH-80)
        dist_box.layout().addWidget(self.distancesSummary)

        self.pythonScript = oasysgui.textArea(readOnly=False)
        self.pythonScript.setMaximumHeight(self.WIDGET_HEIGHT - 300)
        script_box = gui.widgetBox(tab_scr, "Python script", addSpace=True, orientation="horizontal")
        self.wofry_python_script = PythonScript()
        self.wofry_python_script.code_area.setFixedHeight(300)
        script_box.layout().addWidget(self.wofry_python_script)



        self.wofry_output = oasysgui.textArea()
        out_box = oasysgui.widgetBox(tab_out, "System Output", addSpace=True, orientation="horizontal", height=self.WIDGET_HEIGHT - 80)
        out_box.layout().addWidget(self.wofry_output)

    @Inputs.wofry_data
    def set_input(self, wofry_data):
        if not wofry_data is None:
            if isinstance(wofry_data, WofryData):
                self.input_data = wofry_data
            else:
                raise Exception("Only wofry_data allowed as input")

        self.update()

    def update(self):
        if self.input_data is None:
            return

        bl = self.input_data.get_beamline()
        self.distancesSummary.setPlainText(bl.distances())
        self.wofry_python_script.set_code(bl.to_python_code())
        self.sysInfo.setPlainText(bl.info())


    def writeStdOut(self, text):
        cursor = self.shadow_output.textCursor()
        cursor.movePosition(QTextCursor.End)
        cursor.insertText(text)
        self.wofryoutput.setTextCursor(cursor)
        self.wofryoutput.ensureCursorVisible()


add_widget_parameters_to_module(__name__)