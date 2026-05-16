import networkx
import glob
import os
import pandas
import time
import random
import matplotlib.pyplot as plt

from copy import deepcopy
from algorithm_tracker import AlgorithmTracker


def split_nodes_randomly(V):
    V = list(V)
    random.shuffle(V)
    mid = len(V) // 2
    S = set(V[:mid])
    T = set(V[mid:])

    partition = {}
    for u in S:
        partition[u] = "S"
    for u in T:
        partition[u] = "T"

    return partition, len(S), len(T)


def get_bridges(A: list[list[int]], partition: dict[int, str]):
    #print(A, S, T)
    bridges = set()

    for u in partition:
        for v in partition:
            if A[u][v] == 1 and partition[u] != partition[v]:
                bridges.add(tuple(sorted([u, v])))

    return bridges


def calculate_D(partition: dict[int, str], neighbours: dict[int, list[int]], algorithm_tracker: AlgorithmTracker):
    D = dict()
    total_cut = 0

    for vertice in partition:
        D[vertice] = 0
        for neighbour in neighbours[vertice]:
            algorithm_tracker.basic_operations += 1
            if partition[vertice] == partition[neighbour]:
                D[vertice] -= 1
            else:
                D[vertice] += 1
                total_cut += 1
    
    return D, total_cut //2


def draw_partitioned_graph(G: networkx.Graph, partition: dict[int, str], graph_name: str):
    pos = {
        node: tuple(map(float, data["pos"].split(",")))
        for node, data in G.nodes(data=True)
            if "pos" in data
        }
    colors = ["skyblue" if partition[int(node)] == "S" else "lightcoral" for node in G.nodes()]
    
    if len(partition) > 15:
        fig_size = 8
    else:
        fig_size = 4
    plt.figure(figsize=(fig_size, fig_size))
    networkx.draw_networkx_edges(G, pos, alpha=0.5)
    networkx.draw_networkx_nodes(G, pos, node_color=colors, node_size=300)
    labels = {node: str(node) for node in G.nodes()}
    
    networkx.draw_networkx_labels(G, pos, labels=labels, font_size=8)
    
    plt.title("Graph Partition")
    plt.axis("off")
    plt.savefig(f"Greedy_partition/Partitions/{graph_name}.pdf", format='pdf', bbox_inches='tight')
    plt.close()
    plt.clf()
    plt.close('all')
    #plt.show()


def calculate_partition_sizes(partition: dict[int, str], algorithm_tracker: AlgorithmTracker):
    S_size = 0
    T_size = 0

    for node in partition:
        algorithm_tracker.basic_operations += 1
        if partition[node] == "S":
            S_size += 1
        else:
            T_size += 1

    return S_size, T_size


def solve_greedy_partitions(G: networkx.Graph, algorithm_tracker: AlgorithmTracker):
    algorithm_tracker.start_time = time.time()
    nodes = G.nodes()
    edges = G.edges()
    V = len(nodes)

    neighbours = {int(node): [int(neigh) for neigh in G.neighbors(node)] for node in G.nodes()}
    nodes = [int(u) for u in nodes]

    partition, S_size, T_size = split_nodes_randomly(nodes)
    nodes_D, cut_size = calculate_D(partition, neighbours, algorithm_tracker)

    A = [[0 for column in range(V)] for row in range(V)]
    for (a, b) in edges:
        A[int(a)][int(b)] = 1
        A[int(b)][int(a)] = 1
    
    best_partition = partition.copy()
    min_cut = cut_size
    #print(min_number)
    result_improved = True

    #draw_partitioned_graph(G, best_partition, nodes_D)
    
    #print(nodes_D)

    #draw_partitioned_graph(G, partition, nodes_D)
    while result_improved:
        unlocked_nodes = set(nodes)
        current_D = nodes_D.copy()
        current_cut = cut_size

        move_sequence = []
        cut_sequence = []

        while unlocked_nodes:
            algorithm_tracker.solutions_tested += 1
            best_node = None

            for node in unlocked_nodes:
                algorithm_tracker.basic_operations += 1
                if (partition[node] == "S" and S_size <= 1) or (partition[node] == "T" and T_size <= 1):
                    continue
                if best_node is None or current_D[node] > current_D[best_node]:
                    best_node = node

            if best_node is None:
                break 

            if partition[best_node] == "S":
                partition[best_node] = "T"
                S_size -= 1
                T_size += 1
            else:
                partition[best_node] = "S"
                S_size += 1
                T_size -= 1

            unlocked_nodes.remove(best_node)
            move_sequence.append(best_node)
            algorithm_tracker.basic_operations += 2

            delta_cut = 0
            for neighbour in neighbours[best_node]:
                algorithm_tracker.basic_operations += 1
                if partition[neighbour] == partition[best_node]:
                    current_D[neighbour] -= 2
                    delta_cut -= 1
                else:
                    current_D[neighbour] += 2
                    delta_cut += 1

            current_D[best_node] = -current_D[best_node]
            current_cut += delta_cut
            cut_sequence.append(current_cut)

        if cut_sequence:
            min_index = cut_sequence.index(min(cut_sequence))
            if cut_sequence[min_index] < min_cut:
                min_cut = cut_sequence[min_index]
                for i, node in enumerate(move_sequence[:min_index + 1]):
                    best_partition[node] = partition[node]

                partition = deepcopy(best_partition)
                S_size, T_size = calculate_partition_sizes(partition, algorithm_tracker)
                nodes_D, cut_size = calculate_D(partition, neighbours, algorithm_tracker)
                #print(f"Partition sizes of new graph {S_size}, {T_size}")
                #draw_partitioned_graph(G, partition, nodes_D)
                
            else:
                result_improved = False
        else:
            result_improved = False

    
    algorithm_tracker.end_time = time.time()
    return min_cut, best_partition, A, algorithm_tracker
          

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
        min_number_of_bridges, partition, A, algorithm_tracker = solve_greedy_partitions(G, algorithm_tracker)
        edges_to_remove = get_bridges(A, partition)

        #draw_partitioned_graph(G, partition, graph_name)
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
    dataframe_partition.to_csv("min_cut_greedy_partition_results.csv", index=False)