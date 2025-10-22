from AnyQt.QtWidgets import QMessageBox

from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.widget import Input, Output

from oasys2.widget.widget import OWAction, OWWidget
from oasys2.widget import gui as oasysgui
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

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

    class Inputs:
        wofry_data_1  = Input("Input Wofry Data #1", WofryData, default=True, auto_summary=False)
        wofry_data_2  = Input("Input Wofry Data #2", WofryData, default=True, auto_summary=False)
        wofry_data_3  = Input("Input Wofry Data #3", WofryData, default=True, auto_summary=False)
        wofry_data_4  = Input("Input Wofry Data #4", WofryData, default=True, auto_summary=False)
        wofry_data_5  = Input("Input Wofry Data #5", WofryData, default=True, auto_summary=False)
        wofry_data_6  = Input("Input Wofry Data #6", WofryData, default=True, auto_summary=False)
        wofry_data_7  = Input("Input Wofry Data #7", WofryData, default=True, auto_summary=False)
        wofry_data_8  = Input("Input Wofry Data #8", WofryData, default=True, auto_summary=False)
        wofry_data_9  = Input("Input Wofry Data #9", WofryData, default=True, auto_summary=False)
        wofry_data_10 = Input("Input Wofry Data #10", WofryData, default=True, auto_summary=False)

    class Outputs:
        wofry_data = Output("Wofry Data", WofryData, id="WofryData", default=True, auto_summary=False)

    want_main_area = 0
    want_control_area = 1

    input_wavefront_1 = None
    input_wavefront_2 = None
    input_wavefront_3 = None
    input_wavefront_4 = None
    input_wavefront_5 = None
    input_wavefront_6 = None
    input_wavefront_7 = None
    input_wavefront_8 = None
    input_wavefront_9 = None
    input_wavefront_10 = None

    use_weights = Setting(0)

    weight_input_wavefront_1 = Setting(1.0)
    weight_input_wavefront_2 = Setting(1.0)
    weight_input_wavefront_3 = Setting(1.0)
    weight_input_wavefront_4 = Setting(1.0)
    weight_input_wavefront_5 = Setting(1.0)
    weight_input_wavefront_6 = Setting(1.0)
    weight_input_wavefront_7 = Setting(1.0)
    weight_input_wavefront_8 = Setting(1.0)
    weight_input_wavefront_9 = Setting(1.0)
    weight_input_wavefront_10 = Setting(1.0)

    phase_input_wavefront_1 = Setting(0.0)
    phase_input_wavefront_2 = Setting(0.0)
    phase_input_wavefront_3 = Setting(0.0)
    phase_input_wavefront_4 = Setting(0.0)
    phase_input_wavefront_5 = Setting(0.0)
    phase_input_wavefront_6 = Setting(0.0)
    phase_input_wavefront_7 = Setting(0.0)
    phase_input_wavefront_8 = Setting(0.0)
    phase_input_wavefront_9 = Setting(0.0)
    phase_input_wavefront_10 = Setting(0.0)

    def __init__(self):
        super().__init__()

        self.runaction = OWAction("Merge Wavefronts", self)
        self.runaction.triggered.connect(self.merge_wavefronts)
        self.addAction(self.runaction)

        self.setFixedWidth(470)
        self.setFixedHeight(870)

        gen_box = gui.widgetBox(self.controlArea, "Merge Wofry Data", addSpace=True, orientation="vertical")

        button_box = oasysgui.widgetBox(gen_box, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Merge Wavefronts and Send", callback=self.merge_wavefronts)
        button.setStyleSheet("color: darkblue; font-weight: bold; height: 45px;")

        weight_box = oasysgui.widgetBox(gen_box, "Relative Weights and Phases", addSpace=False, orientation="vertical")

        gui.comboBox(weight_box, self, "use_weights", label="Use Relative Weights and Phases?", labelWidth=350,
                     items=["No", "Yes"],
                     callback=self.set_UseWeights, sendSelectedValue=False, orientation="horizontal")

        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_1 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_1", "Input Wavefront 1 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_1 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_1", "Input Wavefront 1 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_2 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_2", "Input Wavefront 2 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_2 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_2", "Input Wavefront 2 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_3 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_3", "Input Wavefront 3 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_3 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_3", "Input Wavefront 3 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_4 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_4", "Input Wavefront 4 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_4 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_4", "Input Wavefront 4 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_5 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_5", "Input Wavefront 5 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_5 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_5", "Input Wavefront 5 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_6 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_6", "Input Wavefront 6 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_6 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_6", "Input Wavefront 6 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_7 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_7", "Input Wavefront 7 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_7 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_7", "Input Wavefront 7 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_8 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_8", "Input Wavefront 8 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_8 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_8", "Input Wavefront 8 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_9 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_9", "Input Wavefront 9 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_9 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_9", "Input Wavefront 9 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_10 = oasysgui.lineEdit(weight_box, self, "weight_input_wavefront_10", "Input Wavefront 10 weight",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        self.le_phase_input_wavefront_10 = oasysgui.lineEdit(weight_box, self, "phase_input_wavefront_10", "Input Wavefront 10 add phase [rad]",
                                                    labelWidth=300, valueType=float, orientation="horizontal")
        gui.separator(weight_box, height=10)

        self.le_weight_input_wavefront_1.setEnabled(False)
        self.le_weight_input_wavefront_2.setEnabled(False)
        self.le_weight_input_wavefront_3.setEnabled(False)
        self.le_weight_input_wavefront_4.setEnabled(False)
        self.le_weight_input_wavefront_5.setEnabled(False)
        self.le_weight_input_wavefront_6.setEnabled(False)
        self.le_weight_input_wavefront_7.setEnabled(False)
        self.le_weight_input_wavefront_8.setEnabled(False)
        self.le_weight_input_wavefront_9.setEnabled(False)
        self.le_weight_input_wavefront_10.setEnabled(False)

        self.le_phase_input_wavefront_1.setEnabled(False)
        self.le_phase_input_wavefront_2.setEnabled(False)
        self.le_phase_input_wavefront_3.setEnabled(False)
        self.le_phase_input_wavefront_4.setEnabled(False)
        self.le_phase_input_wavefront_5.setEnabled(False)
        self.le_phase_input_wavefront_6.setEnabled(False)
        self.le_phase_input_wavefront_7.setEnabled(False)
        self.le_phase_input_wavefront_8.setEnabled(False)
        self.le_phase_input_wavefront_9.setEnabled(False)
        self.le_phase_input_wavefront_10.setEnabled(False)
    
    
    def __setWavefront(self, wavefront, index):
        le_weight_input_wavefront = getattr(self, f"le_weight_input_wavefront_{index}")
        le_phase_input_wavefront  = getattr(self, f"le_phase_input_wavefront_{index}")
        
        le_weight_input_wavefront.setEnabled(False)
        le_phase_input_wavefront.setEnabled(False)
        setattr(self, f"input_wavefront_{index}", None)

        try:
            _ = wavefront.get_wavefront().get_complex_amplitude().shape
        except:
            QMessageBox.critical(self, "Error",
                                           f"Data #{index} not displayable",
                                           QMessageBox.Ok)
            return

        setattr(self, f"input_wavefront_{index}", wavefront)
        if self.use_weights:
            le_weight_input_wavefront.setEnabled(True)
            le_phase_input_wavefront.setEnabled(True)

    @Inputs.wofry_data_1
    def setWavefront_1(self, wavefront): self.__setWavefront(wavefront, 1)
    @Inputs.wofry_data_2
    def setWavefront_2(self, wavefront): self.__setWavefront(wavefront, 2)
    @Inputs.wofry_data_3
    def setWavefront_3(self, wavefront): self.__setWavefront(wavefront, 3)
    @Inputs.wofry_data_4
    def setWavefront_4(self, wavefront): self.__setWavefront(wavefront, 4)
    @Inputs.wofry_data_5
    def setWavefront_5(self, wavefront): self.__setWavefront(wavefront, 5)
    @Inputs.wofry_data_6
    def setWavefront_6(self, wavefront): self.__setWavefront(wavefront, 6)
    @Inputs.wofry_data_7
    def setWavefront_7(self, wavefront): self.__setWavefront(wavefront, 7)
    @Inputs.wofry_data_8
    def setWavefront_8(self, wavefront): self.__setWavefront(wavefront, 8)
    @Inputs.wofry_data_9
    def setWavefront_9(self, wavefront): self.__setWavefront(wavefront, 9)
    @Inputs.wofry_data_10
    def setWavefront_10(self, wavefront): self.__setWavefront(wavefront, 10)


    def merge_wavefronts(self):
        merged_wavefront = None

        cumulated_complex_amplitude = None
        for index in range(1, 11):
            current_wavefront = getattr(self, f"input_wavefront_{index}")
            if not current_wavefront is None:
                current_wavefront = current_wavefront.duplicate()
                if self.use_weights == 1:
                    new_weight = getattr(self, f"weight_input_wavefront_{index}")
                    current_wavefront.get_wavefront().rescale_amplitude(new_weight)

                    new_phase = getattr(self, f"phase_input_wavefront_{index}")
                    current_wavefront.get_wavefront().add_phase_shift(new_phase)

                if cumulated_complex_amplitude is None:
                    merged_wavefront = current_wavefront.duplicate()
                    energy = merged_wavefront.get_wavefront().get_photon_energy()
                    cumulated_complex_amplitude = current_wavefront.get_wavefront().get_complex_amplitude().copy()
                    shape = cumulated_complex_amplitude.shape
                else:
                    ca = current_wavefront.get_wavefront().get_complex_amplitude().copy()
                    if current_wavefront.get_wavefront().get_photon_energy() != energy:
                        QMessageBox.critical(self, "Error",
                                                       "Energies must match %f != %f" % (energy, current_wavefront.get_wavefront().get_photon_energy()),
                                                       QMessageBox.Ok)
                        return
                    if ca.shape != shape:
                        QMessageBox.critical(self, "Error",
                                                       "Wavefronts must have the same dimension and size",
                                                       QMessageBox.Ok)
                        return
                    cumulated_complex_amplitude += ca

        wf = merged_wavefront.get_wavefront()
        wf.set_complex_amplitude(cumulated_complex_amplitude)

        self.Outputs.wofry_data.send(merged_wavefront)


    def set_UseWeights(self):
        self.le_weight_input_wavefront_1.setEnabled(self.use_weights == 1 and not  self.input_wavefront_1 is None)
        self.le_weight_input_wavefront_2.setEnabled(self.use_weights == 1 and not  self.input_wavefront_2 is None)
        self.le_weight_input_wavefront_3.setEnabled(self.use_weights == 1 and not  self.input_wavefront_3 is None)
        self.le_weight_input_wavefront_4.setEnabled(self.use_weights == 1 and not  self.input_wavefront_4 is None)
        self.le_weight_input_wavefront_5.setEnabled(self.use_weights == 1 and not  self.input_wavefront_5 is None)
        self.le_weight_input_wavefront_6.setEnabled(self.use_weights == 1 and not  self.input_wavefront_6 is None)
        self.le_weight_input_wavefront_7.setEnabled(self.use_weights == 1 and not  self.input_wavefront_7 is None)
        self.le_weight_input_wavefront_8.setEnabled(self.use_weights == 1 and not  self.input_wavefront_8 is None)
        self.le_weight_input_wavefront_9.setEnabled(self.use_weights == 1 and not  self.input_wavefront_9 is None)
        self.le_weight_input_wavefront_10.setEnabled(self.use_weights == 1 and not  self.input_wavefront_10 is None)

        self.le_phase_input_wavefront_1.setEnabled(self.use_weights == 1 and not  self.input_wavefront_1 is None)
        self.le_phase_input_wavefront_2.setEnabled(self.use_weights == 1 and not  self.input_wavefront_2 is None)
        self.le_phase_input_wavefront_3.setEnabled(self.use_weights == 1 and not  self.input_wavefront_3 is None)
        self.le_phase_input_wavefront_4.setEnabled(self.use_weights == 1 and not  self.input_wavefront_4 is None)
        self.le_phase_input_wavefront_5.setEnabled(self.use_weights == 1 and not  self.input_wavefront_5 is None)
        self.le_phase_input_wavefront_6.setEnabled(self.use_weights == 1 and not  self.input_wavefront_6 is None)
        self.le_phase_input_wavefront_7.setEnabled(self.use_weights == 1 and not  self.input_wavefront_7 is None)
        self.le_phase_input_wavefront_8.setEnabled(self.use_weights == 1 and not  self.input_wavefront_8 is None)
        self.le_phase_input_wavefront_9.setEnabled(self.use_weights == 1 and not  self.input_wavefront_9 is None)
        self.le_phase_input_wavefront_10.setEnabled(self.use_weights == 1 and not  self.input_wavefront_10 is None)


add_widget_parameters_to_module(__name__)
