from qtpy import QtCore, QtGui
from qtpy.QtWidgets import QComboBox, QCompleter


class EnumComboBox(QComboBox):
    changeCallback = QtCore.Signal(str)
    textChangedCallback = QtCore.Signal(str)

    def __init__(self, values=None, parent=None):
        super(EnumComboBox, self).__init__(parent)

        if values is None:
            values = []
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setEditable(True)
        self.completer = QCompleter(self)

        # always show all completions
        self.completer.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.pFilterModel = QtCore.QSortFilterProxyModel(self)
        self.pFilterModel.setFilterCaseSensitivity(QtCore.Qt.CaseInsensitive)

        # self.setInsertPolicy(self.NoInsert)

        self.completer.setPopup(self.view())

        self.setCompleter(self.completer)

        self.lineEdit().textEdited[str].connect(self.onTextEdited)
        self.completer.activated.connect(self.setTextIfCompleterIsClicked)

        self.model = QtGui.QStandardItemModel()
        for i, value in enumerate(values):
            item = QtGui.QStandardItem(value)
            self.model.setItem(i, 0, item)
        self.setModel(self.model)
        self.setModelColumn(0)
        self.currentIndexChanged.connect(self.onIndexChanged)

    def onTextEdited(self, text):
        self.pFilterModel.setFilterFixedString(text)
        self.textChangedCallback.emit(text)

    def onReturnPressed(self):
        self.changeCallback.emit(self.currentText())

    def onIndexChanged(self, index):
        self.changeCallback.emit(self.currentText())

    def setModel(self, model):
        super(EnumComboBox, self).setModel(model)
        self.pFilterModel.setSourceModel(model)
        self.completer.setModel(self.pFilterModel)

    def setModelColumn(self, column):
        self.completer.setCompletionColumn(column)
        self.pFilterModel.setFilterKeyColumn(column)
        super(EnumComboBox, self).setModelColumn(column)

    def view(self):
        return self.completer.popup()

    def index(self):
        return self.currentIndex()

    def setTextIfCompleterIsClicked(self, text):
        if text:
            index = self.findText(text)
            self.setCurrentIndex(index)


if __name__ == "__main__":
    import sys
    from qtpy.QtWidgets import QApplication

    a = QApplication(sys.argv)

    def clb(string):
        print(string)

    w = EnumComboBox(["A", "B", "TEST"])
    w.setEditable(False)
    w.changeCallback.connect(clb)

    w.show()

    sys.exit(a.exec_())
