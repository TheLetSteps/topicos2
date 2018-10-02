from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGroupBox, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QComboBox, QMenu
from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QDoubleValidator, QIcon
from PyQt5 import QtCore, QtGui

class EdgeDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, clickPos):
        super(EdgeDialog, self).__init__()
        self.status = -1
        self.createFormGroupBox()
        self.move(clickPos)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.acceptAct)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Aresta")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Edge Setup")
        layout = QFormLayout()
        # teremos que gerar esses ids
        self.label = QLineEdit()
        self.label.setValidator(QDoubleValidator(0, 1000000, 6))

        layout.addRow(QLabel("Distância"), self.label)
        self.formGroupBox.setLayout(layout)

    def acceptAct(self):
        self.buttonBox.accepted.connect(self.accept)
        self.status = 0
        self.close()


class EdgeLabel(QLabel):
    MAX_TEXT_SIZE = 50

    def __init__(self, parentWidget, u=None, v=None, w=None):
        super().__init__(parentWidget)
        self.setText(self.MAX_TEXT_SIZE * ' ')
        self.hide()
        self.localLabelPosition = self.pos()

        if (u is not None and v is not None and w is not None):
            self.initialize(u, v, w)

    def initialize(self, u, v, w):
        self.u = u
        self.v = v
        self.w = w
        self.channels = 0
        self.setText(str(w) + ' Km')
        self.localLabelPosition = QPoint(0, 0)
        self.show()

    def clear(self):
        super().clear()
        self.u = None
        self.v = None
        self.w = None
        self.hide()

    @property
    def centerPosition(self):
        if (self.u is not None and self.v is not None):
            return (self.u.vertexCenter + self.v.vertexCenter) / 2

    def updateCenterPosition(self):
        self.move(self.centerPosition + self.localLabelPosition)

    def mouseDoubleClickEvent(self, event):
        if(self.parent().app_state == self.parent().AppState.DRAWING):
            self.parent().editEdge(self)
        
    def mousePressEvent(self, event):
        print('right click on edge')

        if(event.button() == QtCore.Qt.RightButton and self.parent().app_state == self.parent().AppState.DRAWING):
            self.parent().shouldExecuteRightClickAction = False
            self.onEdgeRightClick(event.pos())
        
    def onEdgeRightClick(self, pos):

        cmenu = QMenu(self.parent())
        editAct = cmenu.addAction("Edit Edge")
        editAct.setIcon(QIcon('Images/edit.png'))

        deleteAct = cmenu.addAction("Delete Edge")
        deleteAct.setIcon(QIcon('Images/exit.png'))
        
        action = cmenu.exec_(self.mapToGlobal(pos))

        if action == editAct:
            print('edit')
            self.parent().editEdge(self)
        elif action == deleteAct:
            print('delet')
            self.deleteEdge()
            
    def deleteEdge(self):        
        self.parent().used_label_edges.remove(self)
        self.parent().unused_label_edges.add(self)
        self.clear()

class CreateEdgeDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, vertexList):
        super(CreateEdgeDialog, self).__init__()
        self.status = -1
        self.vertexList = vertexList
        self.createFormGroupBox()
        self.move(500, 250)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.acceptAct)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Edge")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Nova Aresta")
        
        layout = QFormLayout()
        self.u = QComboBox()
        self.u.addItems(self.vertexList)
        self.v = QComboBox()
        self.v.addItems(self.vertexList)
        self.label = QLineEdit()
        self.label.setText('10')
        
        layout.addRow(QLabel('De'), self.u)
        layout.addRow(QLabel('Para'), self.v)
        layout.addRow(QLabel("Distância"), self.label)
        
        self.formGroupBox.setLayout(layout)

    def acceptAct(self):
        self.buttonBox.accepted.connect(self.accept)
        self.status = 0
        self.close()
