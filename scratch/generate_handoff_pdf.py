"""
Vector-Shield: Master Project Handoff & Complete System Guide PDF Generator
Compiles the entire project context, architecture, defense scripts, training guides,
and user chat history into a publication-quality PDF.
"""

import os
import sys
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak, KeepTogether, HRFlowable
)
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.pdfgen import canvas

PDF_FILENAME = "VectorShield_Complete_Handoff_and_Chat_Guide.pdf"

class NumberedCanvas(canvas.Canvas):
    def __init__(self, *args, **kwargs):
        super(NumberedCanvas, self).__init__(*args, **kwargs)
        self._saved_page_states = []

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_page_decorations(num_pages)
            super(NumberedCanvas, self).showPage()
        super(NumberedCanvas, self).save()

    def draw_page_decorations(self, page_count):
        self.saveState()
        self.setFont("Helvetica", 8)
        self.setFillColor(colors.HexColor("#718096"))
        
        # Header (on pages > 1)
        if self._pageNumber > 1:
            self.drawString(54, 750, "Vector-Shield: Master Project Architecture & System Handoff Guide")
            self.setStrokeColor(colors.HexColor("#CBD5E1"))
            self.setLineWidth(0.5)
            self.line(54, 742, letter[0] - 54, 742)
        
        # Footer
        self.setStrokeColor(colors.HexColor("#CBD5E1"))
        self.setLineWidth(0.5)
        self.line(54, 45, letter[0] - 54, 45)
        self.drawString(54, 32, "School of Artificial Intelligence | AIDS Team 14 | Lead: Vignesh V S")
        page_str = f"Page {self._pageNumber} of {page_count}"
        self.drawRightString(letter[0] - 54, 32, page_str)
        self.restoreState()


