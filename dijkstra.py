
import heapq

def dijkstra(graph, source, destination):
    distances = {airport: float("inf") for airport in graph}
    distances[source] = 0
    previous = {}
    queue = [(0, source)]

    while queue:
        distance, airport = heapq.heappop(queue)

        if distance > distances[airport]:
            continue

        if airport == destination:
            break

        for neighbor, weight in graph[airport].items():
            new_distance = distance + weight

            if new_distance < distances[neighbor]:
                distances[neighbor] = new_distance
                previous[neighbor] = airport
                heapq.heappush(queue, (new_distance, neighbor))

    if distances[destination] == float("inf"):
        return [], float("inf")

    path = []
    current = destination

    while current != source:
        path.append(current)
        current = previous[current]

    path.append(source)
    path.reverse()

    return path, distances[destination]
