from queue import PriorityQueue as PriorityQueue

inf = float("inf")
global dist,path,pred

def makePath(source,destiny):

	path.append(destiny)

	if source == destiny:
		path.reverse()
		return None
	else:
		makePath(source, pred[destiny])


def dijkstra(graph, source):

	pq = PriorityQueue()

	pq.put((dist[source],source))

	while(not pq.empty()):
		distance, vertex = pq.get()

		for neighbor,weight in graph[vertex]:
			
			if dist[vertex] + weight < dist[neighbor]:
				dist[neighbor] = dist[vertex] + weight
				pred[neighbor] = vertex

				pq.put((dist[neighbor], neighbor))



n,m = [int(x) for x in input().split()]

graph = []

for i in range(n+1):
	graph.append([])

for i in range(m):
	vertex, neighbor, weight = [int(x) for x in input().split()]
	graph[vertex].append([neighbor, weight])
	graph[neighbor].append([vertex, weight])

source, destiny = [int(x) for x in input().split()]

path, dist, pred = [], [inf] * len(graph), [-1] * len(graph)

dist[source] = 0

dijkstra(graph, source)

makePath(source,destiny)

for i,p in enumerate(path):
	if(i == (len(path)-1)):
		print(str(p),end='')
	else:
		print(str(p) + "-",end='')

print("(Total = " + str(dist[destiny]) + "km)")