import sys

from AnyQt.QtWidgets import QMessageBox

from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.widget import Input, Output

from oasys2.widget.widget import OWAction
from oasys2.widget import gui as oasysgui
from oasys2.widget.util import congruence
from oasys2.widget.gui import ConfirmDialog
from oasys2.widget.util.widget_util import EmittingStream
from oasys2.widget.util.widget_objects import TriggerIn, TriggerOut

from syned.beamline.optical_elements.refractors.lens import Lens

from syned.widget.widget_decorator import WidgetDecorator
from syned.beamline.element_coordinates import ElementCoordinates
from syned.beamline.beamline_element import BeamlineElement
from syned.beamline.shape import *

from wofry.propagator.propagator import PropagationManager, PropagationElements, PropagationParameters
from wofry.propagator.wavefront2D.generic_wavefront import GenericWavefront2D
from wofryimpl.propagator.propagators2D import initialize_default_propagator_2D
from wofryimpl.propagator.propagators2D.fresnel import Fresnel2D
from wofryimpl.propagator.propagators2D.fresnel_convolution import FresnelConvolution2D
from wofryimpl.propagator.propagators2D.fraunhofer import Fraunhofer2D
from wofryimpl.propagator.propagators2D.integral import Integral2D
from wofryimpl.propagator.propagators2D.fresnel_zoom_xy import FresnelZoomXY2D

from orangecontrib.wofry.util.wofry_objects import WofryData
from orangecontrib.wofry.widgets.gui.ow_wofry_widget import WofryWidget

try:
    initialize_default_propagator_2D()
except Exception as e:
    print("cannot initialize Wofry 2D propagators: " + str(e))


