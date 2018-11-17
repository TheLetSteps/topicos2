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

        self.setWindowTitle("Solicitar Chamadas")

    def createFormGroupBox(self):
        self.formGroupBox = QGroupBox("Solicitar Chamadas")
        layout = QFormLayout()
        

        self.countSimulationsField = QLineEdit()
        self.countSimulationsField.setValidator(QIntValidator(1, 10001))
        
        #self.b1 = QCheckBox("Você tem certeza que deseja calcular?")
        #self.b1.setChecked(True)
        #layout.addRow(self.b1)

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
    
        now = datetime.datetime.now()
        fileSimulationName = 'resultados_simulacao_' + now.strftime("%d-%m-%Y-%H:%M")
        f = open(fileSimulationName + '.txt' ,'w')
        f.write('Numero de chamadas: ' + str(countSimulations) + '\n\n')
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
            
                if rota not in rotas[s_d]:
                    #print('chegou aqui')
                    rotas[s_d].append(rota)
                    #print(rotas[s_d])

                self.currentPath = []
        
                f.write('Simulacao ' + str(countSimulations - leftSimulations + 1) + ':\n')
                f.write('Origem: ' + str((self.index_to_vertex[s].label.text())) + '\n')
                f.write('Destino: ' + str((self.index_to_vertex[d].label.text())) + '\n')
                f.write('Caminho: ' + str(graph.path_to(d, sources[s], self.handleVertices)) + '\n')
                f.write('Distancia: ' + str(sources[s][d].distance) + ' km\n'+'\n')

                #self.firstFit(f)
            else:
                yen_result = graph.ksp_yen(s, d, sources[s])[0]
                sources[s], distance = yen_result['path'], yen_result['cost']

                #print("syen = ",sources[s])

                #path = graph.path(d, sources[s])
                path = self.path_of_vertexes(sources[s]) 
                rota = [int(vertex) for vertex in path.split()]
                #print(f'ROTA: {rota}')
                print(f'ROTA CRIADA: {rota}')
                print(f'ROTAS: {rotas[s_d]}')
                if rota in rotas[s_d]:
                    continue
        
                elif (len(rotas[s_d]) <= 3):
                    
                    f.write('Simulacao ' + str(countSimulations - leftSimulations + 1) + ':\n')
                    f.write('Origem: ' + str((self.index_to_vertex[s].label.text())) + '\n')
                    f.write('Destino: ' + str((self.index_to_vertex[d].label.text())) + '\n')
                    #f.write('Caminho: ' + str(graph.path_to(d, sources[s], self.handleVertices)) + '\n')
                    f.write('Caminho: ' + path + '\n')
                    #f.write('Distancia: ' + str(sources[s][d].distance) + ' km\n'+'\n')
                    f.write('Distancia: ' + str(distance) + 'km\n' + '\n')
                    rotas[s_d].append(rota)

                else:
                    f.write('Simulacao ' + str(countSimulations - leftSimulations + 1) + ':\n')
                    f.write('Origem: ' + str((self.index_to_vertex[s].label.text())) + '\n')
                    f.write('Destino: ' + str((self.index_to_vertex[d].label.text())) + '\n')
                    f.write('Bloqueio!\n\n')
                    self.lostCalls += 1
  
                #continue
                
            leftSimulations -= 1
                
        self.blockingProbability = self.lostCalls / countSimulations
        f.write('Probabilidade de bloqueio: ' + str(self.blockingProbability))
            
        f.close()

        try:
            self.parentApp.showNewMessageDialog('Arquivo do resultado da Simulação criado:  \"' + fileSimulationName + '\"')
        except:
            self.parentApp.showNewMessageDialog('Something went wrong')

    def path_of_vertexes(self, vertex_list):
        path = ""
        print(vertex_list)
        for vertex in vertex_list:
            path += vertex.label + ' '

        path.rstrip()

        return path


            
    def handleVertices(self, u):
        self.currentPath.append(u)
        return str(self.index_to_vertex[u].label.text())
    
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
        self.simulate(False)
        self.close()
        
        

class SimulatorWavelengthDialog(QDialog):
    NumGridRows = 3
    NumButtons = 4

    def __init__(self, parentApp):
        super(SimulatorWavelengthDialog, self).__init__()
        file = str(QFileDialog.getExistingDirectory(self, "Select Directory"))
        
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
