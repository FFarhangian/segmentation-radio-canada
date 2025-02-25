# ===========================================================
# Segmentation of Users Based on Subscription Status
# ===========================================================

# Load necessary libraries
library(dplyr)
library(mclust)
library(fossil)
library(ggplot2)
library(cluster)
library(bios2mds)

# ===========================================================
# Step 1: Load Data
# ===========================================================
cbcl <- read.csv("df_segmented.csv")

# Check dataset dimensions and subscription distribution
dim(cbcl)
table(cbcl$abonnement)

# ===========================================================
# Step 2: Preprocess Data for Clustering
# ===========================================================

# Function to prepare data based on `abonnement` value
prepare_data <- function(df, abonnement_value) {
  df_filtered <- df[df$abonnement == abonnement_value,]
  
  # Select only relevant columns
  if (abonnement_value == 1) {
    df_filtered <- df_filtered[, -c(1, 2, 4, 5, 9:23)]
  } else {
    df_filtered <- df_filtered[, -c(1, 2, 4, 6, 9:23)]
  }
  
  return(df_filtered)
}

# Prepare data for `abonnement = 0` (non-subscribers) and `abonnement = 1` (subscribers)
cbcl_ab0 <- prepare_data(cbcl, 0)
cbcl_ab1 <- prepare_data(cbcl, 1)

# Keep only relevant clustering columns
clust_dat_0 <- cbcl_ab0[, 2:4]
clust_dat_1 <- cbcl_ab1[, 2:4]

# ===========================================================
# Step 3: Hierarchical Clustering
# ===========================================================
perform_hierarchical_clustering <- function(clust_data, title) {
  persclus <- hclust(dist(clust_data), method = "ward.D2")
  plot(persclus, main = paste("Dendrogram for", title))
}

perform_hierarchical_clustering(clust_dat_0, "Abonnement = 0")
perform_hierarchical_clustering(clust_dat_1, "Abonnement = 1")

# ===========================================================
# Step 4: K-Means Clustering
# ===========================================================
perform_kmeans <- function(clust_data, k) {
  cl <- kmeans(clust_data, k)
  plot(clust_data, col = cl$cluster, main = paste("K-Means Clustering (K =", k, ")"))
  points(cl$centers, col = 1:k, pch = 8, cex = 2)
  return(cl)
}

# Apply K-Means Clustering
kmeans_ab0 <- perform_kmeans(clust_dat_0, 3)
kmeans_ab1 <- perform_kmeans(clust_dat_1, 3)

# Add cluster assignments to original data
cbcl_ab0$kmeansClust <- kmeans_ab0$cluster
cbcl_ab1$kmeansClust <- kmeans_ab1$cluster

# ===========================================================
# Step 5: Model-Based Clustering (GMM)
# ===========================================================
perform_model_clustering <- function(clust_data, k) {
  mbclus <- Mclust(clust_data, G = k)
  plot(mbclus, what = "BIC")
  return(mbclus)
}

# Apply Model-Based Clustering (GMM)
modclus_ab0 <- perform_model_clustering(clust_dat_0, 3)
modclus_ab1 <- perform_model_clustering(clust_dat_1, 3)

# Add cluster assignments
cbcl_ab0$modelClust <- modclus_ab0$classification
cbcl_ab1$modelClust <- modclus_ab1$classification

# ===========================================================
# Step 6: Evaluate Clustering with Rand Index
# ===========================================================
evaluate_rand_index <- function(model_clusters, kmeans_clusters) {
  rand.index(as.vector(model_clusters), as.vector(kmeans_clusters))
}

rand_index_ab0 <- evaluate_rand_index(modclus_ab0$classification, kmeans_ab0$cluster)
rand_index_ab1 <- evaluate_rand_index(modclus_ab1$classification, kmeans_ab1$cluster)

cat("\nRand Index for Abonnement = 0:", rand_index_ab0)
cat("\nRand Index for Abonnement = 1:", rand_index_ab1)

# ===========================================================
# Step 7: Compute Silhouette Score
# ===========================================================
compute_silhouette_score <- function(clust_data) {
  sil.score(clust_data, nb.clus = c(2:5), nb.run = 100, iter.max = 1000, method = "euclidean")
}

silhouette_ab0 <- compute_silhouette_score(clust_dat_0)
silhouette_ab1 <- compute_silhouette_score(clust_dat_1)

# ===========================================================
# Step 8: Analyze Cluster Characteristics
# ===========================================================
summarize_clusters <- function(df, cluster_column) {
  df %>%
    group_by(!!sym(cluster_column)) %>%
    summarise(across(c(num_devices, subscription_duration, unique_programs, avg_watch_time, 
                       pct_gratuit, pct_not_logged_in, pct_enchainement, pct_reprise, pct_actif, 
                       pct_progress_75, avg_videoinitiate, Ados, Pour.les.plus.grands, 
                       watch_rate, Educational_Informational, Fiction_Entertainment, 
                       Talk_Show_Reality, Adventure_Youth, For_All_Ages), mean, na.rm = TRUE))
}

# Summarize clusters for both segmentation methods
summary_kmeans_ab0 <- summarize_clusters(cbcl_ab0, "kmeansClust")
summary_model_ab0 <- summarize_clusters(cbcl_ab0, "modelClust")
summary_kmeans_ab1 <- summarize_clusters(cbcl_ab1, "kmeansClust")
summary_model_ab1 <- summarize_clusters(cbcl_ab1, "modelClust")

# ===========================================================
# Step 9: Save Results
# ===========================================================
write.csv(cbcl_ab0, "segmented_users_abonnement_0.csv", row.names = FALSE)
write.csv(cbcl_ab1, "segmented_users_abonnement_1.csv", row.names = FALSE)
write.csv(summary_kmeans_ab0, "summary_kmeans_abonnement_0.csv", row.names = FALSE)
write.csv(summary_model_ab0, "summary_model_abonnement_0.csv", row.names = FALSE)
write.csv(summary_kmeans_ab1, "summary_kmeans_abonnement_1.csv", row.names = FALSE)
write.csv(summary_model_ab1, "summary_model_abonnement_1.csv", row.names = FALSE)

cat("\nClustering Process Completed Successfully!")
