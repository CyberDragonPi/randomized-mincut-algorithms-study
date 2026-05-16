import networkx
import glob
import hashlib
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
    partition = tuple([1 if i < mid else 0 for i in range(len(V))])
    S_size = mid
    T_size = len(V) - mid
    return partition, S_size, T_size


def get_bridges(A: list[list[int]], partition: tuple[int]):
    #print(A, S, T)
    bridges = set()

    for u in range(len(partition)):
        for v in range(len(partition)):
            if A[u][v] == 1 and partition[u] != partition[v]:
                bridges.add(tuple(sorted([u, v])))

    return bridges


def calculate_D(partition: tuple[int], neighbours: dict[int, list[int]], algorithm_tracker: AlgorithmTracker):
    D = dict()
    total_cut = 0

    for vertice in range(len(partition)):
        D[vertice] = 0
        for neighbour in neighbours[vertice]:
            algorithm_tracker.basic_operations += 1
            if partition[vertice] == partition[neighbour]:
                D[vertice] -= 1
            else:
                D[vertice] += 1
                total_cut += 1
    
    return D, total_cut //2


def draw_partitioned_graph(G: networkx.Graph, partition: tuple[int], graph_name: str):
    pos = {
        node: tuple(map(float, data["pos"].split(",")))
        for node, data in G.nodes(data=True)
            if "pos" in data
        }
    colors = ["skyblue" if partition[vertice] == 1 else "lightcoral" for vertice in range(len(partition))]
    
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


def calculate_partition_sizes(partition: tuple[int], algorithm_tracker: AlgorithmTracker):
    S_size = sum(partition)
    T_size = len(partition) - S_size

    algorithm_tracker.basic_operations += len(partition)  # jedan prolazak kroz sve čvorove

    return S_size, T_size


def solve_heuristic_partitions(G: networkx.Graph, algorithm_tracker: AlgorithmTracker, seen_partition: set):
    nodes = [int(v) for v in G.nodes()]
    edges = [(int(u), int(v)) for (u, v) in G.edges()]
    V = len(nodes)

    neighbours = {int(node): [int(neigh) for neigh in G.neighbors(node)] for node in G.nodes()}

    max_attempts = 5
    partition = None
    S_size = T_size = None
    partition_hash = None

    for _ in range(max_attempts):
        candidate_partition, S_size_candidate, T_size_candidate = split_nodes_randomly(nodes)
        algorithm_tracker.basic_operations += V # splitting takes O(|V|)
        candidate_hash = hashlib.sha256(str(candidate_partition).encode()).hexdigest()
        if candidate_hash not in seen_partition:
            partition = candidate_partition
            S_size = S_size_candidate
            T_size = T_size_candidate
            partition_hash = candidate_hash
            seen_partition.add(partition_hash)
            break
        algorithm_tracker.basic_operations += V # hashing and checking takes O(|V| + 1)

    if partition is None:
        max_cut = sum([1 for (u, v) in edges])
        algorithm_tracker.end_time = time.time()
        return max_cut, None, None, None, algorithm_tracker

    nodes_D, cut_size = calculate_D(partition, neighbours, algorithm_tracker)

    A = [[0 for column in range(V)] for row in range(V)]
    for (a, b) in edges:
        A[a][b] = 1
        A[b][a] = 1
        algorithm_tracker.basic_operations += 1

    best_partition = partition
    min_cut = cut_size
    result_improved = True

    seen_partitions = set()
    seen_partitions.add(tuple(partition[node] for node in sorted(nodes)))

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
                if (partition[node] == 1 and S_size <= 1) or (partition[node] == 0 and T_size <= 1):
                    continue
                if best_node is None or current_D[node] > current_D[best_node]:
                    best_node = node

            if best_node is None:
                break
            
            partition = list(partition)
            if partition[best_node] == 1:
                partition[best_node] = 0
                S_size -= 1
                T_size += 1
            else:
                partition[best_node] = 1
                S_size += 1
                T_size -= 1
            partition = tuple(partition)

            unlocked_nodes.remove(best_node)
            move_sequence.append(best_node)
            algorithm_tracker.basic_operations += 2

            # Ažuriranje D vrijednosti
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
                    best_partition = list(best_partition)
                    best_partition[node] = partition[node]
                    best_partition = tuple(best_partition)

                partition = deepcopy(best_partition)
                S_size, T_size = calculate_partition_sizes(partition, algorithm_tracker)
                nodes_D, cut_size = calculate_D(partition, neighbours, algorithm_tracker)

                part_hash = hashlib.sha256(str(partition).encode()).hexdigest()
                if part_hash in seen_partitions:
                    result_improved = False
                else:
                    seen_partitions.add(part_hash)

            else:
                result_improved = False
        else:
            result_improved = False

    edges_to_remove = get_bridges(A, best_partition)
    return min_cut, best_partition, A, edges_to_remove, algorithm_tracker



def run_multiple_times(G: networkx.Graph, algorithm_tracker: AlgorithmTracker, max_iterations: int=100, time_limit: float=5.0):
    seen_partitions = set()

    best_cut = float('inf')
    best_partition = None
    best_A = None
    best_edges_to_remove = None

    iterations = 0
    algorithm_tracker.start_time = time.time()
    while iterations < max_iterations and (time.time() - algorithm_tracker.start_time) <= time_limit:
        iterations += 1
        min_cut, partition, A, edges_to_remove, algorithm_tracker = solve_heuristic_partitions(
            G, algorithm_tracker, seen_partitions
        )
        if min_cut < best_cut:
            best_cut = min_cut
            best_partition = partition
            best_A = A
            best_edges_to_remove = edges_to_remove

    algorithm_tracker.end_time = time.time()

    return best_cut, best_partition, best_A, best_edges_to_remove, algorithm_tracker



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
        min_number_of_bridges, partition, A, edges_to_remove, algorithm_tracker = run_multiple_times(G, algorithm_tracker)

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
    dataframe_partition.to_csv("min_cut_heuristic_partition_results.csv", index=False)