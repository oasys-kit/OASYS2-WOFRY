from typing import List, Any
from collections import namedtuple

from PyQt5.QtWidgets import QMessageBox, QTreeView, QAbstractItemView
from PyQt5.QtGui import QPalette, QColor, QFont, QStandardItemModel, QStandardItem
from PyQt5.QtCore import Qt, QSortFilterProxyModel, pyqtSignal, QModelIndex

from orangewidget import gui
from orangewidget.settings import Setting
from orangewidget.widget import MultiInput, Output

from oasys2.widget.widget import OWAction, OWWidget
from oasys2.widget import gui as oasysgui
from oasys2.widget.util import congruence
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
        wofry_data = MultiInput("WofryData", WofryData, default=True, auto_summary=False)

    class Outputs:
        wofry_data_1D = Output("WofryData", WofryData, id="WofryData", default=True, auto_summary=False)

    want_main_area=0
    want_control_area = 1

    input_wavefront = []

    use_weights = Setting(0)

    weights_input_wavefront = Setting([[1.0, 0.0]])

    HEADER_SCHEMA = [
        ['index', {'label': 'Index'}],
        ['weight', {'label': 'Weight'}],
        ['phase', {'label': 'Phase'}],
    ]  # type: List[str, dict]

    def __init__(self):
        super().__init__()

        self._header_labels = [header['label'] for _, header in self.HEADER_SCHEMA]
        self._header_index  = namedtuple('_header_index', [info_tag for info_tag, _ in self.HEADER_SCHEMA])
        self.view_header    = self._header_index(*[index for index, _ in enumerate(self._header_labels)])

        self.runaction = OWAction("Merge Wavefronts", self)
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

        self.weights_view = oasysgui.TreeViewWithReturn(
            sortingEnabled=True,
            selectionMode=QTreeView.SingleSelection,
            alternatingRowColors=True,
            rootIsDecorated=False,
            editTriggers=QTreeView.NoEditTriggers,
            uniformRowHeights=True,
            toolTip="Press Return or double-click to send"
        )
        self.weights_view.setModel(QSortFilterProxyModel())
        self.weights_view.setItemDelegate(oasysgui.UniformHeightDelegate(self))
        self.weights_view.setItemDelegateForColumn(self.view_header.index, oasysgui.NumericalDelegate(self))
        self.weights_view.setItemDelegateForColumn(self.view_header.weight, oasysgui.NumericalDelegate(self))
        self.weights_view.setItemDelegateForColumn(self.view_header.phase,  oasysgui.NumericalDelegate(self))

        weight_box.layout().addWidget(self.weights_view)

    def __check_wofry_data(self, wofry_data):
        try:
            _ = wofry_data.get_wavefront().get_complex_amplitude().shape
            return True
        except:
            QMessageBox.critical(self, "Error", "Wrong Input Data Format", QMessageBox.Ok)
            return False

    @Inputs.wofry_data
    def set_wavefront(self, index, wofry_data):
        self.input_wavefront[index] = wofry_data
        self.refresh_view()

    @Inputs.wofry_data.insert
    def insert_wavefront(self, index, wofry_data):
        node_link = self.getNodeLinks()[index]

        print(node_link.__dict__)

        self.input_wavefront.insert(index, wofry_data)
        self.weights_input_wavefront.insert(index, [1.0, 0.0])
        self.refresh_view()

    @Inputs.wofry_data.remove
    def remove_wavefront(self, index):
        self.input_wavefront.pop(index)
        self.weights_input_wavefront.pop(index)
        self.refresh_view()

    def refresh_view(self):
        class TreeModel(QStandardItemModel):
            data_changed = pyqtSignal(QModelIndex, float)

            def setData(self, index, value, role=Qt.EditRole):
                if role == Qt.EditRole:
                    item = self.itemFromIndex(index)
                    if item:
                        item.setData(value, Qt.EditRole)
                        self.data_changed.emit(index, value)  # Emit signal to notify view
                        return True

                return super().setData(index, value, role)

        model = TreeModel(self)
        model.data_changed.connect(self.update_weigths)
        model.setHorizontalHeaderLabels(self._header_labels)

        for i in range(len(self.input_wavefront)):
            item0 = QStandardItem()
            item0.setData(i+1, Qt.DisplayRole)
            item1 = QStandardItem()
            item1.setData(self.weights_input_wavefront[i][0], Qt.EditRole)
            item1.setFlags(item1.flags() | Qt.ItemIsEditable)
            item2 = QStandardItem()
            item2.setData(self.weights_input_wavefront[i][1], Qt.EditRole)
            item2.setFlags(item1.flags() | Qt.ItemIsEditable)

            model.appendRow([item0, item1, item2])

        self.weights_view.model().setSourceModel(model)

        self.weights_view.setColumnWidth(0, 40)
        self.weights_view.setColumnWidth(1, 150)
        self.weights_view.setColumnWidth(2, 150)
        self.weights_view.setEditTriggers(QAbstractItemView.DoubleClicked | QAbstractItemView.SelectedClicked)

        self.weights_view.setEnabled(self.use_weights)

    def update_weigths(self, index, value):
        self.weights_input_wavefront[index.row()][index.column()] = float(value)

    def merge_wavefronts(self):
        return

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

        self.send("WofryData", merged_wavefront)

    def set_UseWeights(self):
        self.weights_view.setEnabled(self.use_weights == 1 and not len(self.input_wavefront)==0)


add_widget_parameters_to_module(__name__)
