from PyQt5 import QtWidgets
from PyQt5.QtGui import QPalette, QColor, QFont

from orangewidget import widget, gui
from orangewidget.settings import Setting

from oasys.widgets import gui as oasysgui
from oasys.widgets.widget import OWWidget

from orangecontrib.wofry.util.wofry_objects import WofryData

class OWWOMerge(OWWidget):

    name = "Merge Wofry Data"
    description = "Display Data: Merge Wofry Data"
    icon = "icons/merge.png"
    maintainer = "M Sanchez del Rio"
    maintainer_email = "srio(@at@)esrf.eu"
    priority = 400
    category = "Wofry Tools"
    keywords = ["WodryData", "Add wavefronts"]

    inputs = [("Input WofryData # 1" , WofryData, "setWavefront1" ),
              ("Input WofryData # 2" , WofryData, "setWavefront2" ),
              ("Input WofryData # 3" , WofryData, "setWavefront3" ),
              ("Input WofryData # 4" , WofryData, "setWavefront4" ),
              ("Input WofryData # 5" , WofryData, "setWavefront5" ),
              ("Input WofryData # 6" , WofryData, "setWavefront6" ),
              ("Input WofryData # 7" , WofryData, "setWavefront7" ),
              ("Input WofryData # 8" , WofryData, "setWavefront8" ),
              ("Input WofryData # 9" , WofryData, "setWavefront9" ),
              ("Input WofryData # 10", WofryData, "setWavefront10"),]

    outputs = [{"name":"WofryData",
                "type":WofryData,
                "doc":"WofryData",
                "id":"WofryData"}]

    want_main_area=0
    want_control_area = 1

    input_wavefront1=None
    input_wavefront2=None
    input_wavefront3=None
    input_wavefront4=None
    input_wavefront5=None
    input_wavefront6=None
    input_wavefront7=None
    input_wavefront8=None
    input_wavefront9=None
    input_wavefront10=None

    use_weights = Setting(0)

    weight_input_wavefront1=Setting(1.0)
    weight_input_wavefront2=Setting(1.0)
    weight_input_wavefront3=Setting(1.0)
    weight_input_wavefront4=Setting(1.0)
    weight_input_wavefront5=Setting(1.0)
    weight_input_wavefront6=Setting(1.0)
    weight_input_wavefront7=Setting(1.0)
    weight_input_wavefront8=Setting(1.0)
    weight_input_wavefront9=Setting(1.0)
    weight_input_wavefront10=Setting(1.0)

    phase_input_wavefront1=Setting(0.0)
    phase_input_wavefront2=Setting(0.0)
    phase_input_wavefront3=Setting(0.0)
    phase_input_wavefront4=Setting(0.0)
    phase_input_wavefront5=Setting(0.0)
    phase_input_wavefront6=Setting(0.0)
    phase_input_wavefront7=Setting(0.0)
    phase_input_wavefront8=Setting(0.0)
    phase_input_wavefront9=Setting(0.0)
    phase_input_wavefront10=Setting(0.0)

    def __init__(self, show_automatic_box=True):
        super().__init__()

        self.runaction = widget.OWAction("Merge Wavefronts", self)
        self.runaction.triggered.connect(self.merge_wavefronts)
        self.addAction(self.runaction)

        self.setFixedWidth(470)
        self.setFixedHeight(470)

        gen_box = gui.widgetBox(self.controlArea, "Merge Wofry Data", addSpace=True, orientation="vertical")

        button_box = oasysgui.widgetBox(gen_box, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Merge Wavefronts and Send", callback=self.merge_wavefronts)
        font = QFont(button.font())
        font.setBold(True)
        button.setFont(font)
        palette = QPalette(button.palette()) # make a copy of the palette
        palette.setColor(QPalette.ButtonText, QColor('Dark Blue'))
        button.setPalette(palette) # assign new palette
        button.setFixedHeight(45)

        weight_box = oasysgui.widgetBox(gen_box, "Relative Weights and Phases", addSpace=False, orientation="vertical")

        gui.comboBox(weight_box, self, "use_weights", label="Use Relative Weights and Phases?", labelWidth=350,
                     items=["No", "Yes"],
                     callback=self.set_UseWeights, sendSelectedValue=False, orientation="horizontal")

        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront1 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront1", "Input Wavefront 1 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront1 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront1", "Input Wavefront 1 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront2 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront2", "Input Wavefront 2 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront2 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront2", "Input Wavefront 2 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront3 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront3", "Input Wavefront 3 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront3 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront3", "Input Wavefront 3 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront4 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront4", "Input Wavefront 4 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront4 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront4", "Input Wavefront 4 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront5 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront5", "Input Wavefront 5 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront5 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront5", "Input Wavefront 5 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront6 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront6", "Input Wavefront 6 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront6 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront6", "Input Wavefront 6 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront7 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront7", "Input Wavefront 7 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront7 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront7", "Input Wavefront 7 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront8 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront8", "Input Wavefront 8 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront8 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront8", "Input Wavefront 8 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront9 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront9", "Input Wavefront 9 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront9 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront9", "Input Wavefront 9 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront10 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront10", "Input Wavefront 10 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront10 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront10", "Input Wavefront 10 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront1.setEnabled(False)
        self.le_weight_input_wavefront2.setEnabled(False)
        self.le_weight_input_wavefront3.setEnabled(False)
        self.le_weight_input_wavefront4.setEnabled(False)
        self.le_weight_input_wavefront5.setEnabled(False)
        self.le_weight_input_wavefront6.setEnabled(False)
        self.le_weight_input_wavefront7.setEnabled(False)
        self.le_weight_input_wavefront8.setEnabled(False)
        self.le_weight_input_wavefront9.setEnabled(False)
        self.le_weight_input_wavefront10.setEnabled(False)

        self.le_phase_input_wavefront1.setEnabled(False)
        self.le_phase_input_wavefront2.setEnabled(False)
        self.le_phase_input_wavefront3.setEnabled(False)
        self.le_phase_input_wavefront4.setEnabled(False)
        self.le_phase_input_wavefront5.setEnabled(False)
        self.le_phase_input_wavefront6.setEnabled(False)
        self.le_phase_input_wavefront7.setEnabled(False)
        self.le_phase_input_wavefront8.setEnabled(False)
        self.le_phase_input_wavefront9.setEnabled(False)
        self.le_phase_input_wavefront10.setEnabled(False)


    def setWavefront1(self, wavefront):
        self.le_weight_input_wavefront1.setEnabled(False)
        self.le_phase_input_wavefront1.setEnabled(False)
        self.input_wavefront1 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #1 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront1 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront1.setEnabled(True)
            self.le_phase_input_wavefront1.setEnabled(True)



    def setWavefront2(self, wavefront):
        self.le_weight_input_wavefront2.setEnabled(False)
        self.le_phase_input_wavefront2.setEnabled(False)
        self.input_wavefront2 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #2 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront2 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront2.setEnabled(True)
            self.le_phase_input_wavefront2.setEnabled(True)

    def setWavefront3(self, wavefront):
        self.le_weight_input_wavefront3.setEnabled(False)
        self.le_phase_input_wavefront3.setEnabled(False)
        self.input_wavefront3 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #3 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront3 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront3.setEnabled(True)
            self.le_phase_input_wavefront3.setEnabled(True)

    def setWavefront4(self, wavefront):
        self.le_weight_input_wavefront4.setEnabled(False)
        self.le_phase_input_wavefront4.setEnabled(False)
        self.input_wavefront4 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #4 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront4 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront4.setEnabled(True)
            self.le_phase_input_wavefront4.setEnabled(True)

    def setWavefront5(self, wavefront):
        self.le_weight_input_wavefront5.setEnabled(False)
        self.le_phase_input_wavefront5.setEnabled(False)
        self.input_wavefront5 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #5 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront5 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront5.setEnabled(True)
            self.le_phase_input_wavefront5.setEnabled(True)

    def setWavefront6(self, wavefront):
        self.le_weight_input_wavefront6.setEnabled(False)
        self.le_phase_input_wavefront6.setEnabled(False)
        self.input_wavefront6 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #6 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront6 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront6.setEnabled(True)
            self.le_phase_input_wavefront6.setEnabled(True)

    def setWavefront7(self, wavefront):
        self.le_weight_input_wavefront7.setEnabled(False)
        self.le_phase_input_wavefront7.setEnabled(False)
        self.input_wavefront7 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #7 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront7 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront7.setEnabled(True)
            self.le_phase_input_wavefront7.setEnabled(True)

    def setWavefront8(self, wavefront):
        self.le_weight_input_wavefront8.setEnabled(False)
        self.le_phase_input_wavefront8.setEnabled(False)
        self.input_wavefront8 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #8 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront8 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront8.setEnabled(True)
            self.le_phase_input_wavefront8.setEnabled(True)

    def setWavefront9(self, wavefront):
        self.le_weight_input_wavefront9.setEnabled(False)
        self.le_phase_input_wavefront9.setEnabled(False)
        self.input_wavefront9 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #9 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront9 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront9.setEnabled(True)
            self.le_phase_input_wavefront9.setEnabled(True)

    def setWavefront10(self, wavefront):
        self.le_weight_input_wavefront10.setEnabled(False)
        self.le_phase_input_wavefront10.setEnabled(False)
        self.input_wavefront10 = None

        try:
            shape = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QtWidgets.QMessageBox.critical(self, "Error",
                                           "Data #10 not displayable",
                                           QtWidgets.QMessageBox.Ok)
            return

        self.input_wavefront10 = wavefront
        if self.use_weights:
            self.le_weight_input_wavefront10.setEnabled(True)
            self.le_phase_input_wavefront10.setEnabled(True)

    def merge_wavefronts(self):
        merged_wavefront = None

        if self.use_weights == 1:
            total_intensity = 1.0
            for index in range(1, 11):
                current_wavefront = getattr(self, "input_wavefront" + str(index))
                if not current_wavefront is None:
                    total_intensity += 0

        cumulated_complex_amplitude = None
        for index in range(1, 11):
            current_wavefront = getattr(self, "input_wavefront" + str(index))
            if not current_wavefront is None:
                current_wavefront = current_wavefront.duplicate()
                if self.use_weights == 1:
                    new_weight = getattr(self, "weight_input_wavefront" + str(index))
                    current_wavefront.get_wavefront().rescale_amplitude(new_weight)

                    new_phase = getattr(self, "phase_input_wavefront" + str(index))
                    current_wavefront.get_wavefront().add_phase_shift(new_phase)

                if cumulated_complex_amplitude is None:
                    merged_wavefront = current_wavefront.duplicate()
                    energy = merged_wavefront.get_wavefront().get_photon_energy()
                    cumulated_complex_amplitude = current_wavefront.get_wavefront().get_complex_amplitude().copy()
                    shape = cumulated_complex_amplitude.shape
                else:
                    ca = current_wavefront.get_wavefront().get_complex_amplitude().copy()
                    if current_wavefront.get_wavefront().get_photon_energy() != energy:
                        QtWidgets.QMessageBox.critical(self, "Error",
                                                       "Energies must match %f != %f" % (energy, current_wavefront.get_wavefront().get_photon_energy()),
                                                       QtWidgets.QMessageBox.Ok)
                        return
                    if ca.shape != shape:
                        QtWidgets.QMessageBox.critical(self, "Error",
                                                       "Wavefronts must have the same dimension and size",
                                                       QtWidgets.QMessageBox.Ok)
                        return
                    cumulated_complex_amplitude += ca

        wf = merged_wavefront.get_wavefront()
        wf.set_complex_amplitude(cumulated_complex_amplitude)

        self.send("WofryData", merged_wavefront)


    def set_UseWeights(self):
        self.le_weight_input_wavefront1.setEnabled(self.use_weights == 1 and not  self.input_wavefront1 is None)
        self.le_weight_input_wavefront2.setEnabled(self.use_weights == 1 and not  self.input_wavefront2 is None)
        self.le_weight_input_wavefront3.setEnabled(self.use_weights == 1 and not  self.input_wavefront3 is None)
        self.le_weight_input_wavefront4.setEnabled(self.use_weights == 1 and not  self.input_wavefront4 is None)
        self.le_weight_input_wavefront5.setEnabled(self.use_weights == 1 and not  self.input_wavefront5 is None)
        self.le_weight_input_wavefront6.setEnabled(self.use_weights == 1 and not  self.input_wavefront6 is None)
        self.le_weight_input_wavefront7.setEnabled(self.use_weights == 1 and not  self.input_wavefront7 is None)
        self.le_weight_input_wavefront8.setEnabled(self.use_weights == 1 and not  self.input_wavefront8 is None)
        self.le_weight_input_wavefront9.setEnabled(self.use_weights == 1 and not  self.input_wavefront9 is None)
        self.le_weight_input_wavefront10.setEnabled(self.use_weights == 1 and not  self.input_wavefront10 is None)

        self.le_phase_input_wavefront1.setEnabled(self.use_weights == 1 and not  self.input_wavefront1 is None)
        self.le_phase_input_wavefront2.setEnabled(self.use_weights == 1 and not  self.input_wavefront2 is None)
        self.le_phase_input_wavefront3.setEnabled(self.use_weights == 1 and not  self.input_wavefront3 is None)
        self.le_phase_input_wavefront4.setEnabled(self.use_weights == 1 and not  self.input_wavefront4 is None)
        self.le_phase_input_wavefront5.setEnabled(self.use_weights == 1 and not  self.input_wavefront5 is None)
        self.le_phase_input_wavefront6.setEnabled(self.use_weights == 1 and not  self.input_wavefront6 is None)
        self.le_phase_input_wavefront7.setEnabled(self.use_weights == 1 and not  self.input_wavefront7 is None)
        self.le_phase_input_wavefront8.setEnabled(self.use_weights == 1 and not  self.input_wavefront8 is None)
        self.le_phase_input_wavefront9.setEnabled(self.use_weights == 1 and not  self.input_wavefront9 is None)
        self.le_phase_input_wavefront10.setEnabled(self.use_weights == 1 and not  self.input_wavefront10 is None)


if __name__ == "__main__":
    import sys
    from PyQt5.QtWidgets import QApplication

    a = QApplication(sys.argv)
    ow = OWWOMerge()
    ow.show()
    a.exec_()
    ow.saveSettings()
