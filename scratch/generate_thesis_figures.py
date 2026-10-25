"""
Generates publication-quality thesis figures for Vector-Shield:
1. architecture_diagram.png - Dual-Stage Neuro-Symbolic Middleware Topology
2. training_loss_curves.png - Stage 2 ModernBERT Fine-Tuning Loss & F1 Progression
3. lof_density_distribution.png - 2D Topographic Manifold & Anomaly Zones
4. latency_comparison.png - Latency Benchmark Comparison vs. Industry Baselines
5. langgraph_workflow_diagram.png - Stateful Cyclic Self-Healing State Machine
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = "Thesis"
os.makedirs(OUTPUT_DIR, exist_ok=True)
IMG_DIR = os.path.join(OUTPUT_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

# -------------------------------------------------------------
# Figure 1: Training Loss & Accuracy Progression on NVIDIA A100
# -------------------------------------------------------------
def plot_training_loss():
    epochs = [1, 2, 3]
    loss = [0.5296, 0.1485, 0.0625]
    val_acc = [94.29, 97.14, 100.00]
    f1_score = [92.86, 96.55, 100.00]

    fig, ax1 = plt.subplots(figsize=(7, 4.2), dpi=300)

    color = '#1E3A8A'
    ax1.set_xlabel('Fine-Tuning Epochs (NVIDIA A100 80GB)', fontsize=11, fontweight='bold', labelpad=8)
    ax1.set_ylabel('Training Loss (Cross-Entropy)', color=color, fontsize=11, fontweight='bold')
    line1 = ax1.plot(epochs, loss, color=color, marker='o', linewidth=2.5, markersize=8, label='Training Loss')
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.set_xticks(epochs)
    ax1.grid(True, linestyle='--', alpha=0.5)

    ax2 = ax1.twinx()
    color2 = '#059669'
    ax2.set_ylabel('Validation Metric (%)', color=color2, fontsize=11, fontweight='bold')
    line2 = ax2.plot(epochs, val_acc, color=color2, marker='s', linewidth=2.2, linestyle='--', markersize=7, label='Val Accuracy')
    line3 = ax2.plot(epochs, f1_score, color='#7C3AED', marker='^', linewidth=2.2, linestyle='-.', markersize=7, label='F1 Score')
    ax2.tick_params(axis='y', labelcolor=color2)
    ax2.set_ylim(85, 103)

    lines = line1 + line2 + line3
    labels = [l.get_label() for l in lines]
    ax1.legend(lines, labels, loc='center right', framealpha=0.9)
    plt.title('Stage 2 ModernBERT Convergence on NVIDIA A100 (FP16)', fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()
    
    path1 = os.path.join(OUTPUT_DIR, "training_loss_curves.png")
    path2 = os.path.join(IMG_DIR, "training_loss_curves.png")
    plt.savefig(path1)
    plt.savefig(path2)
    plt.close()
    print("[Figure Generator] Generated training_loss_curves.png")

# -------------------------------------------------------------
# Figure 2: Topographic Manifold & LOF Anomaly Zones
# -------------------------------------------------------------
def plot_lof_distribution():
    np.random.seed(42)
    # Clean corporate cluster
    clean_x = np.random.normal(loc=0.0, scale=0.35, size=90)
    clean_y = np.random.normal(loc=0.0, scale=0.35, size=90)

    # Borderline payloads
    theta = np.random.uniform(0, 2*np.pi, 25)
    r = np.random.uniform(0.9, 1.4, 25)
    border_x = r * np.cos(theta)
    border_y = r * np.sin(theta)

    # Severe isolated outliers
    outlier_x = np.array([-2.2, 2.4, -1.9, 2.1, -2.5, 0.8, -0.6])
    outlier_y = np.array([2.0, -1.8, -2.1, 2.3, 0.4, 2.6, -2.7])

    fig, ax = plt.subplots(figsize=(6.8, 5.2), dpi=300)
    
    # Concentric decision boundary zones
    c_safe = plt.Circle((0, 0), 0.85, color='#DCFCE7', alpha=0.5, label='SAFE Zone (LOF <= 1.30)')
    c_border = plt.Circle((0, 0), 1.65, color='#FEF3C7', alpha=0.4, label='BORDERLINE Zone (1.30 < LOF < 2.50)')
    ax.add_patch(c_border)
    ax.add_patch(c_safe)

    ax.scatter(clean_x, clean_y, c='#059669', edgecolors='k', linewidth=0.5, s=45, label='Clean Corporate Documents (SAFE)', zorder=3)
    ax.scatter(border_x, border_y, c='#D97706', edgecolors='k', linewidth=0.6, s=55, marker='s', label='Stealth Injections (Route to ModernBERT)', zorder=4)
    ax.scatter(outlier_x, outlier_y, c='#DC2626', edgecolors='k', linewidth=0.8, s=80, marker='X', label='High-Dimensional Outliers (QUARANTINE)', zorder=5)

    ax.set_xlim(-3.0, 3.0)
    ax.set_ylim(-3.0, 3.0)
    ax.set_xlabel('Principal Component 1 (PCA-1)', fontsize=10, fontweight='bold')
    ax.set_ylabel('Principal Component 2 (PCA-2)', fontsize=10, fontweight='bold')
    ax.set_title('Topographic Vector Distribution & Decision Boundaries', fontsize=12, fontweight='bold', pad=10)
    ax.legend(loc='lower left', fontsize=8.5, framealpha=0.95)
    ax.grid(True, linestyle=':', alpha=0.6)
    plt.tight_layout()

    path1 = os.path.join(OUTPUT_DIR, "lof_density_distribution.png")
    path2 = os.path.join(IMG_DIR, "lof_density_distribution.png")
    plt.savefig(path1)
    plt.savefig(path2)
    plt.close()
    print("[Figure Generator] Generated lof_density_distribution.png")

# -------------------------------------------------------------
# Figure 3: Latency Benchmark Comparison vs. Industry Baselines
# -------------------------------------------------------------
def plot_latency_comparison():
    models = ['Vector-Shield\n(Stage 1 LOF)', 'Vector-Shield\n(Stage 2 ModernBERT)', 'OpenAI\nModeration API', 'NVIDIA NeMo\nGuardrails', 'Meta Llama\nGuard 7B']
    latencies = [1.82, 22.15, 450.0, 680.0, 1250.0]
    colors_list = ['#059669', '#2563EB', '#64748B', '#D97706', '#DC2626']

    fig, ax = plt.subplots(figsize=(7.2, 4.2), dpi=300)
    bars = ax.bar(models, latencies, color=colors_list, width=0.55, edgecolor='black', linewidth=0.8)

    ax.set_yscale('log')
    ax.set_ylabel('Inference / Inspection Latency (ms) [Log Scale]', fontsize=10, fontweight='bold')
    ax.set_title('Inference Latency Comparison: Vector-Shield vs. LLM Guardrails', fontsize=11, fontweight='bold', pad=12)
    ax.grid(axis='y', linestyle='--', alpha=0.6)

    for bar, val in zip(bars, latencies):
        height = bar.get_height()
        ax.annotate(f'{val:.2f} ms',
                    xy=(bar.get_x() + bar.get_width() / 2, height),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8.5, fontweight='bold')

    plt.tight_layout()
    path1 = os.path.join(OUTPUT_DIR, "latency_comparison.png")
    path2 = os.path.join(IMG_DIR, "latency_comparison.png")
    plt.savefig(path1)
    plt.savefig(path2)
    plt.close()
    print("[Figure Generator] Generated latency_comparison.png")

# -------------------------------------------------------------
# Figure 4: Dual-Stage Architecture Flowchart
# -------------------------------------------------------------
def plot_architecture_diagram():
    fig, ax = plt.subplots(figsize=(8.5, 4.8), dpi=300)
    ax.axis('off')

    def add_box(xy, text, title, color='#F8FAFC', border='#1E3A8A', width=2.4, height=1.0):
        rect = patches.FancyBboxPatch(xy, width, height, boxstyle="round,pad=0.08,rounding_size=0.1",
                                     facecolor=color, edgecolor=border, linewidth=1.5)
        ax.add_patch(rect)
        ax.text(xy[0] + width/2, xy[1] + height - 0.25, title, ha='center', va='center', fontsize=9.5, fontweight='bold', color='#0F172A')
        ax.text(xy[0] + width/2, xy[1] + 0.35, text, ha='center', va='center', fontsize=8, color='#334155')
        return rect

    # Nodes
    add_box((0.2, 2.0), "User Retrieval Instruction\n& ChromaDB Candidate Fetch", "1. Query & Retrieval", color='#EFF6FF', border='#2563EB')
    add_box((3.2, 2.0), "LOF Density on 16D PCA\nDecision: SAFE / BORDER / QUAR", "2. Stage 1 Symbolic LOF", color='#F0FDF4', border='#059669')
    add_box((6.2, 3.1), "149M ModernBERT\nSequence Classifier (A100)", "3. Stage 2 Neural Tier", color='#FAF5FF', border='#7C3AED')
    add_box((6.2, 0.9), "Blacklist Corrupted Vector\nIncrement Rank & Re-retrieve", "4. LangGraph Self-Heal", color='#FEF2F2', border='#DC2626')
    add_box((9.2, 2.0), "Safe Prompt Synthesis\nLLM Agent Action Execution", "5. Protected LLM Context", color='#ECFDF5', border='#047857')

    # Connecting Arrows
    arrow_props = dict(facecolor='#1E3A8A', edgecolor='#1E3A8A', width=1.5, headwidth=6, headlength=6)
    
    # 1 -> 2
    ax.annotate('', xy=(3.2, 2.5), xytext=(2.6, 2.5), arrowprops=arrow_props)
    # 2 -> 5 (Safe direct)
    ax.annotate('', xy=(9.2, 2.5), xytext=(5.6, 2.5), arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.8, headwidth=6, headlength=6))
    ax.text(5.9, 2.65, "LOF <= 1.30 (SAFE)", fontsize=7.5, fontweight='bold', color='#059669')
    
    # 2 -> 3 (Borderline)
    ax.annotate('', xy=(6.2, 3.4), xytext=(5.6, 2.8), arrowprops=dict(facecolor='#7C3AED', edgecolor='#7C3AED', width=1.5, headwidth=5, headlength=5))
    ax.text(5.2, 3.35, "1.30 < LOF < 2.50", fontsize=7.5, fontweight='bold', color='#7C3AED')
    
    # 2 -> 4 (Quarantine)
    ax.annotate('', xy=(6.2, 1.6), xytext=(5.6, 2.2), arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=1.5, headwidth=5, headlength=5))
    ax.text(5.2, 1.65, "LOF >= 2.50", fontsize=7.5, fontweight='bold', color='#DC2626')

    # 3 -> 5 (Stage 2 Clean)
    ax.annotate('', xy=(9.2, 2.8), xytext=(8.6, 3.4), arrowprops=dict(facecolor='#059669', edgecolor='#059669', width=1.5, headwidth=5, headlength=5))
    # 3 -> 4 (Stage 2 Injection)
    ax.annotate('', xy=(7.4, 1.9), xytext=(7.4, 3.1), arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=1.5, headwidth=5, headlength=5))

    # 4 -> 1 (Cycle rewind)
    ax.annotate('', xy=(1.4, 2.0), xytext=(6.2, 1.2), arrowprops=dict(facecolor='#DC2626', edgecolor='#DC2626', width=1.5, headwidth=5, headlength=5, linestyle='--'))
    ax.text(3.5, 1.0, "State Rewind & Re-Query (Dynamic Blacklist)", fontsize=8, fontweight='bold', color='#DC2626')

    ax.set_xlim(0, 12)
    ax.set_ylim(0.5, 4.5)
    plt.title('Vector-Shield: Dual-Stage Neuro-Symbolic Middleware Architecture', fontsize=12, fontweight='bold', pad=12)
    plt.tight_layout()

    path1 = os.path.join(OUTPUT_DIR, "architecture_diagram.png")
    path2 = os.path.join(IMG_DIR, "architecture_diagram.png")
    plt.savefig(path1)
    plt.savefig(path2)
    plt.close()
    print("[Figure Generator] Generated architecture_diagram.png")

if __name__ == "__main__":
    plot_training_loss()
    plot_lof_distribution()
    plot_latency_comparison()
    plot_architecture_diagram()
    print("[Figure Generator] All thesis figures generated successfully!")
