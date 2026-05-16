# Randomized Algorithms for the Minimum Cut Problem

This project presents a design, analysis, and experimental evaluation of randomized algorithms for solving the global minimum cut problem in undirected, unweighted graphs.

The focus is on comparing fully randomized methods with hybrid and heuristic approaches, and analyzing the trade-off between solution quality, probability of success, and computational efficiency.

## Algorithms Implemented

### 1. Random Edge Contraction (Karger-style)
Repeatedly contracts random edges until two super-nodes remain. The cut is computed between the final components.

### 2. Contraction-Then-Exhaustive Hybrid
Performs partial random contractions to reduce graph size, followed by exhaustive partition enumeration on the reduced graph.

### 3. Greedy Randomized Partitioning
Improves a greedy partitioning heuristic by running multiple randomized initializations and selecting the best result.

---

## Key Ideas

- Randomization helps escape local minima in deterministic greedy approaches
- Multiple independent runs increase probability of finding the global optimum
- Hybrid methods balance structural preservation and exhaustive search
- Hashing is used to avoid redundant evaluations of identical states

---

## Experimental Study

The algorithms are evaluated on:
- success rate vs number of iterations
- cut quality (exact vs approximate)
- computational time complexity
- scalability with graph size

Results show:
- Pure randomized methods are fast but unstable
- Hybrid approaches significantly improve accuracy
- Randomized greedy methods provide strong practical performance

---

## Dataset / Graphs

Synthetic and generated graph instances were used for evaluation, including varying sizes and densities.

---

## Conclusion

This study compares exhaustive, greedy, randomized, and hybrid approaches for the minimum cut problem in undirected graphs.

Key findings:

- Exhaustive methods guarantee optimality but scale exponentially and become impractical for larger graphs.
- Greedy heuristics scale efficiently but may miss globally optimal cuts due to local decision-making.
- Randomized methods provide variable performance depending on graph structure.
- Hybrid approaches combining randomization with limited exhaustive search offer the best balance between robustness and accuracy.

Overall, the results highlight the trade-off between optimality and computational efficiency, showing that heuristic and randomized strategies are practical alternatives to exact methods for large-scale graphs.


## Project Structure

```text
├── study.pdf  
├── data  
│   ├── graphs  
│   ├── plots  
│   └── results  
└── src  
    ├── graph_generation  
    ├── solve  
    └── data_analysis  