library(dplyr)
library(ggplot2)

folder_path <- "data/results"
csv_files <- list.files(path = folder_path, pattern = "*.csv", full.names = TRUE)

# Load all CSVs and combine
all <- lapply(csv_files, function(f) {
  df <- read.csv(f)
  df$algorithm <- tools::file_path_sans_ext(basename(f))
  df
})
big <- bind_rows(all)

# Filter only rows where algorithm finished (min_cut != -1)
valid <- big %>% filter(min_cut != -1)
valid$algorithm <- recode(valid$algorithm,
                          "min_cut_greedy_results" = "Greedy Edge Removal",
                          "min_cut_greedy_partition_results" = "Greedy Partition",
                          "min_cut_partition_results" = "Exhaustive Partition",
                          "min_cut_random_contractions_results" = "Random Contractions",
                          "min_cut_random_contractions_exhaustive_results" = "Contractions-Then-Exhaustive",
                          "min_cut_heuristic_partition_results" = "Random Partitions",
)

# ---- GROUP BY NODES ----
ops_by_nodes <- valid %>%
  group_by(algorithm, nodes) %>%
  summarise(
    avg_ops = mean(basic_operations, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(log_ops = log10(avg_ops))

# ---- GROUP BY EDGES ----
ops_by_edges <- valid %>%
  group_by(algorithm, edges) %>%
  summarise(
    avg_ops = mean(basic_operations, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(log_ops = log10(avg_ops))
         
         
 p1 <- ggplot(ops_by_nodes, aes(x = nodes, y = log_ops, color = algorithm)) +
      geom_line() + geom_point() +
      labs(
      title = "Log Basic Operations vs Number of Nodes",
      x = "Number of Nodes (|V|)",
      y = "log10(Basic Operations)"
      ) +
      theme_minimal()
 
ggsave("log_ops_vs_nodes.pdf", p1, width = 6, height = 4)
print("Saved: log_ops_vs_nodes.png")
print(p1)
         
         
p2 <- ggplot(ops_by_edges, aes(x = edges, y = log_ops, color = algorithm)) +
        geom_line() + geom_point() +
        labs(
        title = "Log Basic Operations vs Number of Edges",
        x = "Number of Edges (|E|)",
        y = "log10(Basic Operations)"
        ) +
        theme_minimal()

ggsave("log_ops_vs_edges.pdf", p2, width = 6, height = 4)
print("Saved: log_ops_vs_nedges.pdf")

print(p1)


# ---- GROUP BY NODES: compute avg solutions tested ----
sol_by_nodes <- valid %>%
  group_by(algorithm, nodes) %>%
  summarise(
    avg_solutions = mean(solutions_tested, na.rm = TRUE),
    .groups = "drop"
  ) %>%
  mutate(log_solutions = log10(avg_solutions))

# ---- PLOT ----
p_solutions_nodes <- ggplot(sol_by_nodes,
                            aes(x = nodes, y = log_solutions, color = algorithm)) +
  geom_line() + geom_point() +
  labs(
    title = "Log Solutions Tested vs Number of Nodes",
    x = "Number of Nodes (|V|)",
    y = "log10(Solutions Tested)"
  ) +
  theme_minimal()

ggsave("log_solutions_vs_nodes.pdf", p_solutions_nodes,
       width = 6, height = 4)

print("Saved: log_solutions_vs_nodes.pdf")
print(p_solutions_nodes)

corr_table <- valid %>%
  group_by(algorithm) %>%
  summarise(
    n = n(),
    correlation = cor(solutions_tested, basic_operations, use = "complete.obs"),
    .groups = "drop"
  )

print("Correlation between solutions tested and basic operations:")
print(corr_table)

filtered <- valid %>% 
  filter(algorithm != "Exhaustive Edge Subset")

# ---- GROUP BY NODES ----
time_by_nodes <- filtered %>%
  group_by(algorithm, nodes) %>%
  summarise(
    avg_time = mean(time_elapsed, na.rm = TRUE),
    .groups = "drop"
  )

p4 <- ggplot(time_by_nodes, aes(x = nodes, y = avg_time, color = algorithm)) +
  geom_line() + geom_point() +
  scale_y_log10() +
  labs(title = "Runtime vs Number of Nodes",
       x = "Number of Nodes (|V|)",
       y = "Runtime (seconds, log scale)") +
  theme_minimal()

ggsave("time_vs_nodes.pdf", p4,
       width = 6, height = 4)


# ---- OPS vs NODES ----
ggsave("log_ops_vs_nodes.pdf", p1, width = 6, height = 4)
print("Saved: log_ops_vs_nodes.pdf")
print(p1)

# ---- OPS vs EDGES ----
ggsave("log_ops_vs_edges.pdf", p2, width = 6, height = 4)
print("Saved: log_ops_vs_edges.pdf")
print(p2)

# ---- SOLUTIONS vs NODES ----
ggsave("log_solutions_vs_nodes.pdf", p_solutions_nodes, width = 6, height = 4)
print("Saved: log_solutions_vs_nodes.pdf")
print(p_solutions_nodes)

# ---- TIME vs NODES ----
ggsave("time_vs_nodes.pdf", p4, width = 6, height = 4)
print("Saved: time_vs_nodes.pdf")
print(p4)


library(dplyr)

# Keep only finished runs
valid <- big %>% filter(min_cut != -1)

# Compute per-graph minimum cut across all algorithms
best_per_graph <- valid %>%
  group_by(graph) %>%
  summarise(
    best_cut = min(min_cut),
    .groups = "drop"
  )

# Join back to label which algorithms achieved that best cut
marked <- valid %>%
  inner_join(best_per_graph, by = "graph") %>%
  mutate(achieved_best = (min_cut == best_cut))

# Count how many times each algorithm got the best solution
best_counts <- marked %>%
  group_by(algorithm) %>%
  summarise(
    total_graphs = n(),
    best_found = sum(achieved_best),
    best_rate = round(best_found / total_graphs * 100, 2),
    .groups = "drop"
  ) %>%
  arrange(desc(best_rate))

print(best_counts)


df <- data.frame(
  algorithm = c("min_cut_greedy_results",
                "min_cut_greedy_partition_results",
                "min_cut_heuristic_partition_results",
                "min_cut_random_contractions_results",
                "min_cut_random_contractions_exhaustive_results"),
  total_graphs = c(134, 134, 134, 134, 134),
  best_found = c(134, 131, 128, 69, 52)
)

# Compute error per run
df <- df %>%
  mutate(
    abs_error = total_graphs - best_found
  )

# Summarise average and maximum error per algorithm
error_summary <- df %>%
  group_by(algorithm) %>%
  summarise(
    max_error = max(abs_error),
    avg_error = mean(abs_error),
    .groups = "drop"
  )

print(error_summary)

