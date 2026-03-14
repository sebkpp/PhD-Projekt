"""
Explorative Datenanalyse: PCA und hierarchisches Clustering.
Für Zusammenhangsanalysen und Teilnehmer-Untergruppen.
"""
from __future__ import annotations
import numpy as np
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler
from sklearn.cluster import AgglomerativeClustering
from scipy.cluster.hierarchy import linkage, dendrogram
from scipy.spatial.distance import pdist


def run_pca(
    data: dict[str, list[float]],
    n_components: int = 2,
) -> dict | None:
    """
    PCA auf den übergebenen Variablen.

    data: {"variable_name": [value_per_participant], ...}
          Alle Listen müssen gleich lang sein (n Teilnehmer).

    Returns None wenn n < n_components + 1 oder < 2 Variablen.

    Returns:
    {
        "explained_variance_ratio": list[float],  # pro Komponente
        "cumulative_variance": list[float],
        "n_components": int,
        "n_observations": int,
        "variable_names": list[str],
        "components": list[dict],  # [{"PC1": float, "PC2": float, ...}] per observation
        "loadings": dict[str, dict],  # {variable: {"PC1": loading, "PC2": loading, ...}}
    }
    """
    variable_names = list(data.keys())
    if len(variable_names) < 2:
        return None

    lengths = [len(v) for v in data.values()]
    if len(set(lengths)) > 1:
        return None  # ungleiche Längen

    n = lengths[0]
    actual_components = min(n_components, len(variable_names), n - 1)
    if actual_components < 1 or n < 2:
        return None

    matrix = np.array([data[v] for v in variable_names], dtype=float).T  # (n, p)

    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix)

    pca = PCA(n_components=actual_components)
    scores = pca.fit_transform(matrix_scaled)

    pc_names = [f"PC{i+1}" for i in range(actual_components)]

    components_list = [
        {pc: round(float(scores[i, j]), 4) for j, pc in enumerate(pc_names)}
        for i in range(n)
    ]

    loadings = {
        var: {pc: round(float(pca.components_[j, vi]), 4) for j, pc in enumerate(pc_names)}
        for vi, var in enumerate(variable_names)
    }

    evr = [round(float(v), 4) for v in pca.explained_variance_ratio_]
    cumulative = [round(float(np.sum(pca.explained_variance_ratio_[:i+1])), 4) for i in range(actual_components)]

    return {
        "explained_variance_ratio": evr,
        "cumulative_variance": cumulative,
        "n_components": actual_components,
        "n_observations": n,
        "variable_names": variable_names,
        "components": components_list,
        "loadings": loadings,
    }


def run_clustering(
    data: dict[str, list[float]],
    n_clusters: int = 3,
    linkage_method: str = "ward",
) -> dict | None:
    """
    Hierarchisches Clustering der Beobachtungen.

    data: {"variable_name": [value_per_participant], ...}

    Returns None wenn n < n_clusters oder < 2 Variablen.

    Returns:
    {
        "labels": list[int],         # Cluster-Label pro Beobachtung (0-indexed)
        "n_clusters": int,
        "n_observations": int,
        "cluster_sizes": dict[int, int],  # {cluster_id: count}
        "linkage_method": str,
    }
    """
    variable_names = list(data.keys())
    if len(variable_names) < 2:
        return None

    lengths = [len(v) for v in data.values()]
    if len(set(lengths)) > 1:
        return None

    n = lengths[0]
    actual_clusters = min(n_clusters, n)
    if n < actual_clusters or n < 2:
        return None

    matrix = np.array([data[v] for v in variable_names], dtype=float).T

    scaler = StandardScaler()
    matrix_scaled = scaler.fit_transform(matrix)

    clustering = AgglomerativeClustering(n_clusters=actual_clusters, linkage=linkage_method)
    labels = clustering.fit_predict(matrix_scaled).tolist()

    cluster_sizes = {}
    for label in labels:
        cluster_sizes[label] = cluster_sizes.get(label, 0) + 1

    return {
        "labels": labels,
        "n_clusters": actual_clusters,
        "n_observations": n,
        "cluster_sizes": cluster_sizes,
        "linkage_method": linkage_method,
    }
