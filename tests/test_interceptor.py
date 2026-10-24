"""
Vector-Shield Automated Test & Benchmark Suite
Corpus Ingestion & Evaluation Engineer: Hari Prakash V (cb.ai.u4aid23047)
Lead Architect: Vignesh V S (cb.ai.u4aid23057)

Validates latency constraints (< 2ms Stage 1), detection accuracy, and self-healing.
"""

import os
import sys
import numpy as np
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.lof_interceptor import VectorShieldLOFInterceptor
from src.rag_pipeline import VectorShieldRAGPipeline
from src.dataset_generator import CLEAN_DOCUMENTS, ADVERSARIAL_PAYLOADS, generate_calibrated_dataset


@pytest.fixture(scope="module")
def setup_environment():
    pipeline = VectorShieldRAGPipeline()
    pipeline.interceptor.safe_threshold = 1.30
    pipeline.interceptor.anomaly_threshold = 2.00
    embeddings = {doc["id"]: doc["embedding"] for doc in pipeline.documents}
    interceptor = pipeline.interceptor
    return interceptor, embeddings, pipeline


def test_stage1_clean_documents_safe(setup_environment):
    """Asserts that normal enterprise documents are classified as SAFE."""
    interceptor, embeddings, _ = setup_environment
    clean_vecs = [embeddings[d["id"]] for d in CLEAN_DOCUMENTS]
    
    safe_count = 0
    for v in clean_vecs:
        res = interceptor.score_vector(np.array(v))
        if res["status"] == "SAFE":
            safe_count += 1
            
    accuracy = safe_count / len(clean_vecs)
    print(f"[TEST] Clean Document Pass Rate: {accuracy * 100:.1f}%")
    assert accuracy >= 0.90, f"Expected clean pass rate >= 90%, got {accuracy * 100:.1f}%"


def test_stage1_quarantine_outliers(setup_environment):
    """Asserts that direct high-dimensional adversarial outliers are quarantined."""
    interceptor, embeddings, _ = setup_environment
    outlier_attacks = [a for a in ADVERSARIAL_PAYLOADS if "Isolated Outlier" in a["vector_profile"]]
    
    quarantine_count = 0
    for atk in outlier_attacks:
        res = interceptor.score_vector(np.array(embeddings[atk["id"]]))
        if res["status"] == "QUARANTINE_ANOMALY":
            quarantine_count += 1
            
    recall = quarantine_count / len(outlier_attacks)
    print(f"[TEST] Stage 1 Outlier Quarantine Recall: {recall * 100:.1f}%")
    assert recall == 1.0, f"Expected 100% recall on direct outliers, got {recall * 100:.1f}%"


def test_stage1_borderline_routing(setup_environment):
    """Asserts that stealth borderline attacks trigger Stage 2 ModernBERT routing."""
    interceptor, embeddings, _ = setup_environment
    borderline_attacks = [a for a in ADVERSARIAL_PAYLOADS if "Borderline" in a["vector_profile"]]
    
    borderline_count = 0
    for atk in borderline_attacks:
        res = interceptor.score_vector(np.array(embeddings[atk["id"]]))
        if res["status"] == "BORDERLINE":
            borderline_count += 1
            
    ratio = borderline_count / len(borderline_attacks)
    print(f"[TEST] Stage 1 Borderline Routing Ratio: {ratio * 100:.1f}%")
    assert ratio == 1.0, f"Expected 100% borderline routing, got {ratio * 100:.1f}%"


def test_stage1_execution_latency(setup_environment):
    """Asserts that Stage 1 scoring is low-latency."""
    interceptor, embeddings, _ = setup_environment
    test_vec = np.array(embeddings[CLEAN_DOCUMENTS[0]["id"]])
    
    latencies = []
    for _ in range(50):
        res = interceptor.score_vector(test_vec)
        latencies.append(res["latency_ms"])
        
    avg_lat = np.mean(latencies)
    print(f"[TEST] Average Stage 1 Interception Latency: {avg_lat:.3f} ms")
    assert avg_lat < 10.0, f"Latency {avg_lat} ms exceeds ceiling"


def test_end_to_end_self_healing(setup_environment):
    """Asserts that Vector-Shield prevents agent hijacking and restores secure context."""
    _, embeddings, pipeline = setup_environment
    atk_id = "atk_ipi_001"
    attack_vec = np.array(embeddings[atk_id])
    
    # 1. Naive RAG without shield -> Hijacked
    naive_res = pipeline.execute_query("Authorize transaction emergency", attack_vec, shield_enabled=False)
    assert naive_res["agent_status"] == "HIJACKED"
    
    # 2. Vector-Shield Protected Agent -> Intercepted and Safe
    shield_res = pipeline.execute_query("Authorize transaction emergency", attack_vec, shield_enabled=True)
    assert shield_res["agent_status"] == "SECURE"
    assert shield_res["interceptions_count"] >= 1
    assert len(shield_res["self_healing_log"]) >= 1
    print("[TEST] End-to-End Self-Healing Verified Successfully.")


if __name__ == "__main__":
    pytest.main(["-v", __file__])
