library(dplyr)
library(ggplot2)

# ---- Putanje do CSV datoteka ----
heuristic_file <- "data/results/min_cut_greedy_partition_results.csv"
random_file <- "data/results/min_cut_heuristic_partition_results.csv"

# ---- Load CSVs ----
heuristic_df <- read.csv(heuristic_file) %>%
  mutate(algorithm = "Greedy Partitions")

random_df <- read.csv(random_file) %>%
  mutate(algorithm = "Random Partitions")

# ---- Optimalne vrijednosti (pretpostavljamo da dolaze iz istog foldera) ----
opt_df <- read.csv("data/results/min_cut_partition_results.csv") %>%
  select(graph, opt_cut = min_cut)

# ---- Spoji s optimalnim vrijednostima ----
heuristic_cmp <- heuristic_df %>%
  inner_join(opt_df, by = "graph") %>%
  mutate(abs_err = abs(min_cut - opt_cut))

random_cmp <- random_df %>%
  inner_join(opt_df, by = "graph") %>%
  mutate(abs_err = abs(min_cut - opt_cut))

# ---- Kombiniraj oba algoritma ----
cmp_combined <- bind_rows(heuristic_cmp, random_cmp) %>%
  mutate(algorithm = factor(algorithm, levels = c("Greedy Partitions", "Random Partitions")))

# ---- Histogram: koliko puta algoritam nije pogodio minimalni cut ----
cmp_combined$missed <- cmp_combined$abs_err > 0

cmp_nonzero <- cmp_combined %>% filter(abs_err > 0)

p <- ggplot(cmp_nonzero, aes(x = abs_err, fill = algorithm)) +
  geom_histogram(position = "dodge", binwidth = 0.5, color = "black") + 
  scale_x_continuous(breaks = scales::pretty_breaks(n = max(cmp_combined$abs_err))) +
  labs(
    title = "Histogram of Absolute Errors (non-zero)",
    x = "Absolute Error",
    y = "Frequency",
    fill = "Algorithm"
  ) +
  theme_minimal(base_size = 10)

# ---- Spremi i prikaži ----
ggsave("hist_abs_error_nonzero.pdf", p, width = 6, height = 4)
print(p)
