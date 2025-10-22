import numpy

from AnyQt.QtWidgets import QMessageBox
from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.widget import Input, Output

from oasys2.widget.widget import OWAction
from oasys2.widget import gui as oasysgui
from oasys2.widget.util import congruence
from oasys2.widget.util.widget_objects import TriggerOut
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module


from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

from wofryimpl.propagator.light_source import WOLightSource
from wofryimpl.beamline.beamline import WOBeamline


class OWGenericWavefront2D(WofryWidget):
    name = "Generic Wavefront 2D"
    id = "GenericWavefront2D"
    description = "Generic Wavefront 2D"
    icon = "icons/gw2d.png"
    priority = 101

    category = "Wofry Wavefront Propagation"
    keywords = ["data", "file", "load", "read"]

    class Inputs:
        trigger = Input("Trigger", TriggerOut, id="Trigger", default=True, auto_summary=False)

    class Outputs:
        wofry_data = Output("Wofry Data", WofryData, id="WofryData", default=True, auto_summary=False)

    units = Setting(1)
    energy = Setting(1000.0)
    wavelength = Setting(1e-10)
    number_of_points_h = Setting(100)
    number_of_points_v = Setting(100)

    initialize_from = Setting(0)

    range_from_h  = Setting(-0.0005)
    range_to_h    = Setting(0.0005)
    steps_start_h = Setting(-0.0005)
    steps_step_h  = Setting(1e-6)
    range_from_v  = Setting(-0.0005)
    range_to_v    = Setting(0.0005)
    steps_start_v = Setting(-0.0005)
    steps_step_v  = Setting(1e-6)

    kind_of_wave = Setting(0)

    initialize_amplitude = Setting(0)
    complex_amplitude_re = Setting(1.0)
    complex_amplitude_im = Setting(0.0)
    radius = Setting(1.0)

    gaussian_sigma_h = Setting(0.001)
    gaussian_sigma_v = Setting(0.001)
    gaussian_amplitude = Setting(1.0)
    gaussian_mode_h = Setting(0)
    gaussian_mode_v = Setting(0)
    gaussian_beta_h = Setting(1.0)
    gaussian_beta_v = Setting(1.0)

    amplitude = Setting(1.0)
    phase = Setting(0.0)

    wavefront2D = None

    def __init__(self):
        super().__init__(is_automatic=False, show_view_options=True)

        self.runaction = OWAction("Generate Wavefront", self)
        self.runaction.triggered.connect(self.generate)
        self.addAction(self.runaction)

        gui.separator(self.controlArea)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Generate", callback=self.generate)
        button.setStyleSheet("color: darkblue; font-weight: bold; height: 45px;")

        gui.separator(self.controlArea)

        self.controlArea.setFixedWidth(self.CONTROL_AREA_WIDTH)

        tabs_setting = oasysgui.tabWidget(self.controlArea)
        tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT + 50)
        tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_sou = oasysgui.createTabPage(tabs_setting, "Generic Wavefront 2D Settings")

        box_energy = oasysgui.widgetBox(self.tab_sou, "Energy Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_energy, self, "units", label="Units in use", labelWidth=350,
                     items=["Electron Volts", "Meters"],
                     callback=self.set_Units,
                     sendSelectedValue=False, orientation="horizontal")

        self.units_box_1 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_1, self, "energy", "Photon Energy [eV]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.units_box_2 = oasysgui.widgetBox(box_energy, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.units_box_2, self, "wavelength", "Photon Wavelength [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Units()

        box_space = oasysgui.widgetBox(self.tab_sou, "Space Settings", addSpace=False, orientation="vertical")

        number_of_points_box = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="horizontal")

        oasysgui.lineEdit(number_of_points_box, self, "number_of_points_h", "Number of Points                    (H)",
                          labelWidth=200, valueType=int, orientation="horizontal")
        oasysgui.lineEdit(number_of_points_box, self, "number_of_points_v", "x (V)",
                          valueType=int, orientation="horizontal")

        gui.comboBox(box_space, self, "initialize_from", label="Space Initialization", labelWidth=350,
                     items=["From Range", "From Steps"],
                     callback=self.set_Initialization,
                     sendSelectedValue=False, orientation="horizontal")

        self.initialization_box_1 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_from_h", "(H) From [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_to_h", "          To [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_from_v", "(V) From [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_1, self, "range_to_v", "          To [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.initialization_box_2 = oasysgui.widgetBox(box_space, "", addSpace=False, orientation="vertical")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_start_h", "(H) Start [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_step_h", "      Step [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_start_v", "(V) Start [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.initialization_box_2, self, "steps_step_v", "      Step [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Initialization()

        box_amplitude = oasysgui.widgetBox(self.tab_sou, "Amplitude Settings", addSpace=False, orientation="vertical")

        gui.comboBox(box_amplitude, self, "kind_of_wave", label="Kind of Wave", labelWidth=350,
                     items=["Plane", "Spherical", "Gaussian", "Gaussian Shell Model"],
                     callback=self.set_KindOfWave,
                     sendSelectedValue=False, orientation="horizontal")


        self.plane_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)
        self.spherical_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)
        self.gaussian_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)
        self.gsm_box = oasysgui.widgetBox(box_amplitude, "", addSpace=False, orientation="vertical", height=150)

        # --- PLANE

        gui.comboBox(self.plane_box, self, "initialize_amplitude", label="Amplitude Initialization", labelWidth=350,
                     items=["Complex", "Real"],
                     callback=self.set_Amplitude,
                     sendSelectedValue=False, orientation="horizontal")

        self.amplitude_box_1 = oasysgui.widgetBox(self.plane_box, "", addSpace=False, orientation="horizontal", height=50)

        oasysgui.lineEdit(self.amplitude_box_1, self, "complex_amplitude_re", "Complex Amplitude ",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.amplitude_box_1, self, "complex_amplitude_im", " + ",
                          valueType=float, orientation="horizontal")

        oasysgui.widgetLabel(self.amplitude_box_1, "i", labelWidth=15)

        self.amplitude_box_2 = oasysgui.widgetBox(self.plane_box, "", addSpace=False, orientation="vertical", height=50)

        oasysgui.lineEdit(self.amplitude_box_2, self, "amplitude", "Amplitude",
                          labelWidth=300, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.amplitude_box_2, self, "phase", "Phase",
                          labelWidth=300, valueType=float, orientation="horizontal")

        self.set_Amplitude()

        # ------ SPHERIC

        oasysgui.lineEdit(self.spherical_box, self, "radius", "Radius [m]",
                          labelWidth=300, valueType=float, orientation="horizontal")

        amplitude_box_3 = oasysgui.widgetBox(self.spherical_box, "", addSpace=False, orientation="horizontal", height=50)

        oasysgui.lineEdit(amplitude_box_3, self, "complex_amplitude_re", "Complex Amplitude ",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(amplitude_box_3, self, "complex_amplitude_im", " + ",
                          valueType=float, orientation="horizontal")

        oasysgui.widgetLabel(amplitude_box_3, "i", labelWidth=15)

        # ---- GAUSSIAN

        oasysgui.lineEdit(self.gaussian_box, self, "gaussian_sigma_h", "Sigma (H)",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gaussian_box, self, "gaussian_sigma_v", "Sigma (V)",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gaussian_box, self, "gaussian_amplitude", "Amplitude",
                          labelWidth=250, valueType=float, orientation="horizontal")

        # ---- GAUSSIAN SHELL MODEL

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_sigma_h", "H Sigma I",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_sigma_v", "V Sigma I",
                          labelWidth=250, valueType=float, orientation="horizontal")


        oasysgui.lineEdit(self.gsm_box, self, "gaussian_beta_h", "H beta = Sigma Mu/Sigma I",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_beta_v", "V beta = Sigma Mu/Sigma I",
                          labelWidth=250, valueType=float, orientation="horizontal")


        oasysgui.lineEdit(self.gsm_box, self, "gaussian_amplitude", "Amplitude",
                          labelWidth=250, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_mode_h", "H Mode",
                          labelWidth=250, valueType=int, orientation="horizontal")

        oasysgui.lineEdit(self.gsm_box, self, "gaussian_mode_v", "V Mode",
                          labelWidth=250, valueType=int, orientation="horizontal")

        self.set_KindOfWave()


    def set_Units(self):
        self.units_box_1.setVisible(self.units == 0)
        self.units_box_2.setVisible(self.units == 1)

    def set_Initialization(self):
        self.initialization_box_1.setVisible(self.initialize_from == 0)
        self.initialization_box_2.setVisible(self.initialize_from == 1)

    def set_Amplitude(self):
        self.amplitude_box_1.setVisible(self.initialize_amplitude == 0)
        self.amplitude_box_2.setVisible(self.initialize_amplitude == 1)

    def set_KindOfWave(self):
        self.plane_box.setVisible(self.kind_of_wave == 0)
        self.spherical_box.setVisible(self.kind_of_wave == 1)
        self.gaussian_box.setVisible(self.kind_of_wave == 2)
        self.gsm_box.setVisible(self.kind_of_wave == 3)

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Wavefront 2D","Phase"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def check_fields(self):
        if self.units == 0:
            congruence.checkStrictlyPositiveNumber(self.energy, "Energy")
        else:
            congruence.checkStrictlyPositiveNumber(self.wavelength, "Wavelength")

        congruence.checkStrictlyPositiveNumber(self.number_of_points_h, "Number of Points (H)")
        congruence.checkStrictlyPositiveNumber(self.number_of_points_v, "Number of Points (V)")

        if self.initialize_from == 0:
            congruence.checkGreaterThan(self.range_to_h, self.range_from_h, "(H) Range To", "Range From")
            congruence.checkGreaterThan(self.range_to_v, self.range_from_v, "(V) Range To", "Range From")
        else:
            congruence.checkStrictlyPositiveNumber(self.steps_step_h, "Step (H)")
            congruence.checkStrictlyPositiveNumber(self.steps_step_v, "Step (V)")

        if self.kind_of_wave == 1:
            congruence.checkStrictlyPositiveNumber(numpy.abs(self.radius), "Radius")
        elif self.kind_of_wave > 1:
            congruence.checkStrictlyPositiveNumber(self.gaussian_sigma_h, "Sigma (H)")
            congruence.checkStrictlyPositiveNumber(self.gaussian_sigma_v, "Sigma (V)")
            congruence.checkStrictlyPositiveNumber(self.gaussian_amplitude, "Amplitude")

            if self.kind_of_wave == 3:
                congruence.checkPositiveNumber(self.gaussian_mode_h, "Mode (H)")
                congruence.checkPositiveNumber(self.gaussian_mode_v, "Mode (V)")

    def get_light_source(self):

        return WOLightSource(
            name                = self.name                ,
            # electron_beam       = None  ,
            # magnetic_structure  = None  ,
            dimension           = 2           ,
            initialize_from     = self.initialize_from     ,
            range_from_h        = self.range_from_h        ,
            range_to_h          = self.range_to_h          ,
            range_from_v        = self.range_from_v       ,
            range_to_v          = self.range_to_v       ,
            steps_start_h       = self.steps_start_h       ,
            steps_step_h        = self.steps_step_h        ,
            steps_start_v       = self.steps_start_v       ,
            steps_step_v        = self.steps_step_v       ,
            number_of_points_h  = self.number_of_points_h  ,
            number_of_points_v  = self.number_of_points_v  ,
            energy              = self.energy       ,
            sigma_h             = self.gaussian_sigma_h             ,
            sigma_v             = self.gaussian_sigma_v             ,
            amplitude           = (self.gaussian_amplitude if self.kind_of_wave > 1 else 1.0),
            kind_of_wave        = self.kind_of_wave  ,
            n_h                 = self.gaussian_mode_h                 ,
            n_v                 = self.gaussian_mode_v                 ,
            beta_h              = self.gaussian_beta_h              ,
            beta_v              = self.gaussian_beta_v          ,
            units               = self.units,
            wavelength          = self.wavelength,
            initialize_amplitude= self.initialize_amplitude,
            complex_amplitude_re= self.complex_amplitude_re,
            complex_amplitude_im= self.complex_amplitude_im,
            phase               = self.phase,
            radius              = self.radius,
            # center              = 0,
            # inclination         = 0,
            # gaussian_shift      = 0,
            # add_random_phase    = 0,
        )

    def generate(self):

        try:
            self.wofry_output.setText("")
            self.progressBarInit()

            self.check_fields()

            light_source = self.get_light_source()
            self.wavefront2D = light_source.get_wavefront()

            self.initializeTabs()
            self.plot_results()

            beamline = WOBeamline(light_source=light_source)

            try:
                self.wofry_python_script.set_code(beamline.to_python_code())
            except:
                print(">>>>>>>>>>>>>>>  ERROR CREATING SCRIPT <<<<<<<<<<<<<<<<<")
                pass

            self.Outputs.wofry_data.send(WofryData(wavefront=self.wavefront2D, beamline=beamline))

        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

            self.progressBarFinished()

    def generate_python_code(self):

        txt = ""

        txt += "\n\n#"
        txt += "\n# create input_wavefront\n#"
        txt += "\n#"
        txt += "\nfrom wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D"

        if self.initialize_from == 0:
            txt += "\ninput_wavefront = GenericWavefront2D.initialize_wavefront_from_range(x_min=%g,x_max=%g,y_min=%g,y_max=%g,number_of_points=(%d,%d))"%\
            (self.range_from_h,self.range_to_h,self.range_from_v,self.range_to_v,self.number_of_points_h, self.number_of_points_v)

        else:
            txt += "\ninput_wavefront = GenericWavefront2D.initialize_wavefront_from_steps(x_start=%g, x_step=%g,y_start=%g,y_step=%g,"+\
                   "number_of_points=(%d,%d))"%\
                   (self.steps_start_h,self.steps_step_h,self.steps_start_v,self.steps_step_v,self.number_of_points_h,self.number_of_points_v)

        if self.units == 0:
            txt += "\ninput_wavefront.set_photon_energy(%g)"%(self.energy)
        else:
            txt += "\ninput_wavefront.set_wavelength(%g)"%(self.wavelength)

        if self.kind_of_wave == 0: #plane
            if self.initialize_amplitude == 0:
                txt += "\ninput_wavefront.set_plane_wave_from_complex_amplitude(complex_amplitude=complex(%g,%g))"%(self.complex_amplitude_re,self.complex_amplitude_im)
            else:
                txt += "\ninput_wavefront.set_plane_wave_from_amplitude_and_phase(amplitude=%g,phase=%g)"%(self.amplitude,self.phase)
        elif self.kind_of_wave == 1: # spheric
            txt += "\ninput_wavefront.set_spherical_wave(radius=%g,complex_amplitude=complex(%g, %g))"%(self.radius,self.complex_amplitude_re,self.complex_amplitude_im)
        elif self.kind_of_wave == 2: # gaussian
            txt += "\nwavefront2D.set_gaussian(sigma_x=%g,sigma_y=%g,amplitude=%g )"%(self.gaussian_sigma_h,self.gaussian_sigma_v,self.gaussian_amplitude)
        elif self.kind_of_wave == 3: # g.s.m.
            txt += "\nwavefront2D.set_gaussian_hermite_mode(sigma_x=%g,sigma_y=%g,amplitude=%g,nx=%d,ny=%d)"%\
                   (self.gaussian_sigma_h,self.gaussian_sigma_v,self.gaussian_amplitude,self.gaussian_mode_h,self.gaussian_mode_v)

        return txt

    def do_plot_results(self, progressBarValue):
        if not self.wavefront2D is None:

            self.progressBarSet(progressBarValue)

            titles = ["Wavefront 2D Intensity", "Wavefront 2D Phase"]

            self.plot_data2D(data2D=self.wavefront2D.get_intensity(),
                             dataX=1e6 * self.wavefront2D.get_coordinate_x(),
                             dataY=1e6 * self.wavefront2D.get_coordinate_y(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=0,
                             plot_canvas_index=0,
                             title=titles[0],
                             xtitle="Horizontal [$\\mu$m] ( %d pixels)" % (self.wavefront2D.get_coordinate_x().size),
                             ytitle="Vertical [$\\mu$m] ( %d pixels)" % (self.wavefront2D.get_coordinate_y().size))


            self.plot_data2D(data2D=self.wavefront2D.get_phase(from_minimum_intensity=0.1),
                             dataX=1e6 * self.wavefront2D.get_coordinate_x(),
                             dataY=1e6 * self.wavefront2D.get_coordinate_y(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             title=titles[1],
                             xtitle="Horizontal [$\\mu$m] ( %d pixels)" % (
                                 self.wavefront2D.get_coordinate_x().size),
                             ytitle="Vertical [$\\mu$m] ( %d pixels)" % (self.wavefront2D.get_coordinate_y().size))

            self.progressBarFinished()

    @Inputs.trigger
    def receive_trigger_signal(self, trigger):
        if trigger and trigger.new_object == True:
            if trigger.has_additional_parameter("variable_name"):
                variable_name = trigger.get_additional_parameter("variable_name").strip()
                variable_display_name = trigger.get_additional_parameter("variable_display_name").strip()
                variable_value = trigger.get_additional_parameter("variable_value")
                variable_um = trigger.get_additional_parameter("variable_um")

                if "," in variable_name:
                    variable_names = variable_name.split(",")

                    for variable_name in variable_names:
                        setattr(self, variable_name.strip(), variable_value)
                else:
                    setattr(self, variable_name, variable_value)

                self.generate()

add_widget_parameters_to_module(__name__)
