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
        self.width = 1800
        self.height = 1200
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

        nodeAct = QAction(QIcon('Images/icon.png'), 'Criar vertice', self)
        nodeAct.triggered.connect(self.create_vertex_toolbar)
        nodeAct.setEnabled(True)

        edgeAct = QAction(QIcon('Images/edge.png'), 'Criar aresta', self)
        edgeAct.setEnabled(True)
        edgeAct.triggered.connect(self.create_edge_toolbar)

        self.routeAct = QAction(QIcon('Images/route.png'), 'Calcular rotas', self)
        self.routeAct.setEnabled(True)
        self.routeAct.triggered.connect(self.showSimulatorDialog)

        self.toolbar = self.addToolBar('Exit')
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
            self.showNewMessageDialog('Não é possível criar! Qtd de vértices é menor que dois.')
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
                        self.createEdge(str(u), str(v), self.dialog.label.text())

    def create_vertex(self, x, y, label, idVertex):
        v = self.unused_icon_vertexes.pop()
        self.used_icon_vertexes.add(v)
        v.initialize(x, y, label, idVertex)
        self.createdNodes += 1

    def create_vertex_toolbar(self,  event):
        self.create_vertex(100,100, 'Untitled', self.createdNodes)

    def load_topology(self, fileName):
        file = open(fileName,'r')

        content = file.readlines()
        print(content)
        if content[0]!='0':
            self.createdNodes = int(content[0])
            for i in range (1,int(content[0]) + 1):
                aux = []
                aux = str(content[i]).rstrip().split(' ')
                self.create_vertex(int(aux[0])*100, int(aux[1])*100, str(i), int(aux[2]))
                self.create_edge(aux[0], aux[1], aux[2])

  
    def open_file_name_dialog(self):
        options = QFileDialog.Options()
        options |= QFileDialog.DontUseNativeDialog
        fileName, _ = QFileDialog.getOpenFileName(self,"QFileDialog.getOpenFileName()", "","All Files (*);;Python Files (*.py)", options=options)
        if fileName:
            print(fileName)
            self.fileName = fileName
            self.loadTopology(fileName)	

    def importFile(self):
	    self.open_file_name_dialog()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = App()
    sys.exit(app.exec_())
