import sys
import ast
import os
from PyQt5 import QtCore
from PyQt5.QtGui import *
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QIcon, QPainter, QPen
from PyQt5.QtCore import Qt
from enum import Enum
from QGraph import QEdge, QVertex
from Graph import Simulator
import random

try:
  from enum import auto
except ImportError: 
  __my_enum_auto_id = 0
  def auto() -> int:
    global __my_enum_auto_id
    i = __my_enum_auto_id
    __my_enum_auto_id += 1
    return i


class App(QMainWindow):
    
    class AppState(Enum):
        DEFAULT = auto()
        NODE = auto()
        EDGE = auto()
        DRAWING = auto()
        SAVING = auto()
        EDITING = auto()    
    
    MAX_VERTEXES = 100
    count_id = 0
 
    def __init__(self):
        super().__init__()

        scriptDir = os.path.dirname(os.path.realpath(__file__))

        self.app_state = App.AppState.DEFAULT
        self.shouldExecuteRightClickAction = True
        self.title = 'Grafo'
        self.left = 100
        self.top = 100
        self.width = 1500
        self.height = 1100
        self.v = 0
        self.init_interface()
        
    
    def init_interface(self):
        
        p = self.palette()
        p.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(p)
        
        self.mouseTrackingPosition = self.pos()
        self.SourceEdgeDrawingVertex = None

        self.unused_icon_vertexes = set()
        self.used_icon_vertexes = set()
        
        self.unused_label_edges = set()
        self.used_label_edges = set()
        
        self.createdNodes = 0
        self.lambda_ = 0
        self.fileName = None
        
        for i in range(self.MAX_VERTEXES):
            self.unused_icon_vertexes.add(QVertex.VertexIcon(self))
        
        self.MAX_EDGES = (self.MAX_VERTEXES * (self.MAX_VERTEXES - 1))//2
        
        for i in range(self.MAX_EDGES):
            self.unused_label_edges.add(QEdge.EdgeLabel(self))
        
        self.setWindowTitle(self.title)
        self.setGeometry(self.left, self.top, self.width, self.height)

        importAct = QAction(QIcon('Images/import.png'),'&Import', self)
        importAct.triggered.connect(self.importFile)

        nodeAct = QAction(QIcon('Images/vertex.jpeg'), 'Criar vertice', self)
        nodeAct.triggered.connect(self.create_vertex_toolbar)
        nodeAct.setEnabled(True)

        edgeAct = QAction(QIcon('Images/line.jpeg'), 'Criar aresta', self)
        edgeAct.setEnabled(True)
        edgeAct.triggered.connect(self.create_edge_toolbar)

        self.routeAct = QAction(QIcon('Images/route.jpeg'), 'Calcular rotas', self)
        self.routeAct.setEnabled(True)
        self.routeAct.triggered.connect(self.showSimulatorDialog)

        self.toolbar = self.addToolBar('Exit')
        self.toolbar.addAction(importAct)
        self.toolbar.addAction(nodeAct)
        self.toolbar.addAction(edgeAct)
        self.toolbar.addAction(self.routeAct)


        self.show()


    def showSimulatorDialog(self):
        self.dialog = Simulator.SimulatorDialog(self, len(self.used_icon_vertexes), self.used_label_edges)
        self.dialog.exec_()

    def create_edge(self, u, v, w):
        vertex_u = None
        vertex_v = None
        print(u, v)
        e = self.unused_label_edges.pop()
        for vertex in self.used_icon_vertexes:
            if vertex.idVertex==int(u):
                vertex_u = vertex
            elif vertex.idVertex==int(v):
                vertex_v = vertex
            e.initialize(vertex_u, vertex_v, ast.literal_eval(w))
            self.used_label_edges.add(e)   



    def create_edge_toolbar(self, event):
        if (len(self.used_icon_vertexes) < 2):
            self.showNewMessageDialog('Não é possível criar! Quantidade de vértices é menor que dois.')
        else:
            idVertexList = []
            labelVertexList = []
            for v in self.used_icon_vertexes:
                idVertexList.append(v.idVertex)
                labelVertexList.append(v.label.text())

            self.dialog = QEdge.CreateEdgeDialog(labelVertexList)
            self.dialog.exec_()

            if self.dialog.status == 0:
                u = idVertexList[self.dialog.u.currentIndex()]
                v = idVertexList[self.dialog.v.currentIndex()]
                print(u, v)
                if (u == v):
                    self.showNewMessageDialog('Não é possível criar aresta. Vértices iguais.')
                else:
                    existentEdge = False
                    for edge in self.used_label_edges:
                        c1 = edge.u.idVertex == u and edge.v.idVertex == v
                        c2 = edge.u.idVertex == v and edge.v.idVertex == u
                        if (c1 or c2):
                            existentEdge = True

                    if (existentEdge):
                        self.showNewMessageDialog('Não é possível criar aresta. Aresta já existe.')
                    else:
                        self.create_edge(str(u), str(v), self.dialog.label.text())

    def create_vertex(self, x, y, label, idVertex):
        v = self.unused_icon_vertexes.pop()
        self.used_icon_vertexes.add(v)
        v.initialize(x, y, label, idVertex)
        self.createdNodes += 1

    def create_vertex_toolbar(self, event):
        aux = self.createVertexDialog(self.createdNodes)
        if(aux[0]==0):
            self.create_vertex(random.randint(0,self.width),random.randint(0,self.height),aux[1],self.createdNodes)


    def createVertexDialog(self, idField=None):
        self.dialog = QVertex.VertexDialog(idField)
        self.dialog.exec_()
        l = []
        l.append(self.dialog.status)
        l.append(self.dialog.label.text())
        l.append(self.dialog.idField.text())
        
        return(l)

    def load_topology(self, fileName):
        global hasImport
        if not hasImport:
            file = open(fileName,'r')

            content = file.readlines()
            nVertex, nEdges = content[0].rstrip().split()

            for i in range(1,int(nVertex)+1):
                self.create_vertex(random.randint(0,self.width)-100,random.randint(0,self.height)-100,str(i),str(i))

            for j in range(1,int(nEdges)+1):
                vertex,neighbor,weight = content[j].rstrip().split()
                self.create_edge(vertex,neighbor,weight)

            hasImport = True
            self.createdNodes += 1
  
    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            self.fileName = fileName
            self.load_topology(fileName)	

    def importFile(self):
        global hasImport
        if not hasImport:
            self.open_file_name_dialog()
        else:
            self.showNewMessageDialog('Já foi importado uma topologia')

    def showNewMessageDialog(self, mensagem):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(mensagem)
        msg.setWindowTitle("Simulador")
        msg.setStandardButtons(QMessageBox.Ok)
        
        msg.exec_()

    def paintEvent(self, e):
        qp = QPainter()
        qp.begin(self)
        
        self.drawEdges(qp)
        
        #if(self.SourceEdgeDrawingVertex is not None):
        #    self.drawEdgeFollower(qp)
        qp.end()

    '''
    def drawEdgeFollower(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        pen.setStyle(Qt.SolidLine)
        qp.setPen(pen)
        qp.drawLine(self.SourceEdgeDrawingVertex.vertexCenter, self.mouseTrackingPosition)
        self.update()
    '''
        
    def drawEdges(self, qp):
        pen = QPen(Qt.black, 2, Qt.SolidLine)
        pen.setStyle(Qt.SolidLine)
        qp.setPen(pen)
        
        for edge in self.used_label_edges:
            qp.drawLine(edge.u.vertexCenter, edge.v.vertexCenter)
            edge.updateCenterPosition()
            self.update()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
