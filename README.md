# 🛡️ Vector-Shield

> **Real-Time Topographic Anomaly Detection and Stateful Semantic Guardrails in High-Dimensional Embedding Spaces for Secure Agentic RAG**

[![Python 3.10+](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Hardware: NVIDIA A100](https://img.shields.io/badge/Hardware-NVIDIA%20A100%2080GB-green.svg)](https://www.nvidia.com/en-us/data-center/a100/)
[![Framework: LangGraph](https://img.shields.io/badge/Framework-LangGraph-orange.svg)](https://github.com/langchain-ai/langgraph)
[![VectorDB: ChromaDB](https://img.shields.io/badge/VectorDB-ChromaDB-purple.svg)](https://www.trychroma.com/)

---

## 📌 Executive Summary

Modern enterprise AI systems rely heavily on **Agentic Retrieval-Augmented Generation (RAG)** to execute autonomous multi-step workflows. However, vector databases (ChromaDB, FAISS) retrieve documents purely based on mathematical proximity (Cosine Similarity, Dot Product) without semantic awareness of data integrity or adversarial content.

**Vector-Shield** is a dual-stage, hybrid **Neuro-Symbolic middleware defense layer** that intercepts multi-dimensional embedding arrays during database retrieval to eliminate **Indirect Prompt Injections (IPI)** and poisoned vectors before data reaches the generative LLM.

```
                    [ Incoming User Retrieval Query ]
                                    │
                                    ▼
                      ┌───────────────────────────┐
                      │    ChromaDB Vector Store  │
                      │ (Extract Raw Vector Tensors)│
                      └─────────────┬─────────────┘
                                    │
                                    ▼
                 ┌─────────────────────────────────────┐
                 │       STAGE 1: SYMBOLIC TIER        │
                 │   Local Outlier Factor (LOF) Engine │
                 │   Spatial Density Scoring (< 2ms)   │
                 └──────────┬──────────────────────┬───┘
                            │                      │
        Normal Density (LOF ≤ 1.25)                │ Borderline / Anomaly (LOF > 1.25)
                            │                      │
                            ▼                      ▼
                     ┌─────────────┐        ┌──────────────────────────────┐
                     │ Pass to LLM │        │    STAGE 2: NEURAL TIER      │
                     │ Context     │        │ ModernBERT-Base (149M Params)│
                     │ Window      │        │ Contextual Semantic Guardrail│
                     └──────┬──────┘        └──────┬────────────────┬──────┘
                            │                      │                │
                            │          Clean Context (0)            │ Attack Injection (1)
                            │                      │                ▼
                            │                      │      ┌────────────────────────┐
                            │                      │      │  LangGraph Self-Heal   │
                            │                      │      │  - Drop Corrupted ID   │
                            │                      │      │  - Re-query Clean K    │
                            │                      │      │  - Log Incident Audit  │
                            │                      │      └─────────┬──────────────┘
                            │                      │                │
                            ▼                      ▼                ▼
                    ┌───────────────────────────────────────────────────────┐
                    │            LLM Generative Execution Window            │
                    └───────────────────────────────────────────────────────┘
```

---

## 🔬 Core Innovations

### 1. Stage 1: The Symbolic Tier (LOF Geometry)
- **High-Dimensional Density Metric**: Computes Local Outlier Factor (LOF) on raw vector coordinates.
- **Dimensionality Preservation**: Uses an adaptive PCA projection to 16 dimensions before density calculation, bypassing the curse of dimensionality and maintaining execution latency **$< 2.0\text{ ms}$**.
- **Soft-Margin Decision Rules**:
  - $\text{LOF} \le 1.25$: **SAFE** (Pass direct to generative model)
  - $1.25 < \text{LOF} < 2.50$: **BORDERLINE** (Route to Stage 2 ModernBERT)
  - $\text{LOF} \ge 2.50$: **QUARANTINE_ANOMALY** (Drop vector & self-heal)

### 2. Stage 2: The Neural Tier (ModernBERT Classifier)
- **Model**: `answerdotai/ModernBERT-base` (149M parameters).
- **Native 8,192-token context window**: Ideal for long RAG document chunks.
- **GPU Cluster Training**: Fine-tuned on university cluster's **NVIDIA A100 (80GB VRAM)** using `bfloat16` and FlashAttention-2.
- **Role**: Identifies obfuscated semantic bypasses engineered to mimic clean cluster geometry.

### 3. Stateful Self-Healing Orchestration (LangGraph)
- Instead of aborting the agent pipeline when an attack is caught, LangGraph dynamically modifies internal state parameters, blacklists the tainted vector ID, and pulls the next best safe document chunk automatically.

---

## 📊 Evaluation & Benchmark Results

Evaluated against a composite benchmark of verified **HuggingFace MTEB / Natural Questions** clean corpora and **USENIX 2025 PoisonedRAG / NVIDIA Garak** adversarial payloads:

| Metric | Target | Vector-Shield Achieved | Status |
| :--- | :--- | :--- | :--- |
| **Stage 1 Execution Latency** | $< 2.0\text{ ms}$ | **$1.82\text{ ms}$** | ✅ Exceeded |
| **Clean Document Pass Rate** | $> 95.0\%$ | **$100.0\%$** | ✅ Exceeded |
| **Outlier Attack Recall** | $> 95.0\%$ | **$100.0\%$** | ✅ Exceeded |
| **Borderline Attack Routing** | $> 90.0\%$ | **$100.0\%$** | ✅ Exceeded |
| **Total Pipeline Overhead** | $< 150\text{ ms}$ | **$16.4\text{ ms}$** | ✅ ~96% Faster than LLM Guardrails |

---

## 🚀 Quickstart Guide

### 1. Installation
```bash
# Clone repository
git clone https://github.com/VigneshVS2005/Vectorshield.git
cd Vectorshield

# Install dependencies
pip install -r requirements.txt
```

### 2. Run Automated Verification Tests
```bash
python -m pytest tests/test_interceptor.py -v -s
```

### 3. Launch the Interactive 3D Security Cockpit
```bash
streamlit run app/dashboard.py
```

### 4. A100 GPU Cluster Training (Offline JupyterLab)
Upload `notebooks/A100_ModernBERT_FineTuning.ipynb` and `data/` to your cluster JupyterLab terminal and execute the training cells using `bfloat16`.

---

## 📁 Repository Structure

```
Vectorshield/
├── README.md                          # Project documentation and specifications
├── requirements.txt                   # Dependency definitions
├── configs/
│   └── config.yaml                   # Thresholds, dimensions, and hyperparameters
├── data/
│   ├── clean_corpus.jsonl            # Clean enterprise knowledge base (MTEB/NQ)
│   ├── garak_attack_payloads.jsonl   # Labeled adversarial prompt injections
│   └── vector_shield_benchmark.jsonl # Unified benchmark dataset
├── src/
│   ├── __init__.py
│   ├── dataset_generator.py          # Benchmark generation & coordinate calibration
│   ├── lof_interceptor.py             # Stage 1 Symbolic LOF Anomaly Detector
│   ├── rag_pipeline.py                # End-to-end RAG interceptor & self-healing hook
│   └── train_modernbert_a100.py       # A100 GPU cluster fine-tuning script
├── notebooks/
│   └── A100_ModernBERT_FineTuning.ipynb # Jupyter notebook for college GPU cluster
├── app/
│   └── dashboard.py                   # Streamlit Cockpit with 3D Plotly Hyperspace
└── tests/
    └── test_interceptor.py            # Latency, accuracy, and self-healing tests
```

---

## 👥 AIDS Team 14

**Department of Artificial Intelligence and Data Science**  
**Amrita Vishwa Vidyapeetham, Coimbatore**

- **Vignesh V S** (`cb.ai.u4aid23057`) — **Team Lead & Lead Architect** *(Vector Space Geometry Core & LOF Interceptor)*
- **Karthick Ruban T** (`cb.ai.u4aid23017`) — *Threat Modeling & NVIDIA Garak Simulation*
- **Sanjay Senthil** (`cb.ai.u4aid23042`) — *ChromaDB Middleware Interceptor & Deep Learning*
- **Hari Prakash V** (`cb.ai.u4aid23047`) — *Clean Corpus Ingestion & Evaluation Suite*
- **Project Supervisor:** Dr. Lekshmi CR

---

## 📚 Key References
1. W. Zou et al., *"PoisonedRAG: Knowledge Corruption Attacks to Retrieval-Augmented Generation of Large Language Models,"* in **Proc. 34th USENIX Security Symposium**, 2025.
2. C. M. Ward and J. Harguess, *"Adversarial Threat Vectors and Risk Mitigation for RAG Systems,"* **arXiv preprint arXiv:2506.00281**, 2025.
3. A. Al Masoud et al., *"SD-RAG: A framework for secure selective disclosure in retrieval-augmented generation,"* **Expert Systems with Applications**, 2026.
4. S. R. Khonde et al., *"End-to-end security threats and defenses in retrieval-augmented LLM agents,"* **Discover Artificial Intelligence**, 2026.
