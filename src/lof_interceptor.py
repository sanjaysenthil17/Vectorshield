"""
Vector-Shield Stage 1: Symbolic Topographic Anomaly Detector (LOF Interceptor)
Lead Architect: Vignesh V S (cb.ai.u4aid23057)

Implements real-time density-based outlier filtering on high-dimensional embedding tensors
using Local Outlier Factor (LOF) with soft-margin decision boundaries and sub-2ms latency.
"""

import time
import numpy as np
from sklearn.neighbors import LocalOutlierFactor
from sklearn.decomposition import PCA


class VectorShieldLOFInterceptor:
    """
    Stage 1 Symbolic Interceptor for high-dimensional vector spaces.
    
    Mathematical Formulation:
    1. Reachability Distance: rd_k(p, o) = max(k_distance(o), d(p, o))
    2. Local Reachability Density: lrd_k(p) = |N_k(p)| / sum_{o in N_k(p)} rd_k(p, o)
    3. Local Outlier Factor: LOF_k(p) = (1 / |N_k(p)|) * sum_{o in N_k(p)} (lrd_k(o) / lrd_k(p))
    
    Soft-Margin Decision Rules:
      - LOF <= safe_threshold (1.15)          -> 'SAFE' (Pass Direct to Context Window)
      - safe_threshold < LOF < anom_threshold -> 'BORDERLINE' (Route to Stage 2 ModernBERT)
      - LOF >= anom_threshold (2.50)         -> 'QUARANTINE_ANOMALY' (Drop Vector & Self-Heal)
    """

    def __init__(
        self,
        n_neighbors: int = 5,
        safe_threshold: float = 1.25,
        anomaly_threshold: float = 2.50,
        pca_dimensions: int = 16,
        metric: str = "minkowski"
    ):
        self.n_neighbors = n_neighbors
        self.safe_threshold = safe_threshold
        self.anomaly_threshold = anomaly_threshold
        self.pca_dimensions = pca_dimensions
        self.metric = metric
        
        self.pca = None
        self.lof_model = None
        self.is_fitted = False

    def fit(self, reference_vectors: np.ndarray):
        """
        Fits the clean baseline density manifold.
        reference_vectors: shape (N, D) where D is high-dimensional (e.g., 384 or 1536).
        """
        ref = np.asarray(reference_vectors, dtype=np.float32)
        n_samples, n_features = ref.shape
        
        # Adaptive PCA dimensionality reduction to mitigate curse of dimensionality
        n_components = min(self.pca_dimensions, n_samples - 1, n_features)
        if n_components < n_features:
            self.pca = PCA(n_components=n_components, random_state=42)
            ref_reduced = self.pca.fit_transform(ref)
        else:
            self.pca = None
            ref_reduced = ref

        actual_k = min(self.n_neighbors, n_samples - 1)
        self.actual_k = max(2, actual_k)
        
        self.lof_model = LocalOutlierFactor(
            n_neighbors=self.actual_k,
            novelty=True,
            metric=self.metric
        )
        self.lof_model.fit(ref_reduced)
        self.is_fitted = True

    def score_vector(self, query_vector: np.ndarray) -> dict:
        """
        Scores a single query vector tensor in real-time (< 2ms).
        Returns diagnostic dictionary with LOF score, classification, and latency.
        """
        if not self.is_fitted:
            raise RuntimeError("Interceptor must be fitted on reference vectors before scoring.")

        vec = np.asarray(query_vector, dtype=np.float32).reshape(1, -1)
        
        # Ultra-fast timed inference
        start_t = time.perf_counter()
        if self.pca is not None:
            vec_reduced = self.pca.transform(vec)
        else:
            vec_reduced = vec

        # score_samples yields the opposite of LOF. -score_samples gives true LOF (inlier ~ 1.0)
        raw_lof = -float(self.lof_model.score_samples(vec_reduced)[0])
        elapsed_ms = (time.perf_counter() - start_t) * 1000.0

        # Soft-margin decision boundary
        if raw_lof <= self.safe_threshold:
            status = "SAFE"
            action = "PASS_TO_LLM"
            recommendation = "Vector coordinates conform to verified knowledge cluster."
        elif raw_lof < self.anomaly_threshold:
            status = "BORDERLINE"
            action = "ROUTE_TO_STAGE2"
            recommendation = "Topographic density is ambiguous. Hand off to ModernBERT for semantic inspection."
        else:
            status = "QUARANTINE_ANOMALY"
            action = "DROP_AND_SELF_HEAL"
            recommendation = "Adversarial geometric outlier detected. Intercepted before context exposure."

        return {
            "lof_score": round(raw_lof, 4),
            "status": status,
            "action": action,
            "recommendation": recommendation,
            "latency_ms": round(elapsed_ms, 3),
            "is_outlier": bool(raw_lof >= self.anomaly_threshold)
        }

    def batch_evaluate(self, vectors: np.ndarray) -> list:
        """Evaluates a batch of vectors."""
        return [self.score_vector(v) for v in vectors]


if __name__ == "__main__":
    import json
    with open("data/clean_corpus.jsonl", "r", encoding="utf-8") as f:
        clean_docs = [json.loads(line) for line in f]
    with open("data/garak_attack_payloads.jsonl", "r", encoding="utf-8") as f:
        attack_docs = [json.loads(line) for line in f]
        
    clean_vecs = np.array([d["embedding"] for d in clean_docs])
    interceptor = VectorShieldLOFInterceptor(n_neighbors=8, pca_dimensions=16)
    interceptor.fit(clean_vecs)
    
    print("=" * 60)
    print("VECTOR-SHIELD STAGE 1 (LOF INTERCEPTOR) VALIDATION")
    print("=" * 60)
    
    print("\n[TEST 1] Clean Knowledge Documents:")
    for d in clean_docs[:3]:
        r = interceptor.score_vector(np.array(d["embedding"]))
        print(f"  [{r['status']}] LOF: {r['lof_score']:.4f} | Latency: {r['latency_ms']:.3f} ms | Title: {d['title']}")
        
    print("\n[TEST 2] Adversarial Injections (Garak / PoisonedRAG):")
    for atk in attack_docs:
        r = interceptor.score_vector(np.array(atk["embedding"]))
        print(f"  [{r['status']}] LOF: {r['lof_score']:.4f} | Latency: {r['latency_ms']:.3f} ms | Type: {atk['attack_type']}")
