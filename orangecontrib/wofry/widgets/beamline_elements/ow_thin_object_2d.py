from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.widget import Input

from oasys2.widget import gui as oasysgui
from oasys2.widget.util import congruence
from oasys2.canvas.util.canvas_util import add_widget_parameters_to_module

from oasys2.widget.util.widget_objects import OasysSurfaceData

from syned.widget.widget_decorator import WidgetDecorator

from orangecontrib.wofry.widgets.gui.ow_optical_element_2d import OWWOOpticalElement2D

from wofryimpl.beamline.optical_elements.refractors.thin_object import WOThinObject

class OWWOThinObject2D(OWWOOpticalElement2D):
    name = "ThinObject"
    description = "Wofry: Thin Object 2D"
    icon = "icons/thinb2d.png"
    priority = 47

    class Inputs:
        wofry_data   = OWWOOpticalElement2D.Inputs.wofry_data
        syned_data   = WidgetDecorator.syned_input_data(multi_input=True)
        surface_data = Input("Surface Data", OasysSurfaceData, id="Surface Data", default=True, auto_summary=False)

    material = Setting(1)
    refraction_index_delta = Setting(5.3e-7)
    att_coefficient = Setting(0.00357382)

    aperture_shape = Setting(0)
    aperture_dimension_v = Setting(100e-6)
    aperture_dimension_h = Setting(200e-6)

    file_with_thickness_mesh = Setting("<none>")

    def __init__(self):

        super().__init__(is_automatic=True, show_view_options=True, show_script_tab=True)

    def draw_specific_box(self):
        self.thinobject_box = oasysgui.widgetBox(self.tab_bas, "Thin Object Setting", addSpace=False, orientation="vertical",
                                           height=350)

        gui.comboBox(self.thinobject_box, self, "material", label="Lens material",
                     items=self.get_material_name(), callback=self.set_visible,
                     sendSelectedValue=False, orientation="horizontal")

        self.box_refraction_index_id = oasysgui.widgetBox(self.thinobject_box, "", addSpace=False, orientation="horizontal")
        tmp = oasysgui.lineEdit(self.box_refraction_index_id, self, "refraction_index_delta", "Refraction index delta",
                          labelWidth=250, valueType=float, orientation="horizontal")
        tmp.setToolTip("refraction_index_delta")

        self.box_att_coefficient_id = oasysgui.widgetBox(self.thinobject_box, "", addSpace=False, orientation="horizontal")
        tmp = oasysgui.lineEdit(self.box_att_coefficient_id, self, "att_coefficient", "Attenuation coefficient [m-1]",
                          labelWidth=250, valueType=float, orientation="horizontal")
        tmp.setToolTip("att_coefficient")



        filein_box = oasysgui.widgetBox(self.thinobject_box, "", addSpace=True,
                                        orientation="horizontal")  # width=550, height=50)
        self.le_beam_file_name = oasysgui.lineEdit(filein_box, self, "file_with_thickness_mesh",
                                                   "File with thickness mesh",
                                                   labelWidth=90, valueType=str, orientation="horizontal")
        gui.button(filein_box, self, "...", callback=self.selectFile)

        self.set_visible()

    def set_visible(self):
        self.box_refraction_index_id.setVisible(self.material in [0])
        self.box_att_coefficient_id.setVisible(self.material in [0])

    def selectFile(self):
        filename = oasysgui.selectFileFromDialog(self,
                previous_file_path=self.file_with_thickness_mesh, message="HDF5 Files (*.hdf5 *.h5 *.hdf)",
                start_directory=".", file_extension_filter="*.*")

        self.le_beam_file_name.setText(filename)

    def get_material_name(self, index=None):
        materials_list = ["External", "Be", "Al", "Diamond"]
        if index is None:
            return materials_list
        else:
            return materials_list[index]

    def get_optical_element(self):
        return WOThinObject(name=self.name,
                    file_with_thickness_mesh=self.file_with_thickness_mesh,
                    material=self.get_material_name(self.material),
                    refraction_index_delta=self.refraction_index_delta,
                    att_coefficient=self.att_coefficient,
                    )

    def check_data(self):
        super().check_data()
        congruence.checkFileName(self.file_with_thickness_mesh)

    @Inputs.wofry_data
    def set_wofry_data(self, wofry_data):
        super(OWWOThinObject2D, self).set_input(wofry_data)

    @Inputs.syned_data
    def set_syned_data(self, index, syned_data):
        super(OWWOThinObject2D, self).receive_syned_data(syned_data)

    @Inputs.syned_data.insert
    def insert_syned_data(self, index, syned_data):
        super(OWWOThinObject2D, self).receive_syned_data(syned_data)

    @Inputs.syned_data.remove
    def remove_syned_data(self, index):
        pass

    def receive_specific_syned_data(self, optical_element):
        pass

    @Inputs.surface_data
    def set_input_surface_data(self, surface_data):
        if isinstance(surface_data, OasysSurfaceData):
           self.file_with_thickness_mesh = surface_data.surface_data_file
        else:
            raise Exception("Wrong surface_data")

    #
    # overwrite this method to add tab with thickness profile
    #

    def initializeTabs(self):
        size = len(self.tab)
        indexes = range(0, size)

        for index in indexes:
            self.tabs.removeTab(size-1-index)

        titles = ["Intensity","Phase","Thickness Profile"]
        self.tab = []
        self.plot_canvas = []

        for index in range(0, len(titles)):
            self.tab.append(gui.createTabPage(self.tabs, titles[index]))
            self.plot_canvas.append(None)

        for tab in self.tab:
            tab.setFixedHeight(self.IMAGE_HEIGHT)
            tab.setFixedWidth(self.IMAGE_WIDTH)


    def do_plot_results(self, progressBarValue=80):
        super().do_plot_results(progressBarValue)
        if not self.view_type == 0:
            if not self.wavefront_to_plot is None:

                self.progressBarSet(progressBarValue)

                xx, yy, zz = self.get_optical_element().get_surface_thickness_mesh(self.input_data.get_wavefront())

                self.plot_data2D(data2D=1e6*zz.T,
                                 dataX=1e6*xx,
                                 dataY=1e6*xx,
                                 progressBarValue=progressBarValue,
                                 tabs_canvas_index=2,
                                 plot_canvas_index=2,
                                 title="O.E. Thickness profile in $\\mu$m",
                                 xtitle="Horizontal [$\\mu$m] ( %d pixels)"%(xx.size),
                                 ytitle="Vertical [$\\mu$m] ( %d pixels)"%(yy.size))

                self.progressBarFinished()

            
add_widget_parameters_to_module(__name__)