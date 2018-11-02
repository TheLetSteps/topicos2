from enum import Enum
import copy
import heapq as hp
try:
  from enum import auto
except ImportError: 
  __my_enum_auto_id = 0
  def auto() -> int:
    global __my_enum_auto_id
    i = __my_enum_auto_id
    __my_enum_auto_id += 1
    return i


class Color(Enum):
    WHITE = auto()
    BLACK = auto()
    GRAY = auto()


class Vertex:
    INF = float('inf')

    def __init__(self, label):
        self.__color = Color.WHITE
        self.__label = label
        self.__distance = self.INF
        self.__antecessor = None

    def __str__(self):
        info = 'Label: ' + str(self.__label) + '\n'
        info += 'Color: ' + str(self.__color) + '\n'
        info += 'Distance: ' + str(self.__distance) + '\n'
        info += 'Antecessor: ' + str(self.__antecessor) + '\n'
        return info

    def __lt__(self, other):
        if (isinstance(other, Vertex)):
            return self.__distance < other.distance

    @property
    def color(self):
        return self.__color

    @color.setter
    def color(self, value):
        self.__color = value

    @property
    def label(self):
        return self.__label

    @label.setter
    def label(self, value):
        self.__label = value

    @property
    def distance(self):
        return self.__distance

    @distance.setter
    def distance(self, value):
        self.__distance = value

    @property
    def antecessor(self):
        return self.__antecessor

    @antecessor.setter
    def antecessor(self, value):
        self.__antecessor = value


class Graph:

    def __init__(self, n):
        self.__n = n
        self.__initialize()

    def __str__(self):
        info = ''
        for u in range(self.__n):
            info += str(u) + ': '
            for pair in self.__adj_list[u]:
                info += str(pair) + '  '
            info += "\n"
        return info

    def __initialize(self):
        self.__vertexes = []
        self.__adj_list = []
        self.__source_vertex = None

        for i in range(self.__n):
            self.__vertexes.append(Vertex(i))
            self.__adj_list.append([])

    @property
    def vertexes(self):
        return copy.deepcopy(self.__vertexes)

    def insert_edge(self, u, v, w=1):
        self.__adj_list[u].append((v, w))
        self.__adj_list[v].append((u, w))

    def insert_arc(self, u, v, w=1):
        self.__adj_list[u].append((v, w))

    def remove_edge(self, u, v):
        self.__adj_list[u] = [(_v, _w) for _v, _w in self.__adj_list[u] if _v != v]
        self.__adj_list[v] = [(_u, _w) for _u, _w in self.__adj_list[v] if _u != u]

    def get_remove_edge(self, u, v):
        self.__adj_list[u] = [(_v, _w) for _v, _w in self.__adj_list[u] if _v != v]
        self.__adj_list[v] = [(_u, _w) for _u, _w in self.__adj_list[v] if _u != u]
        peso = -1
        for _u, _w in self.__adj_list[v]:
            if _u != u:
                peso+=_w
        return peso

    def remove_arc(self, u, v):
        self.__adj_list[u] = [(_v, _w) for _v, _w in self.__adj_list[u] if _v != v]

    def clear(self):
        self.__initialize()

    def dijkstra_sssp(self, source_vertex):
        self.__source_vertex = source_vertex

        pq = []

        for v in self.__vertexes:
            v.distance = Vertex.INF
            v.antecessor = None

        self.__vertexes[source_vertex].distance = 0
        hp.heappush(pq, (0, source_vertex))

        while (len(pq)):
            d, u = hp.heappop(pq)

            if (d > self.__vertexes[u].distance):
                continue

            for v, w in self.__adj_list[u]:
                if (self.__vertexes[u].distance + w < self.__vertexes[v].distance):
                    self.__vertexes[v].distance = self.__vertexes[u].distance + w
                    self.__vertexes[v].antecessor = u
                    hp.heappush(pq, (self.__vertexes[v].distance, v))

    def path_source_to(self, destination_vertex):
        if(self.__source_vertex is None):
            return ''

        path_list = []
        self.path_to(destination_vertex, self.__vertexes, lambda u: u)
        return path_list

    def path_to(self, u, vertexes_list, handleVertice):
        if (vertexes_list[u].antecessor is None):
            return str(handleVertice(u))
        return self.path_to(vertexes_list[u].antecessor, vertexes_list, handleVertice) + ' ==> ' + str(handleVertice(u))

    def path(self, u, vertexes_list):
        if (vertexes_list[u].antecessor is None):
            return str(u)
        return self.path(vertexes_list[u].antecessor, vertexes_list) + ' ' + str(u)
    
    def itemgetter(self, dict):
        return dict['cost']

    def ksp_yen(self, node_start, node_end, vertexes_list, max_k=2):
    
        self.dijkstra_sssp(node_start)

        path = self.path(node_end, vertexes_list)
        path = [int(vertex) for vertex in path.split()]
        
        A = [{
            'cost' : self.__vertexes[node_end].distance,
            'path' : path
        }]
        B = []

        if not A[0]['path']: return A

        for k in range(1, max_k):
            for i in range(0, len(A[-1]['path']) - 1):
                node_spur = A[-1]['path'][i]
                path_root = A[-1]['path'][:i+1]

                edges_removed = []
                for path_k in A:
                    curr_path = path_k['path']
                    if len(curr_path) > i and path_root == curr_path[:i+1]:
                        cost = self.get_remove_edge(curr_path[i], curr_path[i+1])
                        if cost == -1:
                            continue
                        edges_removed.append([curr_path[i], curr_path[i+1], cost])

                self.dijkstra_sssp(node_spur)
                path = self.path(node_end, vertexes_list)
                path = [int(vertex) for vertex in path.split()]
                
                path_spur = {
                    #'cost': self.vertexes[node_start][node_end].distance,
                    'cost': self.__vertexes[node_end].distance,
                    'path': path
                    }

                if path_spur['path']:
                    path_total = path_root[:-1] + path_spur['path']
                    dist_total = self.vertexes[node_spur].distance + path_spur['cost']
                    potential_k = {'cost': dist_total, 'path': path_total}

                    if not (potential_k in B):
                        B.append(potential_k)

                for edge in edges_removed:
                    self.insert_edge(edge[0], edge[1], edge[2])

            if len(B):
                B = sorted(B, key=self.itemgetter)
                A.append(B[0])
                B.pop(0)
            else:
                break
        return A
