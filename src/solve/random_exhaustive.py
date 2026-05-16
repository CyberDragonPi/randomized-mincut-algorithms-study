import random
import hashlib
import time
import networkx
import os
import glob
import itertools
import pandas

from algorithm_tracker import AlgorithmTracker


def generate_node_partitions(nodes: list, V: int):
    partitions = []
    nodes = [int(u) for u in nodes]

    for r in range(1, V //2 + 1):
        for subset in itertools.combinations(nodes, r):
            S = set(subset)
            T = set(nodes) - S
            partitions.append((S, T))

    return partitions


def random_contraction_until_7(original_graph, original_components, algorithm_tracker):
    # Kreiramo kopiju grafa i komponenti
    graph = {v: set(neighbors) for v, neighbors in original_graph.items()}  # O(|V| + |E|)
    components = {v: set(comp) for v, comp in original_components.items()}  # O(|V|)
    algorithm_tracker.basic_operations += len(graph) + sum(len(neigh) for neigh in graph.values())

    alive = set(graph.keys())  # čuvamo koji čvorovi su "živih" u grafu

    while len(alive) > 7:
        u = random.choice(list(alive))
        if not graph[u]:
            alive.remove(u)
            continue

        # Odaberi susjeda koji je još živ
        neighbors_u = [v for v in graph[u] if v in alive]
        if not neighbors_u:
            alive.remove(u)
            continue

        v = random.choice(neighbors_u)
        algorithm_tracker.basic_operations += 1

        # Merge v u u
        components[u].update(components[v])

        # Iteriraj preko kopije susjeda v da izbjegnemo modifikaciju tijekom iteracije
        for nbr in list(graph[v]):
            if nbr != u and nbr in graph:  # provjeri da susjed još postoji
                graph[nbr].discard(v)  # ukloni stari brid
                graph[nbr].add(u)      # dodaj novi brid
                graph[u].add(nbr)
            algorithm_tracker.basic_operations += 1

        # ukloni v iz alive i graf strukture
        alive.remove(v)
        del graph[v]

    return graph, components, algorithm_tracker


def get_min_cut(G: networkx.Graph, algorithm_tracker: AlgorithmTracker, max_iterations: int=100, time_limit: float=5.0):
    algorithm_tracker.start_time = time.time()
    best_cut = None
    best_cut_size = float('inf')
    seen_hashes = set()

    original_graph = {int(node): list() for node in G.nodes()}
    algorithm_tracker.basic_operations += len(original_graph)

    for u, v in G.edges():
        original_graph[int(u)].append(int(v))
        original_graph[int(v)].append(int(u))
        algorithm_tracker.basic_operations += 1

    original_components = {int(node): {int(node)} for node in G.nodes()}
    algorithm_tracker.basic_operations += len(original_components)

    iterations = 0

    while iterations < max_iterations and (time.time() - algorithm_tracker.start_time) <= time_limit:
        contracted_graph, components, algorithm_tracker = random_contraction_until_7(original_graph, original_components, algorithm_tracker)
        final_sets = [components[v] for v in contracted_graph.keys()]
        sorted_sets = tuple(sorted(tuple(sorted(s)) for s in final_sets))
        cut_hash = hashlib.sha256(str(sorted_sets).encode()).hexdigest()
        algorithm_tracker.basic_operations += 1
        iterations += 1

        if cut_hash in seen_hashes:
            continue
        seen_hashes.add(cut_hash)

        nodes = list(contracted_graph.keys())
        V = len(nodes)
        partitions = generate_node_partitions(nodes, V)

        minimum_number_of_bridges = float('inf')
        best_S = set()
        best_T = set()

        for (S, T) in partitions:
            algorithm_tracker.solutions_tested += 1
            current_number_of_bridges = 0

            for u in S:
                for v in T:
                    for orig_u in components[u]:
                        for orig_v in components[v]:
                            if orig_v in original_graph[orig_u]:
                                current_number_of_bridges += 1
                            algorithm_tracker.basic_operations += 1

            if current_number_of_bridges < minimum_number_of_bridges:
                minimum_number_of_bridges = current_number_of_bridges
                best_S = S
                best_T = T

            if current_number_of_bridges == 1:
                break  # early stop

        if minimum_number_of_bridges < best_cut_size:
            best_cut_size = minimum_number_of_bridges
            best_cut = (best_S, best_T)

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
        #print(f"Loaded graph with V={G.number_of_nodes()} and E={G.number_of_edges()}")
        
        algorithm_tracker = AlgorithmTracker() 
        best_cut, min_cut_size, algorithm_tracker = get_min_cut(G, algorithm_tracker)

        results_random_contractions.append({
            "graph": graph_name,
            "nodes": G.number_of_nodes(),
            "edges": G.number_of_edges(),
            "min_cut": min_cut_size,
            "solutions_tested": algorithm_tracker.solutions_tested,
            "basic_operations": algorithm_tracker.basic_operations,
            "time_elapsed": algorithm_tracker.end_time - algorithm_tracker.start_time
        })

        print(f"-----------------------------------")


    results = sorted(results_random_contractions, key=lambda x: (x["nodes"], x["edges"]))
    dataframe_partition = pandas.DataFrame(results)
    dataframe_partition.to_csv("min_cut_random_contractions_exhaustive_results.csv", index=False)