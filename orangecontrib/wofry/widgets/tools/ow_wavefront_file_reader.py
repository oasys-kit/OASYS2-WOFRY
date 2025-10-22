import os
from AnyQt.QtWidgets import QMessageBox

try:
    from silx.gui.dialog.DataFileDialog import DataFileDialog
except:
    print("Fail to import silx.gui.dialog.DataFileDialog: need silx >= 0.7")

from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.widget import  Output

from oasys2.widget.widget import OWAction, OWWidget
from oasys2.widget import gui as oasysgui
from oasys2.widget.util import congruence
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from wofryimpl.propagator.light_source_h5file import WOH5FileLightSource
from wofryimpl.beamline.beamline import WOBeamline

from orangecontrib.wofry.util.wofry_objects import WofryData

class OWWavefrontFileReader(OWWidget):
    name = "Generic Wavefront File Reader"
    description = "Utility: Wofry Wavefront File Reader"
    icon = "icons/file_reader.png"
    maintainer = "Manuel Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 5
    category = "Utility"
    keywords = ["data", "file", "load", "read"]

    want_main_area = 0

    file_name = Setting("")
    data_path = Setting("")

    class Outputs:
        wofry_data_1D = Output("Wofry Data 1D", WofryData, id="WofryData1D", default=True, auto_summary=False)
        wofry_data_2D = Output("Wofry Data 2D", WofryData, id="WofryData2D", default=True, auto_summary=False)

    def __init__(self):
        super().__init__()

        self.runaction = OWAction("Send Data", self)
        self.runaction.triggered.connect(self.send_data)
        self.addAction(self.runaction)

        self.setFixedWidth(590)
        self.setFixedHeight(250)

        left_box_1 = oasysgui.widgetBox(self.controlArea, "HDF5 Local File Selection", addSpace=True,
                                        orientation="vertical",width=570, height=100)

        figure_box = oasysgui.widgetBox(left_box_1, "", addSpace=True, orientation="vertical", width=550, height=50)

        self.le_file_name = oasysgui.lineEdit(figure_box, self, "file_name", "File Name",
                                                    labelWidth=190, valueType=str, orientation="horizontal")
        self.le_file_name.setFixedWidth(360)

        self.le_data_path = oasysgui.lineEdit(figure_box, self, "data_path", "Group (wavefront name)",
                                                    labelWidth=190, valueType=str, orientation="horizontal")
        self.le_data_path.setFixedWidth(360)

        gui.separator(left_box_1, height=20)

        button = gui.button(self.controlArea, self, "Browse File and Send Data", callback=self.read_file)
        button.setFixedHeight(45)
        gui.separator(self.controlArea, height=20)
        button = gui.button(self.controlArea, self, "Send Data", callback=self.send_data)
        button.setFixedHeight(45)

        gui.rubber(self.controlArea)

    def get_light_source(self):
        return WOH5FileLightSource(name = self.name, h5file = self.file_name)

    def read_file(self):

        dialog = DataFileDialog(self)
        dialog.setFilterMode(DataFileDialog.FilterMode.ExistingGroup)

        path, filename = os.path.split(self.file_name)
        print("Setting path: ",path)
        dialog.setDirectory(path)

        # Execute the dialog as modal
        result = dialog.exec_()
        if result:
            print("Selection:")
            print(dialog.selectedFile())
            print(dialog.selectedUrl())
            print(dialog.selectedDataUrl().data_path())
            self.file_name = dialog.selectedFile()
            self.data_path = dialog.selectedDataUrl().data_path()
            self.send_data()

    def send_data(self):
        try:
            congruence.checkEmptyString(self.file_name, "File Name")
            congruence.checkFile(self.file_name)

            light_source = self.get_light_source()
            wfr = light_source.get_wavefront()

            beamline = WOBeamline(light_source=light_source)


            if light_source.get_dimension() == 1:
                print(">>> sending 1D wavefront")
                self.Outputs.wofry_data_1D.send(WofryData(wavefront=wfr, beamline=beamline))
            elif light_source.get_dimension() == 2:
                print(">>> sending 2D wavefront")
                self.Outputs.wofry_data_2D.send(WofryData(wavefront=wfr, beamline=beamline))
            else:
                raise Exception("Invalid wavefront dimension")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e.args[0]), QMessageBox.Ok)

            if self.IS_DEVELOP:raise e

add_widget_parameters_to_module(__name__)

