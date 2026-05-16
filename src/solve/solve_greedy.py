import networkx
import glob
import os
import pandas
import time

from algorithm_tracker import AlgorithmTracker
from visited_monitor import VisitedMonitor


def floodfill(current_node: int, neighbours: dict[int, list[int]], visited_monitor: VisitedMonitor, algorithm_tracker: AlgorithmTracker):
    visited_monitor.visited[current_node] = 1
    algorithm_tracker.basic_operations += 1

    for v in neighbours[current_node]:
        if visited_monitor.visited[v] == 0:
            floodfill(v, neighbours, visited_monitor, algorithm_tracker)


def check_connected(neighbours: dict[int, list[int]], starting_node: int, V: int, algorithm_tracker: AlgorithmTracker) -> bool:
    #print(graph.nodes, graph.visited)
    visited_monitor = VisitedMonitor(V)
    floodfill(starting_node, neighbours, visited_monitor, algorithm_tracker)
    #print(f"Sum of visited: {sum(self.visited)}, number of vertices: {self.V}, number of edges: {self.E}")
    #input("...")
    return (sum(visited_monitor.visited) == visited_monitor.V)


def calculate_node_degrees(neighbours: dict[int, list[int]], algorithm_tracker: AlgorithmTracker):
    node_degrees = {}

    for node in neighbours:
        node_degrees[node] = len(neighbours[node])
        algorithm_tracker.basic_operations += 1

    return node_degrees, algorithm_tracker


def remove_edge(node_levels: list[int], neighbours: dict[int, list[int]], algorithm_tracker: AlgorithmTracker):
    node = -1

    for i in range(len(node_levels)):
        algorithm_tracker.basic_operations += 1
        if node == -1 or node_levels[i] < node_levels[node]:
            node = i

    neighbour = -1
    for v in neighbours[node]:
        algorithm_tracker.basic_operations += 1
        if neighbour == -1 or node_levels[v] < node_levels[neighbour]:
            neighbour = v

    return node, neighbour, algorithm_tracker

    
def solve_greedy(G: networkx.Graph, algorithm_tracker: AlgorithmTracker):
    algorithm_tracker.start_time = time.time()
    nodes = G.nodes()
    V = len(nodes)

    neighbours = {int(node): [int(neigh) for neigh in G.neighbors(node)] for node in G.nodes()}
    nodes = [int(u) for u in nodes]
    edges_to_remove = set()

    node_levels, algorithm_tracker = calculate_node_degrees(neighbours, algorithm_tracker)

    while True:
        u, v, algorithm_tracker = remove_edge(node_levels, neighbours, algorithm_tracker)
        node_levels[u] -= 1
        neighbours[u].remove(v)

        node_levels[v] -= 1
        neighbours[v].remove(u)
        algorithm_tracker.solutions_tested += 1

        edges_to_remove.add(tuple(sorted([u, v])))

        if node_levels[u] == 0 or node_levels[v] == 0:
            break
        
        if not check_connected(neighbours, 0, V, algorithm_tracker):
            break
    
    algorithm_tracker.end_time = time.time()
    return len(edges_to_remove), edges_to_remove, algorithm_tracker



if __name__ == "__main__":
    dir_path = r"../large_graphs"
    graphml_files = glob.glob(os.path.join(dir_path, "*.graphml"))

    graphs_info = []
    for file_path in graphml_files:
        G = networkx.read_graphml(file_path)
        graphs_info.append((file_path, G.number_of_nodes(), G.number_of_edges()))

    graphs_info.sort(key=lambda x: (x[1], x[2]))
    results_greedy = []

    for (file_path, _, _) in graphs_info:
        graph_name = os.path.splitext(os.path.basename(file_path))[0]
        G = networkx.read_graphml(file_path)
        print(f"Loaded graph with V={G.number_of_nodes()} and E={G.number_of_edges()}")

        algorithm_tracker = AlgorithmTracker() 
        min_number_of_bridges, edges_to_remove, algorithm_tracker = solve_greedy(G, algorithm_tracker)

        results_greedy.append({
            "graph": graph_name,
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "min_cut": min_number_of_bridges,
            "edges_to_remove": edges_to_remove,
            "solutions_tested": algorithm_tracker.solutions_tested,
            "basic_operations": algorithm_tracker.basic_operations,
            "time_elapsed": algorithm_tracker.end_time - algorithm_tracker.start_time
        })

        print(f"-----------------------------------")

    results = sorted(results_greedy, key=lambda x: (x["nodes"], x["edges"]))
    dataframe_partition = pandas.DataFrame(results)
    dataframe_partition.to_csv("min_cut_greedy_results.csv", index=False)