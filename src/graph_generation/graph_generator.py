import networkx
import random
import math
import matplotlib.pyplot as plt

class Generator:
    def __init__(self, V: int, k: float, student_number: int, distance_threshold: float, max_neighbours: int, max_weight: int):
        self.V = V
        self.k = k
        self.E = min(max(self.V - 1, int(self.k * self.V * (self.V - 1) /2) + 1), self.V * (self.V - 1) /2)
        random.seed(student_number)
        self.distance_threshold = distance_threshold
        self.max_neighbours = max_neighbours
        self.max_weight = max_weight
        self.generating_constant = 500
        self.visited = [0 for i in range(self.V)]


    def generate_graph(self) -> networkx.Graph:
        G = networkx.Graph()
        print(f"Generating graph {self.V}, {self.k}")

        vertices = self.generate_vertices()

        for (idx, v) in enumerate(vertices):
            G.add_node(idx, pos=v)
    
        edges = self.generate_edges()
        for (u, v, w) in edges:
            G.add_edge(u, v, weight=w)
        return G


    def generate_vertices(self) -> list[tuple[int, int]]:
        vertices = []

        while len(vertices) < self.V:
            x = random.randint(1, 500)
            y = random.randint(1, 500)

            if self.far_enough((x, y), vertices):
                vertices.append((x, y))
            
        return vertices
    

    def far_enough(self, new_node: tuple[int, int], vertices_to_compare: list[tuple[int, int]]) -> bool:
        for vertice in vertices_to_compare:
            if math.dist(vertice, new_node) < self.distance_threshold:
                return False

        return True
    

    def generate_edges(self) -> list[tuple[int, int, int]]:
        edges = set()

        while len(edges) < self.E:
            u = random.randint(0, self.V - 1)
            v = random.randint(0, self.V - 1)

            if u != v:
                edge = tuple(sorted([u, v]))
                edges.add(edge)

        edges = [(u, v, int(random.uniform(1, self.max_weight))) for u, v in edges]
        return edges
    

    def check_connected(self, starting_node: int, graph: networkx.Graph) -> bool:
        self.visited = [0 for i in range(self.V)]
        self.floodfill(starting_node, graph)
        #print(f"Sum of visited: {sum(self.visited)}, number of vertices: {self.V}, number of edges: {self.E}")
        #input("...")
        return (sum(self.visited) == self.V)


    def floodfill(self, current_node: int, graph: networkx.Graph):
        self.visited[current_node] = 1

        for v in graph.neighbors(current_node):
            if self.visited[v] == 0:
                self.floodfill(v, graph)
    

    def save_graph(self, graph: networkx.Graph, iteration: int, dir: str="Graphs/"):
        for (node, data) in graph.nodes(data=True):
            if "pos" in data:
                data["pos"] = f"{data['pos'][0]},{data['pos'][1]}"
    
        for (u, v, data) in graph.edges(data=True):
            if "weight" in data:
                data["weight"] = str(data["weight"])
    
        path = f"{dir}Graph_{self.V}_{int(self.E)}_{iteration}.graphml"
        networkx.write_graphml(graph, path)
    