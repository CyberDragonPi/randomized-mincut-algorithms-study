import itertools

from graph_generator import Generator


if __name__ == "__main__":
    Vs: list[int] = [25, 50, 75, 100, 125, 150, 175, 200, 250, 300, 350, 400, 450, 500, 1000]
    ks: list[float] = [0.125, 0.25, 0.5, 0.75, 1]
    N = 3

    for V, k in itertools.product(Vs, ks):
        print(f"Generating graph with V={V}, k={k}")

        generator = Generator(V, k, student_number=130288, distance_threshold=10, max_neighbours=V - 1, max_weight=0)
        iterations = 2
        for i in range(iterations):
            graph = generator.generate_graph()
            while not generator.check_connected(0, graph):
                print("Generation failed. Generating again.")
                graph = generator.generate_graph()

            generator.save_graph(graph, i, "../large_graphs/")

    