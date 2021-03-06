from datetime import datetime, timedelta
import numpy as np
import Graph
from PyQt5.QtWidgets import QDialog, QFileDialog, QDialogButtonBox, QGroupBox, QVBoxLayout, QFormLayout, QLineEdit, QLabel, QCheckBox
from PyQt5.QtGui import QIntValidator

TIME_DURATION = timedelta(milliseconds=10)

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

        self.setWindowTitle("Solicitar Chamadas")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Solicitar Chamadas")
        layout = QFormLayout()
        

        self.countSimulationsField = QLineEdit()
        self.countSimulationsField.setValidator(QIntValidator(1, 10001))
        
        #self.b1 = QCheckBox("Você tem certeza que deseja calcular?")
        #self.b2 = QCheckBox("Rodar First-Fit?")
        #self.b1.setChecked(True)
        #self.b2.setChecked(True)
        
        #layout.addRow(self.b1)
        #layout.addRow(self.b2)
        layout.addRow(QLabel("Nº de Chamadas:"), self.countSimulationsField)
        
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
        rotas={}
        for i in range(self.n):
            sources.append(None)
    
        now = datetime.now()
        fileSimulationName = 'resultados_simulacao_' + now.strftime("%d-%m-%Y-%H:%M")
        f = open(fileSimulationName + '.txt' ,'w')
        f.write('Lambda: ' + str(self.index_to_vertex[0].parent().lambda_) + ' Numero de chamadas: ' + str(countSimulations) + '\n\n')
        leftSimulations = countSimulations
        sorteados_s_d = []

        while(leftSimulations):
            s = np.random.randint(0, self.n)
            d = np.random.randint(0, self.n)
            
            if(d == s):
                continue   

            s_d = (s,d)
            

            if s_d not in sorteados_s_d:
                sorteados_s_d.append(s_d)
                rotas[s_d] = []
                #print(s_d)
                #print(rotas[s_d])                          
            
            if(sources[s] is None):
                graph.dijkstra_sssp(s)
                sources[s] = graph.vertexes
                #print("sdi = ",sources[s])
                path = graph.path(d, sources[s])
                rota = [int(vertex) for vertex in path.split()]
            
            self.currentPath = []
    
            f.write('Simulacao ' + str(countSimulations - leftSimulations + 1) + ':\n')
            f.write('Origem: ' + str((self.index_to_vertex[s].label.text())) + '\n')
            f.write('Destino: ' + str((self.index_to_vertex[d].label.text())) + '\n')
            f.write('Caminho: ' + str(graph.path_to(d, sources[s], self.handleVertices)) + '\n')
            f.write('Distancia: ' + str(sources[s][d].distance) + ' km\n'+'\n')
            
            self.firstFit(f)
            
            leftSimulations -= 1
                
        self.blockingProbability = self.lostCalls / countSimulations
        f.write('Probabilidade de bloqueio (first fit): ' + str(self.blockingProbability))
            
        f.close()

        try:
            self.parentApp.showNewMessageDialog('Arquivo do resultado da Simulação criado:  \"' + fileSimulationName + '\"')
        except:
            self.parentApp.showNewMessageDialog('Something went wrong')
            
    def handleVertices(self, u):
        self.currentPath.append(u)
        return str(self.index_to_vertex[u].label.text())

    def turnOffBit(self,n,k):
        return (n & ~(1 << (k - 1)))
    
    def firstFit(self, f):
        index, used = self.channelToBeUsed()
        pathLength = len(self.currentPath)

        f.write('Canal usado: ')
        
        if(index != -1):
            for i in range(1, pathLength):
                u = self.index_to_vertex[self.currentPath[i-1]]
                v = self.index_to_vertex[self.currentPath[i]]
                self.links[u][v].channels |= (1 << index)
            f.write(str(index+1) + '\n')

        else:
            self.lostCalls += 1
            f.write('Bloqueio!\n\n')
        
        f.write('Canais ocupados no caminho até o momento: ' + str(self.usedChannels(used)) + '\n\n')
    
    def usedChannels(self, n):
        usedList = []
        
        while(n):
            x = n & -n
            usedList.append(x.bit_length())
            n -= x
            
        return usedList
        
    
    def channelToBeUsed(self):
        pathLength = len(self.currentPath)
        lambda_ = self.index_to_vertex[0].parent().lambda_
        used = 0
        count = 1
        
        for i in range(1, pathLength):
            u = self.index_to_vertex[self.currentPath[i-1]]
            v = self.index_to_vertex[self.currentPath[i]]
            link = self.links[u][v]
            used |= link.channels
            print(used)
        if used == 1023 and count < 2:
            used = 0
            count +=1
            
        x = used^(used+1)
        
        if(x > ((1 << lambda_)-1)):
            return (-1, used)
        
        index = x.bit_length() - 1
        return (index, used)
        
    def acceptAct(self):
        self.accept()
        #if(self.b1.isChecked()):
        self.simulate(True)
            #self.simulate(self.b2.isChecked())
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

        self.setWindowTitle("Configuração de Comprimento de Onda")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Comprimento de Onda")
        layout = QFormLayout()
        # teremos que gerar esses ids
        self.countLambdasField = QLineEdit(str(self.parentApp.lambda_ ))
        self.countLambdasField.setValidator(QIntValidator(1, 100000))

        layout.addRow(QLabel("Número de Lambdas"), self.countLambdasField)
        self.formGroupBox.setLayout(layout)
               
    def acceptAct(self):
        self.accept()
        self.close()
