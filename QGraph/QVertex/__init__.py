from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGroupBox, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QMenu
from PyQt5 import QtCore, QtGui
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt

class VertexDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self,textIdField):
        super(VertexDialog, self).__init__()
        self.status = -1
        self.textIdField = textIdField
        self.createFormGroupBox()
        #self.move(clickPos)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.acceptAct)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Criar Vértice")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Criar Vértice")
        layout = QFormLayout()
        # teremos que gerar esses ids
        self.label = QLineEdit()
        self.idField = QLineEdit(str(self.textIdField))
        self.idField.setReadOnly(True)

        layout.addRow(QLabel("ID"), self.idField)
        layout.addRow(QLabel("Nome"), self.label)
        self.formGroupBox.setLayout(layout)

    def acceptAct(self):
        self.buttonBox.accepted.connect(self.accept)
        self.status = 0
        self.close()


class VertexIcon(QLabel):
    class VertexLabel(QLabel):

        MAX_TEXT_SIZE = 120

        def __init__(self, parentWidget, vertexIcon=None, text=None):
            super().__init__(parentWidget)
            self.setText(self.MAX_TEXT_SIZE * ' ')
            self.hide()

            if (vertexIcon is not None and text is not None):
                self.initialize(vertexIcon, text)

        def initialize(self, vertexIcon, text):
            self.parentVertex = vertexIcon
            self.setText(text)
            self.localLabelPosition = QtCore.QPoint(-10, 40)
            self.show()

        def clear(self):
            super().clear()
            self.parentVertex = None
            self.setText(self.MAX_TEXT_SIZE * ' ')
            self.hide()

        @property
        def localLabelPosition(self):
            return self.pos() - self.parentVertex.pos()

        @localLabelPosition.setter
        def localLabelPosition(self, value):
            self.move(self.parentVertex.pos() + value)

        def mousePressEvent(self, event):
            self.__mousePressPos = None
            self.__mouseMovePos = None
            if event.button() == Qt.LeftButton:
                self.__mousePressPos = event.globalPos()
                self.__mouseMovePos = event.globalPos()

            super(VertexIcon.VertexLabel, self).mousePressEvent(event)

        def mouseMoveEvent(self, event):
            if (event.buttons() == Qt.LeftButton):
                # adjust offset from clicked point to origin of widget
                currPos = self.mapToGlobal(self.pos())
                globalPos = event.globalPos()
                diff = globalPos - self.__mouseMovePos
                newPos = self.mapFromGlobal(currPos + diff)

                self.move(newPos)

                self.__mouseMovePos = globalPos

            super(VertexIcon.VertexLabel, self).mouseMoveEvent(event)

        def mouseReleaseEvent(self, event):
            if self.__mousePressPos is not None:
                moved = event.globalPos() - self.__mousePressPos
                if moved.manhattanLength() > 3:
                    event.ignore()
                    return

            super(VertexIcon.VertexLabel, self).mouseReleaseEvent(event)

    def __init__(self, parent, pos=None, label=None):
        super().__init__(parent)
        self.hide()
        self.label = self.VertexLabel(parent)

        if (pos is not None and label is not None):
            self.initialize(pos, label)

    def initialize(self, x, y, label, idVertex):
        self.idVertex = idVertex
        self.move(x, y)
        self.setPixmap(QtGui.QPixmap('Images/server.png'))
        self.setGeometry(QtCore.QRect(x, y, 50, 50))
        self.label.initialize(self, label)
        self.show()

    def clear(self):
        super().clear()
        self.label.clear()
        self.hide()

    @property
    def vertexPosition(self):
        return self.pos()

    @vertexPosition.setter
    def vertexPosition(self, value):
        local = self.label.localLabelPosition
        self.move(value)
        self.label.localLabelPosition = local

    @property
    def vertexCenter(self):
        return self.pos() + QtCore.QPoint(20, 25)

    def edge_already_exists(self, u, v):
        edgeList = self.parent().used_label_edges

        for edge in edgeList:
            if(edge.u == u and edge.v == v or edge.u == v and edge.v == u):
                return True

        return False

    def mousePressEvent(self, event):
        print('right click on vertex')
        self.__mousePressPos = None
        self.__mouseMovePos = None
        if (event.button() == QtCore.Qt.LeftButton):
            self.__mousePressPos = event.globalPos()
            self.__mouseMovePos = event.globalPos()

            u = self.parent().SourceEdgeDrawingVertex

            if (u is not None and u != self and not self.edge_already_exists(u, self)):
                e = self.parent().unused_label_edges.pop()
                e.initialize(u, self, 10)
                self.parent().used_label_edges.add(e)
                self.parent().update()
                self.parent().SourceEdgeDrawingVertex = None

        elif (event.button() == QtCore.Qt.RightButton and self.parent().app_state == self.parent().AppState.DRAWING):
            self.parent().shouldExecuteRightClickAction = False
            self.onVertexRightClick(event.pos())

        super(VertexIcon, self).mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if (event.buttons() == QtCore.Qt.LeftButton):
            # adjust offset from clicked point to origin of widget
            currPos = self.mapToGlobal(self.pos())
            globalPos = event.globalPos()
            diff = globalPos - self.__mouseMovePos
            self.vertexPosition = self.mapFromGlobal(currPos + diff)
            self.__mouseMovePos = globalPos

        super(VertexIcon, self).mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        print('soltou')

        if self.__mousePressPos is not None:
            moved = event.globalPos() - self.__mousePressPos
            if moved.manhattanLength() > 3:
                event.ignore()
                return

        super(VertexIcon, self).mouseReleaseEvent(event)

    def mouseDoubleClickEvent(self, event):
        if(self.parent().app_state == self.parent().AppState.DRAWING):        
            self.parent().editVertex(self)
            super(VertexIcon, self).mouseMoveEvent(event)

    def onVertexRightClick(self, pos):

        cmenu = QMenu(self.parent())
        editAct = cmenu.addAction("Edit Vertex")
        editAct.setIcon(QIcon('Images/edit.png'))

        deleteAct = cmenu.addAction("Delete Vertex")
        deleteAct.setIcon(QIcon('Images/exit.png'))

        addEdgeAct = cmenu.addAction("Add Edge")
        addEdgeAct.setIcon(QIcon('Images/edge.png'))

        action = cmenu.exec_(self.mapToGlobal(pos))

        if action == editAct:
            print('edit')
            self.parent().editVertex(self)
        elif action == deleteAct:
            print('delet')
            self.parent().deleteVertex(self)
        elif action == addEdgeAct:
            self.parent().SourceEdgeDrawingVertex = self
            self.parent().update()
