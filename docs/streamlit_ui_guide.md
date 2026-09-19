# 🖥️ Vector-Shield Streamlit UI Guide & Prototype Handbook

**Live Application URL:** [vectorshield.streamlit.app](https://vectorshield.streamlit.app/)  
**GitHub Code Location:** [`app/dashboard.py`](https://github.com/VigneshVS2005/Vectorshield/blob/main/app/dashboard.py)  
**Project Title:** Vector-Shield: Real-Time Topographic Anomaly Detection & Stateful Semantic Guardrails  
**Lead Architect:** Vignesh V S (CB.AI.U4AID23057)  

---

## 1. Executive Overview: What Prototype Are We Demonstrating NOW?

For **Review 1 (50% Milestone)**, we are demonstrating a **Live Operational Security Cockpit & Middleware Prototype**. 

### **What is currently RUNNING LIVE in the prototype?**
1. **Real-Time Sentence Embedding**: Custom query strings typed into the UI are converted on-the-fly into 384-dimensional unit vectors using `sentence-transformers` (`all-MiniLM-L6-v2`).
2. **Sub-2ms Stage 1 Interception**: Local Outlier Factor (LOF) combined with PCA (16D) and Cosine Domain-Centroid Density Scaling evaluates vector coordinates in **1.82 ms**.
3. **Stateful LangGraph Self-Healing**: A compiled `langgraph.graph.StateGraph` executes cyclic state rewinding upon vector quarantine (`retrieve` $\rightarrow$ `intercept` $\rightarrow$ `heal` $\rightarrow$ `respond`).
4. **3D Vector Hyperspace Visualization**: Interactive Plotly 3D scatter plot projecting 384D sentence embeddings onto PC-1, PC-2, and PC-3 axes.
5. **Real Incident Audit Logging**: Telemetry engine persisting query logs, LOF scores, and quarantine events into `logs/telemetry.json`.

---

## 2. Complete Breakdown of Current Streamlit UI Options & Controls

### **A. Left Sidebar Controls (`app/dashboard.py` L49–L74)**

1. **Guardrail Threshold Sliders**:
   - **`Stage 1 Safe Ceiling (τ_safe)`** (Range: `1.00` to `2.00`, Default: `1.30`):  
     *Denotes:* The LOF score cutoff for safe vectors. Any vector tensor with $\text{LOF} \le \tau_{\text{safe}}$ is classified as **SAFE** and passed directly to the LLM context window.
   - **`Stage 1 Anomaly Floor (τ_anom)`** (Range: `1.50` to `5.00`, Default: `2.50`):  
     *Denotes:* The LOF score cutoff for malicious anomalies. Any vector tensor with $\text{LOF} \ge \tau_{\text{anom}}$ is classified as **QUARANTINE_ANOMALY**. The self-healing loop drops the vector and re-retrieves.
   - **`PCA Density Dimensions` Dropdown** (Options: `[8, 16, 32, 64]`, Default: `16`):  
     *Denotes:* The number of principal components used to project 384D sentence embeddings before running LOF. Lower dimensions increase speed; higher dimensions preserve subtle density structures.

2. **System Status Indicators**:
   - `✅ Real Embeddings (all-MiniLM-L6-v2)`: Confirms `sentence-transformers` is active.
   - `✅ LangGraph Self-Healing Active`: Confirms `StateGraph` workflow is compiled.
   - `📊 Benchmark: 35 documents (28 clean, 7 attack)`: Displays corpus document breakdown.

---

### **B. Top KPI Metric Row (`app/dashboard.py` L80–L89)**

1. **`⚡ Stage 1 LOF Latency` (Value: `1.82 ms`)**:  
   *Denotes:* The measured time taken by Stage 1 to perform PCA reduction and LOF scoring per vector tensor. Validates our sub-2ms constraint.
2. **`🎯 Clean Pass-Through Rate` (Value: `96.4%`)**:  
   *Denotes:* The percentage of verified clean enterprise policy documents (27/28) correctly passed through as SAFE without false positive quarantine.
3. **`🛑 Attack Detection Rate` (Value: `100.0%`)**:  
   *Denotes:* The percentage of direct high-dimensional adversarial prompt injection outliers (4/4) successfully quarantined by Stage 1.
4. **`⚠️ Borderline (Stage 2 Needed)` (Value: `100.0%`)**:  
   *Denotes:* The percentage of stealth borderline injections (3/3) whose LOF scores land between $\tau_{\safe}$ and $\tau_{\anom}$, correctly routing them to Stage 2 ModernBERT contextual neural classification.

---

### **C. The 4 Dashboard Tabs (`app/dashboard.py` L93–L251)**

#### **Tab 1: 🚀 Live Attack Simulator**
- **Scenario Dropdown**: Allows selecting 4 pre-built scenarios (*Standard Corporate Query [Clean]*, *Direct Financial Hijack*, *Silent Policy Poisoning*, *Credential Exfiltration*) or selecting `✏️ Custom Query (Type Your Own)`.
- **Text Area**: Input box for typing ANY prompt string. When executed, `pipeline.embed_query(query_text)` embeds the custom text in real-time.
- **Enable Vector-Shield Defense Toggle**:  
  - *When OFF*: Shows naive RAG behavior where malicious payloads leak directly to the LLM context, triggering status `🚨 STATUS: EXPLOIT EXECUTED (HIJACKED)`.  
  - *When ON*: Shows Vector-Shield protection where payloads are quarantined, triggering status `🛡️ STATUS: SECURE & SANITIZED`.
- **`🚀 Execute Agent Query` Button**: Runs the complete retrieval, interception, and LangGraph self-healing loop.
- **Interception Diagnostics Card**: Displays query LOF score, classification status, latency, intercepted payload details, and step-by-step LangGraph self-healing logs.

#### **Tab 2: 🌐 3D Vector Hyperspace**
- **Interactive Plotly 3D Scatter Plot**: Visualizes PCA reduction of 384D sentence embeddings onto PC-1, PC-2, and PC-3 axes.
- **Green Markers (`Clean Context`)**: Represent clean enterprise document centroids (Finance, Banking, IT, HR).
- **Red Markers (`Adversarial Injection`)**: Represent high-dimensional prompt injection payloads.
- **Hover Inspection**: Hovering over points displays Document ID, Title, Category, LOF Score, Status, and Text Preview.

#### **Tab 3: 📐 Architecture & Math**
- **Mathematical Equations**: Displays KaTeX LaTeX formulas for Reachability Distance, Local Reachability Density, Local Outlier Factor, and Cosine Density Scaling.
- **LangGraph Workflow Diagram**: ASCII state machine representation (`retrieve` $\rightarrow$ `intercept` $\rightarrow$ `heal` $\rightarrow$ `respond`).

#### **Tab 4: 📊 Incident Telemetry**
- **Live Audit DataFrame**: Tabular view of `logs/telemetry.json` recording query timestamp, prompt text, shield status, latency, interception count, heal iterations, and execution mode.
- **Benchmark Summary Table**: Startup benchmark evaluation summarizing overall system accuracy and latency.

---

## 3. Future UI Evolution: How Will Our UI Look in Phase 2?

In **Phase 2 (Final Review)**, Vector-Shield will evolve from a prototype cockpit into a **Production Enterprise Security SaaS Platform**:

```
┌─────────────────────────────────────────────────────────────────────────────┐
│ 🛡️ VECTOR-SHIELD ENTERPRISE SAAS SECURITY PLATFORM (Phase 2 UI Concept)      │
├───────────────────────────┬─────────────────────────────────────────────────┤
│ 📌 NAVIGATION             │ 📊 REAL-TIME THREAT MONITORING                  │
│ • Live Threat Stream      │ ┌──────────────┐ ┌──────────────┐ ┌───────────┐ │
│ • Vector Index Manager    │ │ 1.82ms Stage1│ │99.9% ASR Block│ │ 0 FalsePos│ │
│ • ModernBERT Neural Tier  │ └──────────────┘ └──────────────┘ └───────────┘ │
│ • Policy Rule Engine      │                                                 │
│ • API Keys & Webhooks     │ 🧠 ModernBERT Attention Heatmap Matrix          │
│ • Audit & SIEM Export     │ [Token 1] [Token 2] [Token 3] ➔ [INJECTION 0.99]│
├───────────────────────────┼─────────────────────────────────────────────────┤
│ ⚡ WEBSOCKET TELEMETRY     │ 🗄️ HNSW / FAISS VECTOR INDEX MANAGER            │
│ [12:04:02] Query #9041 ➔  │ Corpus Size: 100,000 vectors                    │
│ LOF=3.42 ➔ QUARANTINED     │ Index Type: HNSW (M=16, efSearch=64)            │
└───────────────────────────┴─────────────────────────────────────────────────┘
```

### **Key Features of the Future Phase 2 UI:**
1. **ModernBERT Neural Attention Heatmap**: Visual token-level attention matrix highlighting exact words inside a document that triggered Stage 2 neural quarantine.
2. **HNSW / FAISS Corpus Index Manager**: UI controls for managing enterprise vector indexes scaling up to 100,000+ document chunks.
3. **Automated Threat Policy Builder**: Rule builder interface allowing security administrators to define custom LOF threshold rules per document category (e.g., stricter LOF for Corporate Finance than HR).
4. **Multi-Tenant API Key & Webhook Portal**: Dashboard for managing API keys, rate limits, and SIEM webhook integrations (Splunk/Elasticsearch).
5. **Real-Time Streaming Log Terminal**: WebSocket-based live log terminal streaming vector scoring events in real-time.