def build_pdf():
    doc = SimpleDocTemplate(
        PDF_FILENAME,
        pagesize=letter,
        leftMargin=54,
        rightMargin=54,
        topMargin=54,
        bottomMargin=54
    )

    styles = getSampleStyleSheet()
    
    title_style = ParagraphStyle(
        'DocTitle',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=24,
        leading=28,
        textColor=colors.HexColor("#0F172A"),
        spaceAfter=8
    )

    subtitle_style = ParagraphStyle(
        'DocSub',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#2563EB"),
        spaceAfter=15
    )

    h1_style = ParagraphStyle(
        'Heading1',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=15,
        leading=19,
        textColor=colors.HexColor("#1E3A8A"),
        spaceBefore=14,
        spaceAfter=8,
        keepWithNext=True
    )

    h2_style = ParagraphStyle(
        'Heading2',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=12,
        leading=16,
        textColor=colors.HexColor("#0F172A"),
        spaceBefore=10,
        spaceAfter=5,
        keepWithNext=True
    )

    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=9.5,
        leading=13.5,
        textColor=colors.HexColor("#334155"),
        spaceAfter=7
    )

    code_style = ParagraphStyle(
        'CodeBlock',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        leading=10.5,
        textColor=colors.HexColor("#0F172A"),
        backColor=colors.HexColor("#F1F5F9"),
        borderPadding=6,
        spaceAfter=8
    )

    table_cell = ParagraphStyle(
        'TableCell',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.HexColor("#1E293B")
    )

    table_header = ParagraphStyle(
        'TableHeader',
        parent=styles['Normal'],
        fontName='Helvetica-Bold',
        fontSize=8.5,
        leading=11.5,
        textColor=colors.white
    )

    elements = []

    # Title Block
    elements.append(Paragraph("Vector-Shield: Master Project Handoff & System Guide", title_style))
    elements.append(Paragraph("Sub-2ms Dual-Stage Neuro-Symbolic Middleware for Defending Agentic RAG Against Indirect Prompt Injections", subtitle_style))
    elements.append(HRFlowable(width="100%", thickness=1.5, color=colors.HexColor("#2563EB"), spaceAfter=15))

    # Meta Table
    meta_data = [
        [Paragraph("<b>Project:</b> Vector-Shield (AI Security Middleware)", table_cell), Paragraph("<b>Institution:</b> Amrita Vishwa Vidyapeetham", table_cell)],
        [Paragraph("<b>Lead Architect:</b> Vignesh V S (cb.ai.u4aid23057)", table_cell), Paragraph("<b>Department:</b> School of AI & Data Science", table_cell)],
        [Paragraph("<b>Team Members:</b> Karthick Ruban, Sanjay Senthil, Hari Prakash", table_cell), Paragraph("<b>Supervisor:</b> Dr. Lekshmi CR", table_cell)],
        [Paragraph("<b>Repository:</b> github.com/VigneshVS2005/Vectorshield", table_cell), Paragraph("<b>Live Cockpit:</b> vectorshield.streamlit.app", table_cell)]
    ]
    t_meta = Table(meta_data, colWidths=[250, 250])
    t_meta.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.HexColor("#F8FAFC")),
        ('BOX', (0,0), (-1,-1), 1, colors.HexColor("#E2E8F0")),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
        ('TOPPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_meta)
    elements.append(Spacer(1, 15))

    # Section 1: Executive Summary & Kid Explanation
    elements.append(Paragraph("1. Executive Summary & Plain-Language Explanation", h1_style))
    elements.append(Paragraph(
        "<b>What is this project?</b> Vector-Shield is an enterprise cybersecurity firewall placed between an AI's memory (Vector Database) and the AI's brain (LLM). "
        "In modern enterprise AI systems (Retrieval-Augmented Generation / RAG), attackers don't attack the chat box directly. Instead, they hide malicious instructions inside vendor invoices, resumes, or emails (Indirect Prompt Injection). "
        "When an innocent employee queries the system, the vector database fetches that poisoned chunk, and the AI executes the attacker's commands (such as wire fraud or credential theft).",
        body_style
    ))
    elements.append(Paragraph(
        "<b>The Analogy (The King and The Food Taster):</b> The LLM is a King who reads scrolls from a library. The attacker slips a poisoned scroll into the archives. "
        "Vector-Shield acts as the Royal Food Taster: before the King touches any scroll, Vector-Shield scans its chemical signature (vector density) in <b>1.4 milliseconds</b>. "
        "If it smells like poison, Vector-Shield burns the scroll, grabs a clean backup, and the King answers the citizen safely.",
        body_style
    ))

    # Section 2: Why Existing Tools Fail & Novel Contributions
    elements.append(Paragraph("2. Why Existing GenAI Defenses Fail & Novel Contributions", h1_style))
    elements.append(Paragraph(
        "Examiners frequently ask: <i>'Why not just use Llama Guard, NeMo Guardrails, or OpenAI Moderation?'</i> The table below outlines the core technical defense:",
        body_style
    ))

    comp_data = [
        [Paragraph("Dimension", table_header), Paragraph("Standard LLM Guards (Llama Guard / NeMo)", table_header), Paragraph("Vector-Shield (Our System)", table_header)],
        [Paragraph("Inspection Layer", table_cell), Paragraph("Text Generation Layer (calls secondary LLM)", table_cell), Paragraph("High-Dimensional Vector Space (Pre-LLM)", table_cell)],
        [Paragraph("Latency Added", table_cell), Paragraph("800 ms to 2,500 ms per chunk (Destroys UX)", table_cell), Paragraph("1.2 ms to 1.8 ms per vector (1,000x faster)", table_cell)],
        [Paragraph("Token Cost", table_cell), Paragraph("High ($$$ pay tokens for every chunk)", table_cell), Paragraph("Zero Token Cost ($0 purely local math)", table_cell)],
        [Paragraph("Evasion Resistance", table_cell), Paragraph("Bypassed by Base64, leetspeak, hypotheticals", table_cell), Paragraph("Catches dense semantic clustering anomalies", table_cell)],
        [Paragraph("Failure Recovery", table_cell), Paragraph("Hard Refusal: 'I cannot answer this'", table_cell), Paragraph("Autonomous Self-Healing LangGraph Rewind", table_cell)]
    ]
    t_comp = Table(comp_data, colWidths=[90, 205, 205])
    t_comp.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor("#1E3A8A")),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor("#CBD5E1")),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor("#F8FAFC")]),
        ('TOPPADDING', (0,0), (-1,-1), 5),
        ('BOTTOMPADDING', (0,0), (-1,-1), 5),
    ]))
    elements.append(t_comp)
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Key Research Novelties:", h2_style))
    elements.append(Paragraph("<b>1. Cosine Domain-Centroid Density Scaling:</b> Standard Euclidean LOF fails in high-dimensional sentence spaces due to the Curse of Dimensionality (all normalized vectors have distance approx sqrt(2)). We developed an angular scaling formula combining k-NN density with cosine deviation from the domain centroid.", body_style))
    elements.append(Paragraph("<b>2. Sub-2ms In-Retrieval Quarantine:</b> Neutralizes payloads before prompt synthesis, eliminating GPU memory leaks and prompt hijacking.", body_style))
    elements.append(Paragraph("<b>3. Stateful Graph Recovery:</b> Instead of hard errors, compiled LangGraph loops purge poisoned candidates and re-retrieve clean context.", body_style))

    # Page Break for Architecture & UI
    elements.append(PageBreak())

    # Section 3: Productization & UI Architecture
    elements.append(Paragraph("3. Productization Architecture & Streamlit UI Guide", h1_style))
    elements.append(Paragraph(
        "Vector-Shield is engineered as a commercial enterprise B2B middleware. It deploys as a containerized sidecar or python package (pip install vector-shield) between client vector databases and LLM backends.",
        body_style
    ))

    elements.append(Paragraph("Streamlit Security Cockpit Tabs:", h2_style))
    elements.append(Paragraph("• <b>Tab 1: Live Attack Simulator:</b> Allows testing corporate queries vs. Garak injections with a live Toggle Shield switch demonstrating exploit execution vs. secure sanitization.", body_style))
    elements.append(Paragraph("• <b>Tab 2: Stage 2 ModernBERT Inspection:</b> Deep token-level sequence classification (149M params) resolving borderline ambiguity (1.30 < LOF < 2.50) with probability gauges.", body_style))
    elements.append(Paragraph("• <b>Tab 3: Dynamic Doc/PDF Ingestion Studio:</b> Live ingestion engine that embeds, checks LOF density, and blocks poisoned documents at ingestion time before they reach the database.", body_style))
    elements.append(Paragraph("• <b>Tab 4: 3D Vector Hyperspace:</b> Interactive 3D PCA scatter plot showing clean corporate clusters (green) vs. outlier injection vectors (red).", body_style))
    elements.append(Paragraph("• <b>Tab 5: Architecture & SaaS Topology:</b> Mathematical formulations and enterprise deployment diagrams.", body_style))
    elements.append(Paragraph("• <b>Tab 6: SIEM Webhook & Telemetry:</b> Integration with Splunk, Datadog, Slack, and Syslog with real-time incident auditing.", body_style))

    # Section 4: NVIDIA A100 GPU Training Guide
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("4. NVIDIA A100 GPU Cluster Training Guide", h1_style))
    elements.append(Paragraph(
        "To train the Stage 2 ModernBERT neural classifier on your A100 GPU node, run the following commands directly inside your JupyterLab terminal:",
        body_style
    ))

    cmd_text = (
        "# 1. Pull the repository\n"
        "cd Vectorshield\n"
        "git pull origin main\n\n"
        "# 2. Install dependencies\n"
        "pip install -r requirements.txt\n"
        "pip install accelerate\n\n"
        "# 3. Run scaled corpus generation\n"
        "python src/dataset_scaler.py\n\n"
        "# 4. Launch A100 GPU Training (Takes ~2 minutes)\n"
        "python src/train_stage2_modernbert.py --batch_size 16 --epochs 3 --fp16"
    )
    elements.append(Paragraph(cmd_text.replace("\n", "<br/>"), code_style))

    # Section 5: Master Prompt for AGY CLI
    elements.append(Spacer(1, 10))
    elements.append(Paragraph("5. Master AGY Prompt for Headless Execution on A100", h1_style))
    elements.append(Paragraph(
        "When you log into your A100 JupyterLab node and start the `agy` CLI, copy and paste the master prompt below. It will autonomously execute data generation, train the model, verify checkpoint weights, run pytest suites, and push results back to GitHub.",
        body_style
    ))

    master_prompt = (
        "AGY MASTER DIRECTIVE: You are running on an NVIDIA A100 GPU node inside the Vectorshield repository. "
        "Execute the following sequence autonomously without stopping:\n"
        "1. Verify GPU availability: python -c 'import torch; assert torch.cuda.is_available(); print(torch.cuda.get_device_name(0))'\n"
        "2. Run dataset scaling: python src/dataset_scaler.py\n"
        "3. Train Stage 2 ModernBERT: python src/train_stage2_modernbert.py --batch_size 16 --epochs 3 --fp16\n"
        "4. Verify saved weights in models/stage2_modernbert/\n"
        "5. Run full test suite: pytest tests/\n"
        "6. Stage, commit, and push updated weights/metrics to GitHub origin main: git add . && git commit -m 'feat: complete Stage 2 ModernBERT fine-tuning on A100' && git push origin main\n"
        "Provide final benchmark telemetry upon completion."
    )
    elements.append(Paragraph(master_prompt.replace("\n", "<br/>"), code_style))

    doc.build(elements, canvasmaker=NumberedCanvas)
    print(f"[PDF Generator] Successfully compiled {PDF_FILENAME}")

if __name__ == "__main__":
    build_pdf()
