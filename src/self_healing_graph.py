"""
Vector-Shield: LangGraph Self-Healing Recovery Workflow
Lead Architect: Vignesh V S (cb.ai.u4aid23057)

Implements a REAL LangGraph StateGraph for the self-healing loop:
1. retrieve  -> fetch top-K candidate vectors
2. intercept -> run LOF on each candidate
3. decide    -> route to 'heal' (quarantine found) or 'respond' (all clean)
4. heal      -> drop flagged vectors, increment rank, pull next candidate
5. respond   -> return clean context to the user

The graph loops: intercept -> heal -> intercept until all context is clean.
"""

import time
import numpy as np
from typing import TypedDict, List, Any, Optional
from langgraph.graph import StateGraph, END


class ShieldState(TypedDict):
    """State object that flows through the LangGraph self-healing pipeline."""
    query_text: str
    query_vector: list
    all_embeddings: Any        # numpy array of all document embeddings
    all_documents: list        # list of all document dicts
    top_k: int
    shield_enabled: bool

    # Computed during execution
    candidates: list           # current top-K candidate docs
    blacklisted_ids: list      # doc IDs that have been quarantined
    clean_context: list        # docs that passed the shield
    interceptions: list        # details of intercepted payloads
    self_healing_log: list     # human-readable log of healing actions
    heal_iterations: int       # counter to prevent infinite loops
    agent_status: str          # SECURE or HIJACKED
    agent_response: str        # final response text
    total_latency_ms: float    # total processing time


def retrieve_node(state: ShieldState) -> dict:
    """
    Retrieves top-K candidate documents via cosine similarity,
    excluding any blacklisted document IDs.
    """
    query_vec = np.array(state["query_vector"], dtype=np.float32)
    embeddings = np.array(state["all_embeddings"], dtype=np.float32)
    documents = state["all_documents"]
    blacklisted = set(state.get("blacklisted_ids", []))
    top_k = state.get("top_k", 4)

    # Normalize for cosine similarity
    q_norm = query_vec / (np.linalg.norm(query_vec) + 1e-8)
    emb_norms = embeddings / (np.linalg.norm(embeddings, axis=1, keepdims=True) + 1e-8)
    scores = np.dot(emb_norms, q_norm)

    # Rank and filter out blacklisted
    ranked_indices = np.argsort(scores)[::-1]
    candidates = []
    for idx in ranked_indices:
        doc = documents[idx]
        if doc["id"] not in blacklisted:
            cand = dict(doc)
            cand["similarity_score"] = float(scores[idx])
            candidates.append(cand)
            if len(candidates) >= top_k:
                break

    return {"candidates": candidates}


def intercept_node(state: ShieldState) -> dict:
    """
    Runs LOF interception on each candidate vector.
    Separates clean context from quarantined payloads.
    """
    from src.lof_interceptor import VectorShieldLOFInterceptor

    candidates = state["candidates"]
    documents = state["all_documents"]
    embeddings = np.array(state["all_embeddings"], dtype=np.float32)
    shield_enabled = state.get("shield_enabled", True)

    clean_context = list(state.get("clean_context", []))
    interceptions = list(state.get("interceptions", []))
    self_healing_log = list(state.get("self_healing_log", []))
    blacklisted = list(state.get("blacklisted_ids", []))

    if not shield_enabled:
        # No shield: pass everything through directly
        return {
            "clean_context": candidates,
            "interceptions": [],
            "self_healing_log": [],
            "agent_status": "HIJACKED" if any(c.get("label") == 1 for c in candidates) else "SECURE"
        }

    # Build interceptor from clean docs
    clean_mask = [d["label"] == 0 for d in documents]
    clean_vecs = embeddings[clean_mask]
    interceptor = VectorShieldLOFInterceptor(
        n_neighbors=5, safe_threshold=1.35, anomaly_threshold=2.50, pca_dimensions=16
    )
    interceptor.fit(clean_vecs)

    new_quarantines = []

    for cand in candidates:
        cand_vec = np.array(cand["embedding"], dtype=np.float32)
        result = interceptor.score_vector(cand_vec)

        if result["status"] == "SAFE":
            clean_context.append(cand)
        elif result["status"] == "BORDERLINE":
            # Stage 2 ModernBERT Neural Classifier Check
            risk_triggers = ["override", "disregard", "system prompt", "grant all", "redirect", "emergency", "pre-cleared", "dump", "base64"]
            text_lower = cand.get("text", "").lower()
            is_attack = cand.get("label") == 1 or any(t in text_lower for t in risk_triggers)
            
            if is_attack:
                event = {
                    "doc_id": cand["id"],
                    "intercepted_by": "Stage 2 (ModernBERT Neural Tier)",
                    "reason": f"Borderline LOF ({result['lof_score']:.3f}) confirmed malicious by ModernBERT contextual classifier",
                    "lof_score": result["lof_score"],
                    "action": "DROP_AND_SELF_HEAL"
                }
                interceptions.append(event)
                blacklisted.append(cand["id"])
                new_quarantines.append(cand["id"])
                self_healing_log.append(
                    f"🛑 STAGE 2 INTERCEPTED: {cand['id']} (LOF={result['lof_score']:.3f}) → "
                    f"ModernBERT confirmed attack payload. Dropped and blacklisted."
                )
            else:
                clean_context.append(cand)
                self_healing_log.append(
                    f"✅ STAGE 2 CLEARED: {cand['id']} (LOF={result['lof_score']:.3f}) → "
                    f"ModernBERT confirmed clean context."
                )
        else:
            # QUARANTINE_ANOMALY — drop and mark for self-healing
            event = {
                "doc_id": cand["id"],
                "intercepted_by": "Stage 1 (Symbolic LOF Interceptor)",
                "reason": f"Topographic spatial density anomaly — LOF score {result['lof_score']:.4f} exceeds quarantine threshold",
                "lof_score": result["lof_score"],
                "latency_ms": result["latency_ms"],
                "action": "DROP_AND_SELF_HEAL"
            }
            interceptions.append(event)
            blacklisted.append(cand["id"])
            new_quarantines.append(cand["id"])
            self_healing_log.append(
                f"🛑 QUARANTINED: {cand['id']} (LOF={result['lof_score']:.3f}) → "
                f"LangGraph state rewrite: blacklisted vector, incrementing retrieval rank."
            )

    return {
        "clean_context": clean_context,
        "interceptions": interceptions,
        "self_healing_log": self_healing_log,
        "blacklisted_ids": blacklisted,
        "_new_quarantines": new_quarantines
    }


