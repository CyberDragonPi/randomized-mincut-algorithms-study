import random
import hashlib
import time
import networkx
import os
import glob
import pandas
from algorithm_tracker import AlgorithmTracker


def random_contraction(original_graph, original_components, algorithm_tracker: AlgorithmTracker):
    graph = {v: list(neighbors) for v, neighbors in original_graph.items()} # O(|E|)
    components = {v: set(comp) for v, comp in original_components.items()} # O(|V|)
    algorithm_tracker.basic_operations += len(graph) + sum(len(neigh) for neigh in graph.values())

    alive = set(graph.keys()) # O(|V|)

    while len(alive) > 2: # this is run |V| times in theory
        edges = [(u, v) for u in alive for v in graph[u] if v in alive]
        algorithm_tracker.basic_operations += len(edges)

        u, v = random.choice(edges) # O(1)
        algorithm_tracker.basic_operations += 1

        for nbr in graph[v]:  # Merge vertices
            if nbr != u:  # Avoid self-loop
                graph[u].append(nbr)
                if nbr in graph:
                    graph[nbr] = [u if x == v else x for x in graph[nbr]]
                algorithm_tracker.basic_operations += 1

        # Remove v
        del graph[v]
        alive.remove(v)
        algorithm_tracker.basic_operations += 1

        # Remove self-loops at u
        graph[u] = [x for x in graph[u] if x != u]

        # Merge components
        components[u].update(components[v])
        del components[v]
        algorithm_tracker.basic_operations += 1

    remaining = list(alive)
    if len(remaining) != 2: # bug, should never happen
        return None, float('inf'), None

    a, b = remaining
    comp_a, comp_b = components[a], components[b]

    # Cut size
    cut_size = sum(1 for nbr in graph[a] if nbr == b)

    # Hash for to not check multiple times the same solution
    comp_a_sorted = tuple(sorted(comp_a)) # should be O(|V|) in total
    comp_b_sorted = tuple(sorted(comp_b))
    canon = tuple(sorted([comp_a_sorted, comp_b_sorted]))
    algorithm_tracker.basic_operations += len(comp_a) + len(comp_b)

    cut_hash = hashlib.sha256(str(canon).encode()).hexdigest() # O(|V|)
    algorithm_tracker.basic_operations += len(canon)

    return [comp_a, comp_b], cut_size, cut_hash


def get_min_cut(G: networkx.Graph, algorithm_tracker: AlgorithmTracker, max_iterations: int=100, time_limit: float=5.0):
    algorithm_tracker.start_time = time.time()
    best_cut = None
    best_cut_size = float('inf')
    hash_set = set()

    graph = {int(node): list() for node in G.nodes()}
    algorithm_tracker.basic_operations += len(graph)

    for u, v in G.edges():
        graph[int(u)].append(int(v))
        graph[int(v)].append(int(u))
        algorithm_tracker.basic_operations += 1

    components = {int(node): {int(node)} for node in G.nodes()}
    algorithm_tracker.basic_operations += len(components)

    iterations = 0
    while iterations < max_iterations and (time.time() - algorithm_tracker.start_time) <= time_limit:
        comps, cut_size, cut_hash = random_contraction(graph, components, algorithm_tracker)
        iterations += 1

        if cut_hash not in hash_set:
            hash_set.add(cut_hash)
            algorithm_tracker.solutions_tested += 1

            if cut_size < best_cut_size:
                best_cut_size = cut_size
                best_cut = comps

        # Early stop if minimum possible cut
        if best_cut_size == 1:
            break

    algorithm_tracker.end_time = time.time()
    return best_cut, best_cut_size, algorithm_tracker


if __name__ == "__main__":
    dir_path = r"../large_graphs"
    graphml_files = glob.glob(os.path.join(dir_path, "*.graphml"))

    graphs_info = []
    for file_path in graphml_files:
        G = networkx.read_graphml(file_path)
        graphs_info.append((file_path, G.number_of_nodes(), G.number_of_edges()))

    graphs_info.sort(key=lambda x: (x[1], x[2]))
    results_random_contractions = []

    for (file_path, _, _) in graphs_info:
        graph_name = os.path.splitext(os.path.basename(file_path))[0]
        G = networkx.read_graphml(file_path)
        algorithm_tracker = AlgorithmTracker()
        min_cut, min_cut_size, algorithm_tracker = get_min_cut(G, algorithm_tracker)

        print(f"Loaded graph with V={G.number_of_nodes()} and E={G.number_of_edges()}")

        results_random_contractions.append({
            "graph": graph_name,
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "min_cut": min_cut_size,
            "solutions_tested": algorithm_tracker.solutions_tested,
            "basic_operations": algorithm_tracker.basic_operations,
            "time_elapsed": algorithm_tracker.end_time - algorithm_tracker.start_time
        })

    results_random_contractions = sorted(results_random_contractions, key=lambda x: (x["nodes"], x["edges"]))
    dataframe_partition = pandas.DataFrame(results_random_contractions)
    dataframe_partition.to_csv("min_cut_random_contractions_results.csv", index=False)
