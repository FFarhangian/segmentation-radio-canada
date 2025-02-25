import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from scipy.cluster.hierarchy import dendrogram, linkage
from sklearn.cluster import KMeans, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score, adjusted_rand_score
from sklearn.manifold import TSNE


# Load dataset
df_segmented = pd.read_csv("df_segmented.csv")

# Define features for segmentation
features_abonnement_1 = ['num_devices', 'unique_programs', 'subscription_duration']
features_abonnement_0 = ['num_devices', 'unique_programs', 'avg_watch_time']

# Create separate datasets for both groups
df_abonnement_1 = df_segmented[df_segmented['abonnement'] == 1][features_abonnement_1].dropna()
df_abonnement_0 = df_segmented[df_segmented['abonnement'] == 0][features_abonnement_0].dropna()

# Standardize features for clustering
scaler = StandardScaler()
df_abonnement_1_scaled = scaler.fit_transform(df_abonnement_1)
df_abonnement_0_scaled = scaler.fit_transform(df_abonnement_0)

print("\n✅ Data Loading and Filtering Completed Successfully!")



# Use a subset of the data (10,000 rows max) for Hierarchical Clustering - O(n²)
subset_size = 10000  # Adjust based on available memory
df_abonnement_1_sample = df_abonnement_1_scaled[np.random.choice(df_abonnement_1_scaled.shape[0], min(subset_size, df_abonnement_1_scaled.shape[0]), replace=False)]
df_abonnement_0_sample = df_abonnement_0_scaled[np.random.choice(df_abonnement_0_scaled.shape[0], min(subset_size, df_abonnement_0_scaled.shape[0]), replace=False)]

# ✅ **Hierarchical Clustering on Sampled Data**
plt.figure(figsize=(10, 5))
linked = linkage(df_abonnement_1_sample, method='ward')
dendrogram(linked)
plt.title("Dendrogram for Abonnement = 1 (Sampled Data)")
plt.xlabel("Users")
plt.ylabel("Distance")
plt.show()

plt.figure(figsize=(10, 5))
linked = linkage(df_abonnement_0_sample, method='ward')
dendrogram(linked)
plt.title("Dendrogram for Abonnement = 0 (Sampled Data)")
plt.xlabel("Users")
plt.ylabel("Distance")
plt.show()


# Function to evaluate K-Means with different K values
def evaluate_kmeans(data_scaled, title):
    wcss = []
    silhouette_scores = []

    range_n_clusters = range(2, 7)  # Testing K from 2 to 6
    for k in range_n_clusters:
        kmeans = KMeans(n_clusters=k, random_state=42)
        labels = kmeans.fit_predict(data_scaled)
        wcss.append(kmeans.inertia_)
        silhouette_scores.append(silhouette_score(data_scaled, labels))

    # Plot Elbow Method
    plt.figure(figsize=(8, 5))
    plt.plot(range_n_clusters, wcss, marker='o', linestyle='--', label="WCSS")
    plt.xlabel("Number of Clusters")
    plt.ylabel("WCSS")
    plt.title(f"Elbow Method for {title}")
    plt.legend()
    plt.show()

    # Plot Silhouette Scores
    plt.figure(figsize=(8, 5))
    plt.plot(range_n_clusters, silhouette_scores, marker='o', linestyle='--', label="Silhouette Score")
    plt.xlabel("Number of Clusters")
    plt.ylabel("Silhouette Score")
    plt.title(f"Silhouette Scores for {title}")
    plt.legend()
    plt.show()

# Evaluate K-Means for both groups
evaluate_kmeans(df_abonnement_1_scaled, "Abonnement = 1")
evaluate_kmeans(df_abonnement_0_scaled, "Abonnement = 0")

# Apply K-Means with optimal K
optimal_k_1 = 3
optimal_k_0 = 2

kmeans_1 = KMeans(n_clusters=optimal_k_1, random_state=42)
df_segmented.loc[df_segmented['abonnement'] == 1, 'cluster'] = kmeans_1.fit_predict(df_abonnement_1_scaled)

kmeans_0 = KMeans(n_clusters=optimal_k_0, random_state=42)
df_segmented.loc[df_segmented['abonnement'] == 0, 'cluster'] = kmeans_0.fit_predict(df_abonnement_0_scaled)

print("\n✅ K-Means Clustering Completed!")



# Function to evaluate GMM using BIC
def evaluate_gmm(data_scaled, title):
    bic_scores = []
    range_n_clusters = range(2, 7)

    for k in range_n_clusters:
        gmm = GaussianMixture(n_components=k, random_state=42)
        gmm.fit(data_scaled)
        bic_scores.append(gmm.bic(data_scaled))

    # Plot BIC Scores
    plt.figure(figsize=(8, 5))
    plt.plot(range_n_clusters, bic_scores, marker='o', linestyle='--', label="BIC Score")
    plt.xlabel("Number of Clusters")
    plt.ylabel("BIC")
    plt.title(f"BIC Scores for {title}")
    plt.legend()
    plt.show()

# Evaluate GMM for both groups
evaluate_gmm(df_abonnement_1_scaled, "Abonnement = 1")
evaluate_gmm(df_abonnement_0_scaled, "Abonnement = 0")


# t-SNE for Visualization
def plot_tsne(data_scaled, labels, title):
    tsne = TSNE(n_components=2, random_state=0)
    tsne_data = tsne.fit_transform(data_scaled)

    plt.figure(figsize=(7, 7))
    sns.scatterplot(x=tsne_data[:, 0], y=tsne_data[:, 1], hue=labels, palette="viridis")
    plt.xlabel("t-SNE 1")
    plt.ylabel("t-SNE 2")
    plt.title(f"t-SNE Clustering Visualization - {title}")
    plt.show()

# Apply t-SNE Visualization for both groups
plot_tsne(df_abonnement_1_scaled, df_segmented[df_segmented['abonnement'] == 1]['cluster'], "Abonnement = 1")
plot_tsne(df_abonnement_0_scaled, df_segmented[df_segmented['abonnement'] == 0]['cluster'], "Abonnement = 0")