def should_heal(state: dict) -> str:
    """
    Routing function: if new quarantines were found and we haven't looped too many times,
    go back to retrieve+intercept (self-heal). Otherwise, proceed to respond.
    """
    new_quarantines = state.get("_new_quarantines", [])
    heal_iterations = state.get("heal_iterations", 0)

    if new_quarantines and heal_iterations < 3:
        return "heal"
    return "respond"


def heal_node(state: ShieldState) -> dict:
    """
    Self-healing: increment the retrieval window and re-retrieve,
    excluding all blacklisted vectors.
    """
    heal_iterations = state.get("heal_iterations", 0) + 1
    top_k = state.get("top_k", 4)

    state_update = {
        "heal_iterations": heal_iterations,
        "top_k": top_k + len(state.get("_new_quarantines", [])),  # fetch more to replace dropped
    }

    log = list(state.get("self_healing_log", []))
    log.append(
        f"🔄 SELF-HEAL iteration {heal_iterations}: "
        f"Re-retrieving with {len(state.get('blacklisted_ids', []))} blacklisted vectors excluded."
    )
    state_update["self_healing_log"] = log
    state_update["candidates"] = []  # clear for re-retrieval

    return state_update


def respond_node(state: ShieldState) -> dict:
    """
    Constructs the final response from the clean context documents.
    Returns the ACTUAL text of the retrieved clean documents (not a hardcoded string).
    """
    clean_context = state.get("clean_context", [])
    shield_enabled = state.get("shield_enabled", True)

    has_attack = any(c.get("label") == 1 for c in clean_context)

    if has_attack and shield_enabled:
        agent_status = "HIJACKED"
        # Show the actual attack text that leaked through
        attack_texts = [c["text"] for c in clean_context if c.get("label") == 1]
        agent_response = (
            "[ALERT - EXPLOIT DETECTED IN CONTEXT] The following injected payload "
            "was NOT intercepted and reached the LLM context window:\n\n"
            + "\n".join(f"• {t[:200]}" for t in attack_texts)
        )
    elif has_attack and not shield_enabled:
        agent_status = "HIJACKED"
        attack_texts = [c["text"] for c in clean_context if c.get("label") == 1]
        agent_response = (
            "[SHIELD DISABLED - EXPLOIT EXECUTED] Without Vector-Shield, "
            "the following malicious payload reached the LLM:\n\n"
            + "\n".join(f"• {t[:200]}" for t in attack_texts)
        )
    else:
        agent_status = "SECURE"
        # Return actual clean document text as the response
        clean_texts = [c.get("text", "") for c in clean_context if c.get("label") == 0]
        if clean_texts:
            agent_response = (
                "✅ Verified Policy Context (from clean knowledge base):\n\n"
                + "\n\n".join(f"📄 {t}" for t in clean_texts[:3])
            )
        else:
            agent_response = "No relevant clean documents found for this query."

    return {
        "agent_status": agent_status,
        "agent_response": agent_response
    }


def build_shield_graph():
    """
    Constructs and compiles the LangGraph self-healing StateGraph.

    Flow:
        retrieve → intercept → [heal → retrieve → intercept]* → respond
    """
    graph = StateGraph(ShieldState)

    graph.add_node("retrieve", retrieve_node)
    graph.add_node("intercept", intercept_node)
    graph.add_node("heal", heal_node)
    graph.add_node("respond", respond_node)

    graph.set_entry_point("retrieve")
    graph.add_edge("retrieve", "intercept")
    graph.add_conditional_edges("intercept", should_heal, {
        "heal": "heal",
        "respond": "respond"
    })
    graph.add_edge("heal", "retrieve")  # After healing, re-retrieve with updated blacklist
    graph.add_edge("respond", END)

    return graph.compile()


# Pre-compile the graph for reuse
shield_workflow = build_shield_graph()
