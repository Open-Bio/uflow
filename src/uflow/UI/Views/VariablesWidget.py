import json

from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QListWidget, QListWidgetItem, QWidget, QAbstractItemView

from uflow.UI.EditorHistory import EditorHistory
from uflow.UI.Canvas.UIVariable import UIVariable
from uflow.UI.Views.VariablesWidget_ui import Ui_Form
from uflow.Core.Common import *

VARIABLE_TAG = "VAR"
VARIABLE_DATA_TAG = "VAR_DATA"


class VariablesListWidget(QListWidget):
    """docstring for VariablesListWidget."""

    def __init__(self, parent=None):
        super(VariablesListWidget, self).__init__(parent)
        self.setDragDropMode(QAbstractItemView.InternalMove)
        self.setDefaultDropAction(QtCore.Qt.MoveAction)
        self.setSelectionMode(QAbstractItemView.SingleSelection)
        self.setSelectionRectVisible(True)

    def mousePressEvent(self, event):
        super(VariablesListWidget, self).mousePressEvent(event)
        w = self.itemWidget(self.currentItem())
        if w:
            drag = QtGui.QDrag(self)
            mime_data = QtCore.QMimeData()
            varJson = w.serialize()
            dataJson = {VARIABLE_TAG: True, VARIABLE_DATA_TAG: varJson}
            mime_data.setText(json.dumps(dataJson))
            drag.setMimeData(mime_data)
            drag.exec_()


class VariablesWidget(QWidget, Ui_Form):
    """docstring for VariablesWidget"""

    def __init__(self, uflowInstance, parent=None):
        super(VariablesWidget, self).__init__(parent)
        self.setupUi(self)
        self.uflowInstance = uflowInstance
        self.uflowInstance.graphManager.get().graphChanged.connect(self.onGraphChanged)
        self.pbNewVar.clicked.connect(lambda: self.createVariable())
        self.listWidget = VariablesListWidget()
        self.lytListWidget.addWidget(self.listWidget)
        self.uflowInstance.newFileExecuted.connect(self.actualize)

    def actualize(self):
        self.clear()
        # populate current graph
        graph = self.uflowInstance.graphManager.get().activeGraph()
        if graph:
            for var in graph.getVarList():
                self.createVariableWrapperAndAddToList(var)

    def onGraphChanged(self, *args, **kwargs):
        self.actualize()

    def clear(self):
        """Does not remove any variable. UI only"""
        self.listWidget.clear()

    def killVar(self, uiVariableWidget):
        variableGraph = uiVariableWidget._rawVariable.graph
        variableGraph.killVariable(uiVariableWidget._rawVariable)
        self.actualize()

        self.clearProperties()
        EditorHistory().saveState("Kill variable", modify=True)

    def createVariableWrapperAndAddToList(self, rawVariable):
        uiVariable = UIVariable(rawVariable, self)
        item = QListWidgetItem(self.listWidget)
        item.setSizeHint(QtCore.QSize(60, 20))
        self.listWidget.setItemWidget(item, uiVariable)
        return uiVariable

    def createVariable(
        self, dataType="AnyPin", accessLevel=AccessLevel.public, uid=None
    ):
        print(dataType)
        rawVariable = (
            self.uflowInstance.graphManager.get()
            .activeGraph()
            .createVariable(dataType=dataType, accessLevel=accessLevel, uid=uid)
        )
        uiVariable = self.createVariableWrapperAndAddToList(rawVariable)
        EditorHistory().saveState("Create variable", modify=True)
        return uiVariable

    def clearProperties(self):
        self.uflowInstance.onRequestClearProperties()

    def onUpdatePropertyView(self, uiVariable):
        self.uflowInstance.onRequestFillProperties(uiVariable.createPropertiesWidget)
