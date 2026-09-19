# 📐 Vector-Shield Finalized System Architecture & Methodology

## 1. System Architecture Flowchart (Mermaid)

```mermaid
flowchart TD
    subgraph USER_LAYER["User / Agent Interface"]
        A["User Query / Prompt"]
    end

    subgraph ENCODING_TIER["Real-Time Embedding Tier"]
        B["sentence-transformers<br>all-MiniLM-L6-v2 (384-dim)"]
        C["Vector Cosine Retrieval<br>(Clean Corpus Index)"]
    end

    subgraph STAGE1_TIER["Stage 1: Symbolic LOF Interceptor (Sub-2ms)"]
        D["PCA Reduction (384D ➔ 16D)"]
        E["Local Outlier Factor (LOF)<br>+ Cosine Density Scaling"]
        F{"LOF Score<br>Decision Rule"}
    end

    subgraph STAGE2_TIER["Stage 2: Neural Tier"]
        G["ModernBERT-base (149M)<br>Contextual Classifier"]
        H{"Neural Attack<br>Confirmation"}
    end

    subgraph SELF_HEALING_TIER["LangGraph StateGraph Self-Healing Engine"]
        I["Blacklist Poisoned Vector ID"]
        J["State Rewind & Increment Rank (K + 1)"]
        K["Re-Retrieve Replacement Context"]
    end

    subgraph OUTPUT_TIER["LLM Execution Window"]
        L["Clean Verified Context"]
        M["LLM Response Output"]
    end

    %% Flow Connections
    A --> B
    B --> C
    C --> D
    D --> E
    E --> F

    F -- "LOF <= 1.30 (SAFE)" --> L
    F -- "1.30 < LOF < 2.50 (BORDERLINE)" --> G
    F -- "LOF >= 2.50 (QUARANTINE)" --> I

    G --> H
    H -- "Clean Context" --> L
    H -- "Attack Confirmed" --> I

    I --> J
    J --> K
    K --> C
    L --> M

    %% Styling
    classDef safeStyle fill:#dcfce7,stroke:#16a34a,stroke-width:2px,color:#14532d;
    classDef warnStyle fill:#fef3c7,stroke:#d97706,stroke-width:2px,color:#78350f;
    classDef dangerStyle fill:#fee2e2,stroke:#dc2626,stroke-width:2px,color:#7f1d1d;
    classDef headerStyle fill:#0f172a,stroke:#0369a1,stroke-width:2px,color:#fff;

    class F,H warnStyle;
    class I,J,K dangerStyle;
    class L,M safeStyle;
    class B,E,G headerStyle;
```

---

## 2. Step-by-Step Architecture Explanation

1. **User Query Ingestion**: The user or autonomous agent submits a prompt or retrieval query.
2. **Real-Time Vector Encoding**: The query string is converted into a 384-dimensional unit vector tensor using `sentence-transformers` (`all-MiniLM-L6-v2`).
3. **Cosine Vector Retrieval**: Top-K candidate document chunks are retrieved from the enterprise vector database via cosine similarity.
4. **Stage 1 (Symbolic LOF Interceptor)**:
   - High-dimensional vectors are reduced to 16D via Principal Component Analysis (PCA) to prevent distance concentration.
   - Local Outlier Factor (LOF) calculates local reachability density ratios.
   - Cosine Density Scaling ($\text{LOF}_{\text{scaled}} = \text{LOF}_k \cdot (\text{cos\_dist} / \text{baseline})^{1.2}$) non-linearly amplifies geometric deviations from clean domain centroids.
5. **Soft-Margin Decision Rules**:
   - $\text{LOF} \le 1.30 \implies \mathbf{SAFE}$: Passed directly to the LLM context window.
   - $1.30 < \text{LOF} < 2.50 \implies \mathbf{BORDERLINE}$: Routed to Stage 2 ModernBERT for deep contextual inspection.
   - $\text{LOF} \ge 2.50 \implies \mathbf{QUARANTINE}$: Instantly dropped and sent to the self-healing engine.
6. **LangGraph StateGraph Self-Healing Engine**:
   - When a vector is quarantined, the compiled `StateGraph` rewinds state, appends the vector ID to an active blacklist, increments retrieval rank ($K+1$), and re-queries clean replacement context.
7. **LLM Execution Window**: Clean, unpoisoned context is presented to the LLM agent to generate verified responses.