class OWWOOpticalElement2D(WofryWidget, WidgetDecorator):

    maintainer = "Luca Rebuffi"
    maintainer_email = "luca.rebuffi(@at@)elettra.eu"
    keywords = ["data", "file", "load", "read"]
    category = "Wofry Optical Elements"

    class Inputs:
        wofry_data        = Input("Wofry Data", WofryData, default=True, auto_summary=False)
        generic_wavefront = Input("Generic Wavefront 2D", GenericWavefront2D, default=True, auto_summary=False)
        trigger           = Input("Trigger", TriggerOut, id="Trigger", default=True, auto_summary=False)
        syned_data        = WidgetDecorator.syned_input_data(multi_input=True)

    class Outputs:
        wofry_data = Output("Wofry Data", WofryData, id="WofryData", default=True, auto_summary=False)
        trigger  = Output("Trigger", TriggerIn, id="Trigger", default=True, auto_summary=False)

    oe_name         = Setting("")
    p               = Setting(0.0)
    q               = Setting(0.0)
    angle_radial    = Setting(0.0)
    angle_azimuthal = Setting(0.0)

    shape = Setting(0)
    surface_shape = Setting(0)

    input_data = None
    wavefront_to_plot = None

    propagators_list = ["Fresnel", "Fresnel (Convolution)", "Fraunhofer", "Integral", "Fresnel Zoom XY"]

    propagator = Setting(4)
    shift_half_pixel = Setting(1)

    shuffle_interval = Setting(0)
    calculate_grid_only = Setting(1)
    magnification_x = Setting(1.0)
    magnification_y = Setting(1.0)

    def __init__(self, is_automatic=True, show_view_options=True, show_script_tab=True):
        super().__init__(is_automatic=is_automatic, show_view_options=show_view_options, show_script_tab=show_script_tab)

        self.runaction = OWAction("Propagate Wavefront", self)
        self.runaction.triggered.connect(self.propagate_wavefront)
        self.addAction(self.runaction)

        button_box = oasysgui.widgetBox(self.controlArea, "", addSpace=False, orientation="horizontal")

        button = gui.button(button_box, self, "Propagate Wavefront", callback=self.propagate_wavefront)
        button.setStyleSheet("color: darkblue; font-weight: bold; height: 45px;")

        button = gui.button(button_box, self, "Reset Fields", callback=self.callResetSettings)
        button.setStyleSheet("color: darkred; font-weight: bold; font-style: italic; height: 45px; width: 150px;")

        gui.separator(self.controlArea)

        self.tabs_setting = oasysgui.tabWidget(self.controlArea)
        self.tabs_setting.setFixedHeight(self.TABS_AREA_HEIGHT)
        self.tabs_setting.setFixedWidth(self.CONTROL_AREA_WIDTH-5)

        self.tab_bas = oasysgui.createTabPage(self.tabs_setting, "O.E. Setting")
        self.tab_pro = oasysgui.createTabPage(self.tabs_setting, "Propagation Setting")

        oasysgui.lineEdit(self.tab_bas, self, "oe_name", "O.E. Name", labelWidth=260, valueType=str, orientation="horizontal")

        self.coordinates_box = oasysgui.widgetBox(self.tab_bas, "Coordinates", addSpace=True, orientation="vertical")

        oasysgui.lineEdit(self.coordinates_box, self, "p", "Distance from previous Continuation Plane [m]", labelWidth=280, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.coordinates_box, self, "q", "Distance to next Continuation Plane [m]", labelWidth=280, valueType=float, orientation="horizontal")
        # srio commented; TODO: implement it correctly
        # oasysgui.lineEdit(self.coordinates_box, self, "angle_radial", "Incident Angle (to normal) [deg]", labelWidth=280, valueType=float, orientation="horizontal")
        # oasysgui.lineEdit(self.coordinates_box, self, "angle_azimuthal", "Rotation along Beam Axis [deg]", labelWidth=280, valueType=float, orientation="horizontal")

        self.draw_specific_box()

        gui.comboBox(self.tab_pro, self, "propagator", label="Propagator", labelWidth=260,
                     items=self.propagators_list,
                     callback=self.set_Propagator,
                     sendSelectedValue=False, orientation="horizontal")

        self.fresnel_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        gui.comboBox(self.fresnel_box, self, "shift_half_pixel", label="Shift Half Pixel", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        self.fraunhofer_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        gui.comboBox(self.fraunhofer_box, self, "shift_half_pixel", label="Shift Half Pixel", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        # integral
        self.integral_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)


        oasysgui.lineEdit(self.integral_box, self, "shuffle_interval", "Shuffle Interval (0=no shift) [m]", labelWidth=260, valueType=float, orientation="horizontal")

        gui.comboBox(self.integral_box, self, "calculate_grid_only", label="Calculate Grid Only", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")


        oasysgui.lineEdit(self.integral_box, self, "magnification_x", "Magnification X",
                          labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.integral_box, self, "magnification_y", "Magnification Y",
                          labelWidth=260, valueType=float, orientation="horizontal")

        #new zoom
        self.zoom_box = oasysgui.widgetBox(self.tab_pro, "", addSpace=False, orientation="vertical", height=90)

        gui.comboBox(self.zoom_box, self, "shift_half_pixel", label="Shift Half Pixel", labelWidth=260,
                     items=["No", "Yes"],
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.zoom_box, self, "magnification_x", "Magnification X",
                          labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.zoom_box, self, "magnification_y", "Magnification Y",
                          labelWidth=260, valueType=float, orientation="horizontal")

        self.set_Propagator()

    def set_Propagator(self):
        self.fresnel_box.setVisible(self.propagator <= 1)
        self.fraunhofer_box.setVisible(self.propagator == 2)
        self.integral_box.setVisible(self.propagator == 3)
        self.zoom_box.setVisible(self.propagator == 4)

    def draw_specific_box(self):
        # raise NotImplementedError()
        pass

    def check_data(self):
        congruence.checkNumber(self.p, "Distance from previous Continuation Plane")
        congruence.checkNumber(self.q, "Distance to next Continuation Plane")
        congruence.checkAngle(self.angle_radial, "Incident Angle (to normal)")
        congruence.checkAngle(self.angle_azimuthal, "Rotation along Beam Axis")

    @Inputs.trigger
    def propagate_new_wavefront(self, trigger):
        try:
            if trigger and trigger.new_object == True:
                if trigger.has_additional_parameter("variable_name"):
                    if self.input_data is None: raise Exception("No Input Data")

                    try:
                        variable_name         = trigger.get_additional_parameter("variable_name").strip()
                        variable_display_name = trigger.get_additional_parameter("variable_display_name").strip()
                        variable_value        = trigger.get_additional_parameter("variable_value")
                        variable_um           = trigger.get_additional_parameter("variable_um")

                        if "," in variable_name:
                            variable_names = variable_name.split(",")

                            for variable_name in variable_names:
                                setattr(self, variable_name.strip(), variable_value)
                        else:
                            setattr(self, variable_name, variable_value)

                        self.input_data.get_wavefront().set_scanning_data(GenericWavefront2D.ScanningData(variable_name,
                                                                                                          variable_value,
                                                                                                          variable_display_name,
                                                                                                          variable_um))

                        self.propagate_wavefront()
                    except:
                        raise NotImplementedError("Scanning Loops not implemented, yet")
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def propagate_wavefront(self):
        self.wofry_output.setText("")
        self.progressBarInit()

        sys.stdout = EmittingStream(textWritten=self.writeStdOut)

        try:
            if self.input_data is None: raise Exception("No Input Data")

            self.check_data()

            # propagation to o.e.

            input_wavefront  = self.input_data.get_wavefront()
            beamline         = self.input_data.get_beamline().duplicate()

            optical_element = self.get_optical_element()
            optical_element.name = self.oe_name if not self.oe_name is None else self.windowTitle()

            beamline_element = BeamlineElement(optical_element=optical_element,
                                               coordinates=ElementCoordinates(p=self.p,
                                                                              q=self.q,
                                                                              angle_radial=numpy.radians(self.angle_radial),
                                                                              angle_azimuthal=numpy.radians(self.angle_azimuthal)))

            #
            # this will store the propagation parameters in beamline in order to perform the propagation in the script
            #

            # 2D
            # ==
            # propagators_list = ["Fresnel",   "Fresnel (Convolution)",  "Fraunhofer",    "Integral",    "Fresnel Zoom XY"   ]
            # class_name       = ["Fresnel2D", "FresnelConvolution2D",   "Fraunhofer2D",  "Integral2D",  "FresnelZoomXY2D"   ]
            # handler_name     = ["FRESNEL_2D","FRESNEL_CONVOLUTION_2D", "FRAUNHOFER_2D", "INTEGRAL_2D", "FRESNEL_ZOOM_XY_2D"]
            if self.propagator == 0:
                propagator_info = {
                    "propagator_class_name": "Fresnel2D",
                    "propagator_handler_name": self.get_handler_name(),
                    "propagator_additional_parameters_names": [],
                    "propagator_additional_parameters_values": []}
            elif self.propagator == 1:
                propagator_info = {
                    "propagator_class_name": "FresnelConvolution2D",
                    "propagator_handler_name": self.get_handler_name(),
                    "propagator_additional_parameters_names": [],
                    "propagator_additional_parameters_values": []}
            elif self.propagator == 2:
                propagator_info = {
                    "propagator_class_name": "Fraunhofer2D",
                    "propagator_handler_name": self.get_handler_name(),
                    "propagator_additional_parameters_names": [],
                    "propagator_additional_parameters_values": []}
            elif self.propagator == 3:
                propagator_info = {
                    "propagator_class_name": "Integral2D",
                    "propagator_handler_name": self.get_handler_name(),
                    "propagator_additional_parameters_names": ["shuffle_interval", "calculate_grid_only",
                                                               "magnification_x", "magnification_y"],
                    "propagator_additional_parameters_values": [self.shuffle_interval, self.calculate_grid_only,
                                                                self.magnification_x, self.magnification_y]}
            elif self.propagator == 4:
                propagator_info = {
                    "propagator_class_name": "FresnelZoomXY2D",
                    "propagator_handler_name": self.get_handler_name(),
                    "propagator_additional_parameters_names": ['shift_half_pixel', 'magnification_x','magnification_y'],
                    "propagator_additional_parameters_values": [self.shift_half_pixel, self.magnification_x, self.magnification_y]}


            beamline.append_beamline_element(beamline_element, propagator_info)


            propagation_elements = PropagationElements()
            propagation_elements.add_beamline_element(beamline_element)

            propagation_parameters = PropagationParameters(wavefront=input_wavefront.duplicate(),
                                                           propagation_elements=propagation_elements)

            self.set_additional_parameters(propagation_parameters)

            self.setStatusMessage("Begin Propagation")

            propagator = PropagationManager.Instance()

            output_wavefront = propagator.do_propagation(propagation_parameters=propagation_parameters,
                                                         handler_name=self.get_handler_name())

            self.setStatusMessage("Propagation Completed")

            self.wavefront_to_plot = output_wavefront

            self.initializeTabs()
            self.do_plot_results()
            self.progressBarFinished()

            self.Outputs.wofry_data.send(WofryData(beamline=beamline, wavefront=output_wavefront))
            self.Outputs.trigger.send(TriggerIn(new_object=True))

            try:
                self.wofry_python_script.set_code(beamline.to_python_code())
            except:
                pass

            self.setStatusMessage("")
            try:
                self.print_intensities()
            except:
                pass
        except Exception as exception:
            QMessageBox.critical(self, "Error", str(exception), QMessageBox.Ok)

            if self.IS_DEVELOP: raise exception

    def print_intensities(self):
        input_wavefront = self.input_data.get_wavefront()
        output_wavefront = self.wavefront_to_plot

        c1 = input_wavefront.get_intensity().sum()
        c2 = output_wavefront.get_intensity().sum()
        dx1, dy1 = input_wavefront.delta()
        dx2, dy2 = output_wavefront.delta()
        i1 = input_wavefront.get_integrated_intensity()
        i2 = output_wavefront.get_integrated_intensity()
        print("\n\n\n ==========  integrated intensities: ")
        print("input wavefront integrated intensity: %g" % (i1))
        print("output wavefront integrated intensity: %g" % (i2))
        print("output/input intensity ratio (transmission): %g " % (i2 / i1))
        print("(input-output)/input intensity ratio (absorption): %g " % ((i1 - i2) / i1))
        print("step in: (%g,%g) um, out: (%g,%g) um" % (1e6 * dx1, 1e6 * dy1, 1e6 * dx2, 1e6 * dy2))

    def get_handler_name(self):
        if self.propagator == 0:
            return Fresnel2D.HANDLER_NAME
        elif self.propagator == 1:
            return FresnelConvolution2D.HANDLER_NAME
        elif self.propagator == 2:
            return Fraunhofer2D.HANDLER_NAME
        elif self.propagator == 3:
            return Integral2D.HANDLER_NAME
        elif self.propagator == 4:
            return FresnelZoomXY2D.HANDLER_NAME

    def set_additional_parameters(self, propagation_parameters):
        if self.propagator <= 2:
            propagation_parameters.set_additional_parameters("shift_half_pixel", self.shift_half_pixel==1)
        elif self.propagator == 3:
            propagation_parameters.set_additional_parameters("shuffle_interval", self.shuffle_interval)
            propagation_parameters.set_additional_parameters("calculate_grid_only", self.calculate_grid_only)
            propagation_parameters.set_additional_parameters("magnification_x", self.magnification_x)
            propagation_parameters.set_additional_parameters("magnification_y", self.magnification_y)
        elif self.propagator == 4:
            propagation_parameters.set_additional_parameters("shift_half_pixel", self.shift_half_pixel == 1)
            propagation_parameters.set_additional_parameters("magnification_x", self.magnification_x)
            propagation_parameters.set_additional_parameters("magnification_y", self.magnification_y)

    def get_optical_element(self):
        raise NotImplementedError()

    @Inputs.wofry_data
    def set_wofry_data(self, wofry_data):
        self.set_input(wofry_data)

    @Inputs.generic_wavefront
    def set_generic_wavefront(self, generic_wavefront):
        self.set_input(generic_wavefront)

    def set_input(self, wofry_data):
        if not wofry_data is None:
            if isinstance(wofry_data, WofryData):
                self.input_data = wofry_data
            elif isinstance(wofry_data, GenericWavefront2D):
                self.input_data = WofryData(wavefront=wofry_data)
            else:
                raise Exception("Bad input.")

            if self.is_automatic_execution:
                self.propagate_wavefront()

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Intensity","Phase"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)

    def do_plot_results(self, progressBarValue=80):
        if not self.view_type == 0:
            if not self.wavefront_to_plot is None:

                self.progressBarSet(progressBarValue)

                titles = ["Wavefront 2D Intensity","Wavefront 2D Phase"]

                self.plot_data2D(data2D=self.wavefront_to_plot.get_intensity(),
                                 dataX=1e6*self.wavefront_to_plot.get_coordinate_x(),
                                 dataY=1e6*self.wavefront_to_plot.get_coordinate_y(),
                                 progressBarValue=progressBarValue,
                                 tabs_canvas_index=0,
                                 plot_canvas_index=0,
                                 title=titles[0],
                                 xtitle="Horizontal [$\\mu$m] ( %d pixels)"%(self.wavefront_to_plot.get_coordinate_x().size),
                                 ytitle="Vertical [$\\mu$m] ( %d pixels)"%(self.wavefront_to_plot.get_coordinate_y().size))

                self.plot_data2D(data2D=self.wavefront_to_plot.get_phase(from_minimum_intensity=0.1),
                             dataX=1e6*self.wavefront_to_plot.get_coordinate_x(),
                             dataY=1e6*self.wavefront_to_plot.get_coordinate_y(),
                             progressBarValue=progressBarValue,
                             tabs_canvas_index=1,
                             plot_canvas_index=1,
                             title=titles[1],
                             xtitle="Horizontal [$\\mu$m] ( %d pixels)"%(self.wavefront_to_plot.get_coordinate_x().size),
                             ytitle="Vertical [$\\mu$m] ( %d pixels)"%(self.wavefront_to_plot.get_coordinate_y().size))

                self.progressBarFinished()

    @Inputs.syned_data
    def set_syned_data(self, index, syned_data):
        self.receive_syned_data(syned_data)

    @Inputs.syned_data.insert
    def insert_syned_data(self, index, syned_data):
        self.receive_syned_data(syned_data)

    @Inputs.syned_data.remove
    def remove_syned_data(self, index):
        pass

    def receive_syned_data(self, data):
        if not data is None:
            beamline_element = data.get_beamline_element_at(-1)

            if not beamline_element is None:
                self.oe_name = beamline_element._optical_element._name
                self.p = beamline_element._coordinates._p
                self.q = beamline_element._coordinates._q
                self.angle_azimuthal = round(numpy.degrees(beamline_element._coordinates._angle_azimuthal), 6)
                self.angle_radial = round(numpy.degrees(beamline_element._coordinates._angle_radial), 6)

                self.receive_specific_syned_data(beamline_element._optical_element)
            else:
                raise Exception("Syned Data not correct: Empty Beamline Element")

    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            if isinstance(optical_element, Lens):
                self.lens_radius = optical_element._radius
                self.wall_thickness = optical_element._thickness
                self.material = optical_element._material
            else:
                raise Exception("Syned Data not correct: Optical Element is not a Lens")
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")

    def callResetSettings(self):
        if ConfirmDialog.confirmed(parent=self, message="Confirm Reset of the Fields?"):
            try:
                self._reset_settings()
            except:
                pass




# --------------------------------------------------------------

class OWWOOpticalElement2DWithBoundaryShape(OWWOOpticalElement2D):
    # BOUNDARY

    horizontal_shift = Setting(0.0)
    vertical_shift = Setting(0.0)

    width = Setting(0.0)
    height = Setting(0.0)

    radius = Setting(0.0)

    min_ax = Setting(0.0)
    maj_ax = Setting(0.0)

    def draw_specific_box(self):

        self.shape_box = oasysgui.widgetBox(self.tab_bas, "Boundary Shape", addSpace=True, orientation="vertical")

        gui.comboBox(self.shape_box, self, "shape", label="Boundary Shape", labelWidth=350,
                     items=["Rectangle", "Circle", "Ellipse"],
                     callback=self.set_Shape,
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.shape_box, self, "horizontal_shift", "Horizontal Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.shape_box, self, "vertical_shift", "Vertical Shift [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.rectangle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.rectangle_box, self, "width", "Width [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.rectangle_box, self, "height", "Height [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.circle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.circle_box, self, "radius", "Radius [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.ellipse_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.ellipse_box, self, "min_ax", "Axis a [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.ellipse_box, self, "maj_ax", "Axis b [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.set_Shape()

    def set_Shape(self):
        self.rectangle_box.setVisible(self.shape == 0)
        self.circle_box.setVisible(self.shape == 1)
        self.ellipse_box.setVisible(self.shape == 2)

    def get_boundary_shape(self):
        if self.shape == 0:
            boundary_shape = Rectangle(x_left=-0.5*self.width + self.horizontal_shift,
                                       x_right=0.5*self.width + self.horizontal_shift,
                                       y_bottom=-0.5*self.height + self.vertical_shift,
                                       y_top=0.5*self.height + self.vertical_shift)

        elif self.shape == 1:
            boundary_shape = Circle( self.radius,
                                     x_center=self.horizontal_shift,
                                     y_center=self.vertical_shift)
        elif self.shape == 2:
            boundary_shape = Ellipse(a_axis_min=-0.5*self.min_ax + self.horizontal_shift,
                                     a_axis_max=0.5*self.min_ax + self.horizontal_shift,
                                     b_axis_min=-0.5*self.maj_ax + self.vertical_shift,
                                     b_axis_max=0.5*self.maj_ax + self.vertical_shift)

        return boundary_shape


    def check_data(self):
        super().check_data()

        congruence.checkNumber(self.horizontal_shift, "Horizontal Shift")
        congruence.checkNumber(self.vertical_shift, "Vertical Shift")

        if self.shape == 0:
            congruence.checkStrictlyPositiveNumber(self.width, "Width")
            congruence.checkStrictlyPositiveNumber(self.height, "Height")
        elif self.shape == 1:
            congruence.checkStrictlyPositiveNumber(self.radius, "Radius")
        elif self.shape == 2:
            congruence.checkStrictlyPositiveNumber(self.min_ax, "(Boundary) Minor Axis")
            congruence.checkStrictlyPositiveNumber(self.maj_ax, "(Boundary) Major Axis")

    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            self.check_syned_instance(optical_element)

            if not optical_element._boundary_shape is None:

                left, right, bottom, top = optical_element._boundary_shape.get_boundaries()

                self.horizontal_shift = round(((right + left) / 2), 6)
                self.vertical_shift = round(((top + bottom) / 2), 6)

                if isinstance(optical_element._boundary_shape, Rectangle):
                    self.shape = 0

                    self.width = round((numpy.abs(right - left)), 6)
                    self.height = round((numpy.abs(top - bottom)), 6)

                if isinstance(optical_element._boundary_shape, Circle):
                    self.shape = 1

                if isinstance(optical_element._boundary_shape, Ellipse):
                    self.shape = 2

                    self.min_ax = round((numpy.abs(right - left)), 6)
                    self.maj_ax = round((numpy.abs(top - bottom)), 6)

                self.set_Shape()
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")

# --------------------------------------------------------------

class OWWOOpticalElement2DWithDoubleBoundaryShape(OWWOOpticalElement2D):
    # BOUNDARY

    horizontal_shift = Setting(-500e-6)
    vertical_shift = Setting(-400e-6)

    width = Setting(1e-3)
    height = Setting(1e-4)

    radius = Setting(50e-6)

    min_ax = Setting(1e-3)
    maj_ax = Setting(1e-4)

    # the same for patch 2
    horizontal_shift2 = Setting(500e-6)
    vertical_shift2 = Setting(400e-6)

    width2 = Setting(1e-3)
    height2 = Setting(1e-4)

    radius2 = Setting(30e-6)

    min_ax2 = Setting(1e-3)
    maj_ax2 = Setting(1e-4)

    def draw_specific_box(self):

        self.shape_box = oasysgui.widgetBox(self.tab_bas, "Boundary Shape", addSpace=True, orientation="vertical")

        gui.comboBox(self.shape_box, self, "shape", label="Boundary Shape", labelWidth=350,
                     items=["Rectangle", "Circle", "Ellipse"],
                     callback=self.set_Shape,
                     sendSelectedValue=False, orientation="horizontal")

        oasysgui.lineEdit(self.shape_box, self, "horizontal_shift", "Horizontal Shift Patch 1[m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.shape_box, self, "vertical_shift", "Vertical Shift Patch 1 [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.shape_box, self, "horizontal_shift2", "Horizontal Shift Patch 2[m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.shape_box, self, "vertical_shift2", "Vertical Shift Patch 2[m]", labelWidth=260, valueType=float, orientation="horizontal")


        self.rectangle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=120)

        oasysgui.lineEdit(self.rectangle_box, self, "width", "Width Patch 1[m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.rectangle_box, self, "height", "Height Patch 1[m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.rectangle_box, self, "width2", "Width Patch 2[m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.rectangle_box, self, "height2", "Height Patch 2[m]", labelWidth=260, valueType=float, orientation="horizontal")


        self.circle_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.circle_box, self, "radius", "Radius Patch 1 [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.circle_box, self, "radius2", "Radius Patch 2 [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.ellipse_box = oasysgui.widgetBox(self.shape_box, "", addSpace=False, orientation="vertical", height=120)

        oasysgui.lineEdit(self.ellipse_box, self, "min_ax", "Axis a Patch 1 [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.ellipse_box, self, "maj_ax", "Axis b Patch 1 [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.ellipse_box, self, "min_ax2", "Axis a Patch 2 [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.ellipse_box, self, "maj_ax2", "Axis b Patch 2 [m]", labelWidth=260, valueType=float, orientation="horizontal")

        self.set_Shape()

    def set_Shape(self):
        self.rectangle_box.setVisible(self.shape == 0)
        self.circle_box.setVisible(self.shape == 1)
        self.ellipse_box.setVisible(self.shape == 2)

    def get_boundary_shape(self):
        if self.shape == 0:
            boundary_shape = DoubleRectangle(x_left1   =-0.5*self.width  + self.horizontal_shift,
                                             x_right1  = 0.5*self.width  + self.horizontal_shift,
                                             y_bottom1 =-0.5*self.height + self.vertical_shift,
                                             y_top1    = 0.5*self.height + self.vertical_shift,
                                             x_left2   =-0.5*self.width2  + self.horizontal_shift2,
                                             x_right2  = 0.5*self.width2  + self.horizontal_shift2,
                                             y_bottom2 =-0.5*self.height2 + self.vertical_shift2,
                                             y_top2    = 0.5*self.height2 + self.vertical_shift2,)

        elif self.shape == 1:
            boundary_shape = DoubleCircle( radius1=self.radius,
                                     x_center1=self.horizontal_shift,
                                     y_center1=self.vertical_shift,
                                     radius2=self.radius2,
                                     x_center2=self.horizontal_shift2,
                                     y_center2=self.vertical_shift2,
                                           )
        elif self.shape == 2:
            boundary_shape = DoubleEllipse(
                                    a_axis_min1 =-0.5*self.min_ax + self.horizontal_shift,
                                    a_axis_max1 =0.5*self.min_ax + self.horizontal_shift,
                                    b_axis_min1 =-0.5*self.maj_ax + self.vertical_shift,
                                    b_axis_max1 =0.5*self.maj_ax + self.vertical_shift,
                                    a_axis_min2 =-0.5*self.min_ax2 + self.horizontal_shift2,
                                    a_axis_max2 =0.5*self.min_ax2 + self.horizontal_shift2,
                                    b_axis_min2 =-0.5*self.maj_ax2 + self.vertical_shift2,
                                    b_axis_max2 =0.5*self.maj_ax2 + self.vertical_shift2,
                                    )

        return boundary_shape

    def get_boundary_shape_python_code(self):
        txt = ""
        if self.shape == 0:
            txt += "\nfrom syned.beamline.shape import DoubleRectangle"
            txt += "\nboundary_shape = DoubleRectangle(x_left1=%g,"%(-0.5*self.width + self.horizontal_shift)
            txt += "x_right1=%g,"%(0.5*self.width + self.horizontal_shift)
            txt += "y_bottom1=%g,"%(-0.5*self.height + self.vertical_shift)
            txt += "y_top1=%g,"%(0.5*self.height + self.vertical_shift)
            txt += "\n    x_left2=%g,"%(-0.5*self.width2 + self.horizontal_shift2)
            txt += "x_right2=%g,"%(0.5*self.width2 + self.horizontal_shift2)
            txt += "y_bottom2=%g,"%(-0.5*self.height2 + self.vertical_shift2)
            txt += "y_top2=%g)\n"%(0.5*self.height2 + self.vertical_shift2)
        elif self.shape == 1:
            txt += "\nfrom syned.beamline.shape import DoubleCircle\n"
            txt += "\nboundary_shape = DoubleCircle(radius1=%g,"%(self.radius)
            txt += "                         x_center1=%g,\n"%(self.horizontal_shift)
            txt += "                         y_center1=%g,\n"%(self.vertical_shift)
            txt += "                         radius2=%g,\n"%(self.radius2)
            txt += "                         x_center2=%g,\n"%(self.horizontal_shift2)
            txt += "                         y_center2=%g)\n"%(self.vertical_shift2)

        elif self.shape == 2:
            txt += "\nfrom syned.beamline.shape import Ellipse\n"
            txt += "\nboundary_shape = Ellipse(a_axis_min1=%g,\n"%(-0.5*self.min_ax + self.horizontal_shift)
            txt += "                         a_axis_max1=%g,\n"%(   0.5*self.min_ax + self.horizontal_shift)
            txt += "                         b_axis_min1=%g,\n"%(  -0.5*self.maj_ax + self.vertical_shift)
            txt += "                         b_axis_max1=%g)\n"%(   0.5*self.maj_ax + self.vertical_shift)
            txt += "                         a_axis_min2=%g,\n"%(  -0.5*self.min_ax2 + self.horizontal_shift2)
            txt += "                         a_axis_max2=%g,\n"%(   0.5*self.min_ax2 + self.horizontal_shift2)
            txt += "                         b_axis_min2=%g,\n"%(  -0.5*self.maj_ax2 + self.vertical_shift2)
            txt += "                         b_axis_max2=%g)\n"%(   0.5*self.maj_ax2 + self.vertical_shift2)

        return txt



    def check_data(self):
        super().check_data()

        congruence.checkNumber(self.horizontal_shift, "Horizontal Shift")
        congruence.checkNumber(self.vertical_shift, "Vertical Shift")

        if self.shape == 0:
            congruence.checkStrictlyPositiveNumber(self.width, "Width")
            congruence.checkStrictlyPositiveNumber(self.height, "Height")
        elif self.shape == 1:
            congruence.checkStrictlyPositiveNumber(self.radius, "Radius")
        elif self.shape == 2:
            congruence.checkStrictlyPositiveNumber(self.min_ax, "(Boundary) Minor Axis")
            congruence.checkStrictlyPositiveNumber(self.maj_ax, "(Boundary) Major Axis")

    def receive_specific_syned_data(self, optical_element):
        if not optical_element is None:
            self.check_syned_instance(optical_element)

            if not optical_element._boundary_shape is None:

                left, right, bottom, top = optical_element._boundary_shape.get_boundaries()

                self.horizontal_shift = round(((right + left) / 2), 6)
                self.vertical_shift = round(((top + bottom) / 2), 6)

                if isinstance(optical_element._boundary_shape, Rectangle):
                    self.shape = 0

                    self.width = round((numpy.abs(right - left)), 6)
                    self.height = round((numpy.abs(top - bottom)), 6)

                if isinstance(optical_element._boundary_shape, Circle):
                    self.shape = 1

                if isinstance(optical_element._boundary_shape, Ellipse):
                    self.shape = 2

                    self.min_ax = round((numpy.abs(right - left)), 6)
                    self.maj_ax = round((numpy.abs(top - bottom)), 6)

                self.set_Shape()
        else:
            raise Exception("Syned Data not correct: Empty Optical Element")

# --------------------------------------------------------------

class OWWOOpticalElement2DWithSurfaceShape(OWWOOpticalElement2DWithBoundaryShape):

    # SURFACE

    convexity = Setting(0)
    is_cylinder = Setting(1)
    cylinder_direction = Setting(0)

    p_surface = Setting(0.0)
    q_surface = Setting(0.0)

    calculate_sphere_parameter = Setting(0)
    calculate_ellipsoid_parameter = Setting(0)
    calculate_paraboloid_parameter = Setting(0)
    calculate_hyperboloid_parameter = Setting(0)
    calculate_torus_parameter = Setting(0)


    # SPHERE
    radius_surface = Setting(0.0)

    # ELLIPSOID/HYPERBOLOID
    min_ax_surface = Setting(0.0)
    maj_ax_surface = Setting(0.0)

    # PARABOLOID
    parabola_parameter_surface = Setting(0.0)
    at_infinty_surface = Setting(0.0)

    # TORUS
    min_radius_surface = Setting(0.0)
    maj_radius_surface = Setting(0.0)

    def draw_specific_box(self, tab_oe):

        super().draw_specific_box()

        self.surface_shape_box = oasysgui.widgetBox(tab_oe, "Surface Shape", addSpace=True, orientation="vertical", height=190)

        gui.comboBox(self.surface_shape_box, self, "surface_shape", label="Surface Shape", labelWidth=350,
                     items=["Plane", "Sphere", "Ellipsoid", "Paraboloid", "Hyperboloid", "Toroidal"],
                     callback=self.set_SurfaceParameters,
                     sendSelectedValue=False, orientation="horizontal")


        self.plane_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)

        self.sphere_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
        self.ellipsoid_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
        self.paraboloid_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=115)
        self.hyperboloid_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)
        self.torus_box = oasysgui.widgetBox(self.surface_shape_box, "", addSpace=False, orientation="vertical", height=90)

        # SPHERE --------------------------

        gui.comboBox(self.sphere_box, self, "calculate_sphere_parameter", label="Sphere Shape", labelWidth=350,
                     items=["Manual", "Automatic"],
                     callback=self.set_SphereShape,
                     sendSelectedValue=False, orientation="horizontal")

        self.sphere_box_1 = oasysgui.widgetBox(self.sphere_box, "", addSpace=False, orientation="vertical", height=60)
        self.sphere_box_2 = oasysgui.widgetBox(self.sphere_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.sphere_box_1, self, "radius_surface", "Radius [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.sphere_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.sphere_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")


        # ELLIPSOID --------------------------

        gui.comboBox(self.ellipsoid_box, self, "calculate_ellipsoid_parameter", label="Ellipsoid Shape", labelWidth=350,
                     items=["Manual", "Automatic"],
                     callback=self.set_EllipsoidShape,
                     sendSelectedValue=False, orientation="horizontal")

        self.ellipsoid_box_1 = oasysgui.widgetBox(self.ellipsoid_box, "", addSpace=False, orientation="vertical", height=60)
        self.ellipsoid_box_2 = oasysgui.widgetBox(self.ellipsoid_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.ellipsoid_box_1, self, "min_ax_surface", "Minor Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.ellipsoid_box_1, self, "maj_ax_surface", "Major Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.ellipsoid_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.ellipsoid_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")


        # PARABOLOID --------------------------

        gui.comboBox(self.paraboloid_box, self, "calculate_paraboloid_parameter", label="Sphere Shape", labelWidth=350,
                     items=["Manual", "Automatic"],
                     callback=self.set_ParaboloidShape,
                     sendSelectedValue=False, orientation="horizontal")

        self.paraboloid_box_1 = oasysgui.widgetBox(self.paraboloid_box, "", addSpace=False, orientation="vertical", height=85)
        self.paraboloid_box_2 = oasysgui.widgetBox(self.paraboloid_box, "", addSpace=False, orientation="vertical", height=85)

        oasysgui.lineEdit(self.paraboloid_box_1, self, "parabola_parameter_surface", "Parabola Parameter [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.paraboloid_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.paraboloid_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")

        gui.comboBox(self.paraboloid_box_2, self, "at_infinty_surface", label="At infinity", labelWidth=350,
                     items=["Source", "Image"],
                     sendSelectedValue=False, orientation="horizontal")


        # HYPERBOLOID --------------------------

        gui.comboBox(self.hyperboloid_box, self, "calculate_hyperboloid_parameter", label="Hyperboloid Shape", labelWidth=350,
                     items=["Manual", "Automatic"],
                     callback=self.set_HyperboloidShape,
                     sendSelectedValue=False, orientation="horizontal")

        self.hyperboloid_box_1 = oasysgui.widgetBox(self.hyperboloid_box, "", addSpace=False, orientation="vertical", height=60)
        self.hyperboloid_box_2 = oasysgui.widgetBox(self.hyperboloid_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.hyperboloid_box_1, self, "min_ax_surface", "Minor Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.hyperboloid_box_1, self, "maj_ax_surface", "Major Axis [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.hyperboloid_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.hyperboloid_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")


        # TORUS --------------------------

        gui.comboBox(self.torus_box, self, "calculate_torus_parameter", label="Torus Shape", labelWidth=350,
                     items=["Manual", "Automatic"],
                     callback=self.set_TorusShape,
                     sendSelectedValue=False, orientation="horizontal")

        self.torus_box_1 = oasysgui.widgetBox(self.torus_box, "", addSpace=False, orientation="vertical", height=60)
        self.torus_box_2 = oasysgui.widgetBox(self.torus_box, "", addSpace=False, orientation="vertical", height=60)

        oasysgui.lineEdit(self.torus_box_1, self, "min_radius_surface", "Minor radius [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.torus_box_1, self, "maj_radius_surface", "Major radius [m]", labelWidth=260, valueType=float, orientation="horizontal")

        oasysgui.lineEdit(self.torus_box_2, self, "p_surface", "First Focus to O.E. Center (P) [m]", labelWidth=260, valueType=float, orientation="horizontal")
        oasysgui.lineEdit(self.torus_box_2, self, "q_surface", "O.E. Center to Second Focus (Q) [m]", labelWidth=260, valueType=float, orientation="horizontal")

        # -----------------------------------------------------
        # -----------------------------------------------------

        self.surface_orientation_box = oasysgui.widgetBox(tab_oe, "Surface Orientation", addSpace=False, orientation="vertical")

        gui.comboBox(self.surface_orientation_box, self, "convexity", label="Convexity", labelWidth=350,
                     items=["Upward", "Downward"],
                     sendSelectedValue=False, orientation="horizontal")

        gui.comboBox(self.surface_orientation_box, self, "is_cylinder", label="Cylinder", labelWidth=350,
                     items=["No", "Yes"], callback=self.set_Cylinder,
                     sendSelectedValue=False, orientation="horizontal")

        self.cylinder_box_1 = oasysgui.widgetBox(self.surface_orientation_box, "", addSpace=False, orientation="vertical", height=25)
        self.cylinder_box_2 = oasysgui.widgetBox(self.surface_orientation_box, "", addSpace=False, orientation="vertical", height=25)

        gui.comboBox(self.cylinder_box_1, self, "cylinder_direction", label="Cylinder Direction", labelWidth=350,
                     items=["Tangential", "Sagittal"],
                     sendSelectedValue=False, orientation="horizontal")

        self.set_SurfaceParameters()

    def set_SphereShape(self):
        self.sphere_box_1.setVisible(self.calculate_sphere_parameter==0)
        self.sphere_box_2.setVisible(self.calculate_sphere_parameter==1)

    def set_EllipsoidShape(self):
        self.ellipsoid_box_1.setVisible(self.calculate_ellipsoid_parameter==0)
        self.ellipsoid_box_2.setVisible(self.calculate_ellipsoid_parameter==1)

    def set_ParaboloidShape(self):
        self.paraboloid_box_1.setVisible(self.calculate_paraboloid_parameter==0)
        self.paraboloid_box_2.setVisible(self.calculate_paraboloid_parameter==1)

    def set_HyperboloidShape(self):
        self.hyperboloid_box_1.setVisible(self.calculate_hyperboloid_parameter==0)
        self.hyperboloid_box_2.setVisible(self.calculate_hyperboloid_parameter==1)

    def set_TorusShape(self):
        self.torus_box_1.setVisible(self.calculate_torus_parameter==0)
        self.torus_box_2.setVisible(self.calculate_torus_parameter==1)


    def set_Cylinder(self):
        self.cylinder_box_1.setVisible(self.is_cylinder==1)
        self.cylinder_box_2.setVisible(self.is_cylinder==0)

    def set_SurfaceParameters(self):
        self.plane_box.setVisible(self.surface_shape == 0)

        if self.surface_shape == 1 :
            self.sphere_box.setVisible(True)
            self.set_SphereShape()
        else:
            self.sphere_box.setVisible(False)

        if self.surface_shape == 2 :
            self.ellipsoid_box.setVisible(True)
            self.set_EllipsoidShape()
        else:
            self.ellipsoid_box.setVisible(False)

        if self.surface_shape == 3 :
            self.paraboloid_box.setVisible(True)
            self.set_ParaboloidShape()
        else:
            self.paraboloid_box.setVisible(False)

        if self.surface_shape == 4 :
            self.hyperboloid_box.setVisible(True)
            self.set_HyperboloidShape()
        else:
            self.hyperboloid_box.setVisible(False)

        if self.surface_shape == 5 :
            self.torus_box.setVisible(True)
            self.set_TorusShape()
        else:
            self.torus_box.setVisible(False)

        if self.surface_shape in (1,2,3,4):
            self.surface_orientation_box.setVisible(True)
            self.set_Cylinder()
        else:
            self.surface_orientation_box.setVisible(False)

    def get_surface_shape(self):
        if self.surface_shape == 0:
            surface_shape = Plane()

        # SPHERE --------------------------
        elif self.surface_shape == 1:
            if self.calculate_sphere_parameter == 0:
                if self.is_cylinder == 0:
                    surface_shape = Sphere(radius=self.radius_surface,
                                           convexity=self.convexity)
                else:
                    surface_shape = SphericalCylinder(radius=self.radius_surface,
                                                      convexity=self.convexity,
                                                      cylinder_direction=self.cylinder_direction)
            elif self.calculate_sphere_parameter == 1:
                if self.is_cylinder == 0:
                    surface_shape = Sphere(convexity=self.convexity)
                else:
                    surface_shape = SphericalCylinder(convexity=self.convexity,
                                                      cylinder_direction=self.cylinder_direction)

                surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial))

                self.radius_surface = round(surface_shape.get_radius(), 6)

        # ELLIPSOID --------------------------
        elif self.surface_shape == 2:
            if self.calculate_ellipsoid_parameter == 0:
                if self.is_cylinder == 0:
                    surface_shape = Ellipsoid(min_axis=self.min_ax_surface,
                                              maj_axis=self.maj_ax_surface,
                                              convexity=self.convexity)
                else:
                    surface_shape = EllipticalCylinder(min_axis=self.min_ax_surface,
                                                       maj_axis=self.maj_ax_surface,
                                                       convexity=self.convexity,
                                                       cylinder_direction=self.cylinder_direction)
            elif self.calculate_ellipsoid_parameter == 1:
                if self.is_cylinder == 0:
                    surface_shape = Ellipsoid(convexity=self.convexity)
                else:
                    surface_shape = EllipticalCylinder(convexity=self.convexity,
                                                       cylinder_direction=self.cylinder_direction)

                surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial))

                self.min_ax_surface = round(surface_shape._min_axis, 6)
                self.maj_ax_surface = round(surface_shape._maj_axis, 6)

        # PARABOLOID --------------------------
        elif self.surface_shape == 3:
            if self.calculate_paraboloid_parameter == 0:
                if self.is_cylinder == 0:
                    surface_shape = Paraboloid(parabola_parameter=self.parabola_parameter_surface,
                                               convexity=self.convexity)
                else:
                    surface_shape = ParabolicCylinder(parabola_parameter=self.parabola_parameter_surface,
                                                      convexity=self.convexity,
                                                      cylinder_direction=self.cylinder_direction)
            elif self.calculate_paraboloid_parameter == 1:
                if self.is_cylinder == 0:
                    surface_shape = Paraboloid(convexity=self.convexity)
                else:
                    surface_shape = ParabolicCylinder(convexity=self.convexity,
                                                    cylinder_direction=self.cylinder_direction)

                surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial), at_infinity=self.at_infinty_surface)

                self.parabola_parameter_surface = round(surface_shape._parabola_parameter, 6)

        # HYPERBOLOID --------------------------
        elif self.surface_shape == 4:
            if self.calculate_hyperboloid_parameter == 0:
                if self.is_cylinder == 0:
                    surface_shape = Hyperboloid(min_axis=self.min_ax_surface,
                                                maj_axis=self.maj_ax_surface,
                                                convexity=self.convexity)
                else:
                    surface_shape = HyperbolicCylinder(min_axis=self.min_ax_surface,
                                                       maj_axis=self.maj_ax_surface,
                                                       convexity=self.convexity,
                                                       cylinder_direction=self.cylinder_direction)
            elif self.calculate_ellipsoid_parameter == 1:
                raise NotImplementedError("HYPERBOLOID, you should not be here!")

        # TORUS --------------------------
        elif self.surface_shape == 5:
            if self.calculate_torus_parameter == 0:
                surface_shape = Toroid(min_radius=self.min_radius_surface,
                                      maj_radius=self.maj_radius_surface)
            elif self.calculate_torus_parameter == 1:
                surface_shape = Toroid()

                surface_shape.initialize_from_p_q(self.p_surface, self.q_surface, numpy.radians(90-self.angle_radial))

                self.min_radius_surface = round(surface_shape._min_radius, 6)
                self.maj_radius_surface = round(surface_shape._maj_radius, 6)

        return surface_shape

    def check_data(self):
        super().check_data()

        if self.surface_shape == 1: # SPHERE
            if self.calculate_sphere_parameter == 0:
                congruence.checkStrictlyPositiveNumber(self.radius_surface, "(Surface) Radius")
            elif self.calculate_sphere_parameter == 1:
                congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")

        if self.surface_shape == 2: # ELLIPSOID
            if self.calculate_ellipsoid_parameter == 0:
                congruence.checkStrictlyPositiveNumber(self.min_ax_surface, "(Surface) Minor Axis")
                congruence.checkStrictlyPositiveNumber(self.maj_ax_surface, "(Surface) Major Axis")
            elif self.calculate_ellipsoid_parameter == 1:
                congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
                congruence.checkStrictlyPositiveNumber(self.q_surface, "(Surface) Q")

                if self.is_cylinder and self.cylinder_direction == Direction.SAGITTAL:
                    raise NotImplementedError("Sagittal automatic calculation is not supported, yet")

        if self.surface_shape == 3: # PARABOLOID
            if self.calculate_paraboloid_parameter == 0:
                congruence.checkStrictlyPositiveNumber(self.parabola_parameter_surface, "(Surface) Parabola Parameter")
            elif self.calculate_paraboloid_parameter == 1:
                congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
                congruence.checkStrictlyPositiveNumber(self.q_surface, "(Surface) Q")

                if self.is_cylinder and self.cylinder_direction == Direction.SAGITTAL:
                    raise NotImplementedError("Sagittal automatic calculation is not supported, yet")

        if self.surface_shape == 4: # HYPERBOLOID
            if self.calculate_hyperboloid_parameter == 0:
                congruence.checkStrictlyPositiveNumber(self.min_ax_surface, "(Surface) Minor Axis")
                congruence.checkStrictlyPositiveNumber(self.maj_ax_surface, "(Surface) Major Axis")
            elif self.calculate_hyperboloid_parameter == 1:
                raise NotImplementedError("Automatic calculation is not supported, yet")

        if self.surface_shape == 5: # TORUS
            if self.calculate_torus_parameter == 0:
                congruence.checkStrictlyPositiveNumber(self.min_radius_surface, "(Surface) Minor Radius")
                congruence.checkStrictlyPositiveNumber(self.maj_radius_surface, "(Surface) Major Radius")
            elif self.calculate_torus_parameter == 1:
                congruence.checkStrictlyPositiveNumber(self.p_surface, "(Surface) P")
                congruence.checkStrictlyPositiveNumber(self.q_surface, "(Surface) Q")

    def receive_specific_syned_data(self, optical_element):
        super().receive_specific_syned_data(optical_element)

        #TODO: check and passage of shapes

        raise NotImplementedError()

