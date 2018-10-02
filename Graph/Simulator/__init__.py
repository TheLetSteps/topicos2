import datetime
import numpy as np
import Graph
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QGroupBox, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QCheckBox
from PyQt5.QtGui import QIntValidator

class SimulatorDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, parentApp, n, used_label_edges):
        super(SimulatorDialog, self).__init__()
        #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        self.parentApp = parentApp
        self.move(500, 250)
        
        self.used_label_edges = used_label_edges
        self.n = n
        self.createFormGroupBox()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.acceptAct)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Simulator Setup")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Simulator Setup")
        layout = QFormLayout()
        # teremos que gerar esses ids
        self.countSimulationsField = QLineEdit()
        self.countSimulationsField.setValidator(QIntValidator(1, 10001))
        
        self.b1 = QCheckBox("Djikstra")
        self.b2 = QCheckBox("First-Fit")
        self.b1.setChecked(True)
        self.b2.setChecked(True)
        
        layout.addRow(self.b1)
        layout.addRow(self.b2)
        layout.addRow(QLabel("Number of calls"), self.countSimulationsField)
        
        self.formGroupBox.setLayout(layout)
        
    def simulate(self, firstFit):
        
        countSimulations = int(self.countSimulationsField.text())

        if countSimulations < 1:
            return
        
        graph = Graph.Graph(self.n)
        
        self.lostCalls = 0
        self.vertex_to_index = {}
        self.index_to_vertex = list(range(self.n))
        self.links = {}
        countVertexes = 0
    
        for edge in self.used_label_edges:
            if(edge.u not in self.vertex_to_index):
                self.vertex_to_index[edge.u] = countVertexes
                self.index_to_vertex[countVertexes] = edge.u
                self.links[edge.u] = {}
                countVertexes += 1
    
            if(edge.v not in self.vertex_to_index):
                self.vertex_to_index[edge.v] = countVertexes
                self.index_to_vertex[countVertexes] = edge.v
                self.links[edge.v] = {}
                countVertexes += 1
    
            self.links[edge.u][edge.v] = self.links[edge.v][edge.u] = edge
            
            u = self.vertex_to_index[edge.u]
            v = self.vertex_to_index[edge.v]
            graph.insert_edge(u, v, edge.w)
    
        sources = []
        for i in range(self.n):
            sources.append(None)
    
        now = datetime.datetime.now()
        fileSimulationName = 'SimulaÃ§Ã£o - ' + now.strftime("%d-%m-%Y - %Hh%Mm%Ss")
        f = open(fileSimulationName + '.txt' ,'w')
        f.write('Lambda: ' + str(self.index_to_vertex[0].parent().lambda_) + ' Numero de chamadas: ' + str(countSimulations) + '\n\n')
        leftSimulations = countSimulations
        
        while(leftSimulations):
            s = np.random.randint(0, self.n)
            d = np.random.randint(0, self.n)
    
            if(d == s):
                continue
    
            if(sources[s] is None):
                graph.dijkstra_sssp(s)
                sources[s] = graph.vertexes
            
            self.currentPath = []
    
            f.write('SimulaÃ§Ã£o ' + str(countSimulations - leftSimulations + 1) + ':\n')
            f.write('Origem: ' + str((self.index_to_vertex[s].idVertex, self.index_to_vertex[s].label.text())) + '\n')
            f.write('Destino: ' + str((self.index_to_vertex[d].idVertex, self.index_to_vertex[d].label.text())) + '\n')
            f.write('Caminho: ' + str(graph.path_to(d, sources[s], self.handleVertices)) + '\n')
            f.write('DistÃ¢ncia: ' + str(sources[s][d].distance) + ' km\n')
            
            self.firstFit(f)
            
            leftSimulations -= 1
            
        self.blockingProbability = self.lostCalls / countSimulations
        f.write('Probabilidade de bloqueio (first fit): ' + str(self.blockingProbability))
            
        f.close()

        try:
            self.parentApp.showNewMessageDialog('Simulation file created successfully with name \"' + fileSimulationName + '\"')
        except:
            print('Something went wrong')
            
    def handleVertices(self, u):
        self.currentPath.append(u)
        return str((self.index_to_vertex[u].idVertex, self.index_to_vertex[u].label.text()))
    
    def firstFit(self, f):
        index, used = self.channelToBeUsed()
        pathLength = len(self.currentPath)

        f.write('Canal usado: ')
        
        if(index != -1):
            for i in range(1, pathLength):
                u = self.index_to_vertex[self.currentPath[i-1]]
                v = self.index_to_vertex[self.currentPath[i]]
                self.links[u][v].channels |= (1 << index)
            f.write(str(index) + '\n')
        else:
            self.lostCalls += 1
            f.write('Bloqueio!\n\n')
        
        f.write('Canais ocupados no caminho: ' + str(self.usedChannels(used)) + '\n\n')
    
    def usedChannels(self, n):
        usedList = []
        
        while(n):
            x = n & -n
            usedList.append(x.bit_length()-1)
            n -= x
            
        return usedList
        
    
    def channelToBeUsed(self):
        pathLength = len(self.currentPath)
        lambda_ = self.index_to_vertex[0].parent().lambda_
        used = 0
        
        for i in range(1, pathLength):
            u = self.index_to_vertex[self.currentPath[i-1]]
            v = self.index_to_vertex[self.currentPath[i]]
            link = self.links[u][v]
            used |= link.channels
            
            
        x = used^(used+1)
        
        if(x > ((1 << lambda_)-1)):
            return (-1, used)
        
        index = x.bit_length() - 1
        return (index, used)
        
    def acceptAct(self):
        self.accept()
        if(self.b1.isChecked()):
            self.simulate(self.b2.isChecked())
        self.close()
        
        

class SimulatorWavelengthDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, parentApp):
        super(SimulatorWavelengthDialog, self).__init__()
        #file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
        self.parentApp = parentApp
        self.move(500, 250)
        
        self.createFormGroupBox()

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self.buttonBox.accepted.connect(self.acceptAct)
        self.buttonBox.rejected.connect(self.reject)

        mainLayout = QVBoxLayout()
        mainLayout.addWidget(self.formGroupBox)
        mainLayout.addWidget(self.buttonBox)
        self.setLayout(mainLayout)

        self.setWindowTitle("Wavelength Setup")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Wavelength")
        layout = QFormLayout()
        # teremos que gerar esses ids
        self.countLambdasField = QLineEdit(str(self.parentApp.lambda_ ))
        self.countLambdasField.setValidator(QIntValidator(1, 100))

        layout.addRow(QLabel("Number of Lambdas"), self.countLambdasField)
        self.formGroupBox.setLayout(layout)
               
    def acceptAct(self):
        self.accept()
        self.close()