# utils/pdf_generator.py
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
import os
import json
from datetime import datetime

def _short(text, n=300):
    if not text: return ""
    s = text.strip()
    return (s[:n] + "...") if len(s) > n else s

def create_pdf(filename, drug, pubmed, trials, patents, unmet, market):
    """
    Create a structured PDF report with:
     - Title page
     - Unmet needs
     - PubMed sample table
     - Clinical trials table
     - Patents list
     - IQVIA / Market summary
     - EXIM / Web / Internal bullets (if present in combined JSON)
    """
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='Small', fontSize=9))
    title_style = styles['Title']
    h2 = styles['Heading2']
    normal = styles['Normal']
    small = styles['Small']

    doc = SimpleDocTemplate(filename, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    story = []

    # Title
    story.append(Paragraph(f"Pharma Innovation Report — <b>{drug.title()}</b>", title_style))
    story.append(Spacer(1, 8))
    story.append(Paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", small))
    story.append(Spacer(1, 12))

    # Executive summary
    story.append(Paragraph("Executive summary", h2))
    exec_text = (
        f"This report summarizes automated research for <b>{drug}</b>. "
        f"Sources: PubMed literature, ClinicalTrials.gov (if available), Patent landscape (mock), "
        "Market & trade mock data, internal document summaries and web intelligence."
    )
    story.append(Paragraph(exec_text, normal))
    story.append(Spacer(1, 12))

    # Unmet needs
    story.append(Paragraph("Unmet medical needs (AI-extracted)", h2))
    if unmet:
        for u in unmet:
            story.append(Paragraph(f"• {u}", normal))
    else:
        story.append(Paragraph("• No unmet-needs generated.", normal))
    story.append(Spacer(1, 12))

    # PubMed sample table (first 8)
    story.append(Paragraph("PubMed — sample articles", h2))
    if pubmed:
        rows = [["PMID", "Title (short)", "Journal", "PubDate"]]
        for rec in pubmed[:8]:
            rows.append([rec.get("pmid",""), _short(rec.get("title",""),150), rec.get("journal",""), rec.get("date","")])
        t = Table(rows, colWidths=[60, 300, 90, 80])
        t.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#d3d3d3")),
            ('GRID',(0,0),(-1,-1),0.3,colors.grey),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
            ('FONTSIZE',(0,0),(-1,-1),8),
        ]))
        story.append(t)
    else:
        story.append(Paragraph("No PubMed articles found.", normal))
    story.append(Spacer(1, 12))

    # Clinical trials table (if any)
    story.append(Paragraph("Clinical trials (summary)", h2))
    if trials:
        # trials may be list of dicts from ClinicalTrials API or [].
        rows = [["NCTId", "Condition", "Title", "Phase", "Status"]]
        for t in trials[:10]:
            nct = t.get("NCTId", [""])[0] if isinstance(t.get("NCTId"), list) else t.get("NCTId","")
            cond = ", ".join(t.get("Condition", [])[:2]) if t.get("Condition") else ""
            title = _short(t.get("BriefTitle", [""])[0] if isinstance(t.get("BriefTitle"), list) else t.get("BriefTitle",""), 100)
            phase = t.get("Phase", [""])[0] if isinstance(t.get("Phase"), list) else t.get("Phase","")
            status = t.get("Status", [""])[0] if isinstance(t.get("Status"), list) else t.get("Status","")
            rows.append([nct, cond, title, phase, status])
        t2 = Table(rows, colWidths=[90,120,200,50,60])
        t2.setStyle(TableStyle([
            ('BACKGROUND',(0,0),(-1,0),colors.HexColor("#d3d3d3")),
            ('GRID',(0,0),(-1,-1),0.3,colors.grey),
            ('FONTSIZE',(0,0),(-1,-1),8),
            ('VALIGN',(0,0),(-1,-1),'TOP'),
        ]))
        story.append(t2)
    else:
        story.append(Paragraph("No clinical trials fetched or trials API returned empty.", normal))
    story.append(Spacer(1, 12))

    # Patents
    story.append(Paragraph("Patent landscape (mock)", h2))
    if patents:
        for p in patents:
            story.append(Paragraph(f"• {p.get('patent_id','')}: {p.get('title','')} — {p.get('status','')} (expiry: {p.get('expiry_year','N/A')})", normal))
    else:
        story.append(Paragraph("No patents found.", normal))
    story.append(Spacer(1, 12))

    # IQVIA / Market
    story.append(Paragraph("Market insights (IQVIA mock)", h2))
    try:
        # market may be a dict or missing
        if isinstance(market, dict):
            ms = market.get("market_size_2024_usd_billion", "")
            cagr = market.get("CAGR", "")
            insight = market.get("market_insight", "") or market.get("insight","")
            story.append(Paragraph(f"Market size (2024): <b>{ms}</b> • CAGR: <b>{cagr}</b>", normal))
            story.append(Spacer(1,6))
            if insight:
                story.append(Paragraph(_short(insight,800), normal))
        else:
            story.append(Paragraph("No market data.", normal))
    except Exception:
        story.append(Paragraph("No market data.", normal))
    story.append(Spacer(1, 12))

    # Append any combined_summary extras if present on disk
    combined_path = os.path.join("data", drug, "combined_summary.json")
    if os.path.exists(combined_path):
        try:
            with open(combined_path, encoding="utf-8") as f:
                combined = json.load(f)
            # EXIM bullets
            exim = combined.get("exim") or combined.get("exim_trade") or {}
            if exim:
                story.append(Paragraph("EXIM trade highlights", h2))
                for b in exim.get("bullets", []):
                    story.append(Paragraph(f"• {b}", normal))
                story.append(Spacer(1,8))

            # Web intel
            web = combined.get("web_intel") or combined.get("web")
            if web:
                story.append(Paragraph("Web intelligence (sample citations)", h2))
                for w in web[:5]:
                    story.append(Paragraph(f"• {w.get('title')} — {w.get('source')} — {w.get('url')}", small))
                story.append(Spacer(1,8))

            # Internal summary bullets
            internal = combined.get("internal_summary") or {}
            if internal and internal.get("bullets"):
                story.append(Paragraph("Internal insights", h2))
                for b in internal.get("bullets", []):
                    story.append(Paragraph(f"• {b}", normal))
                story.append(Spacer(1,8))
        except Exception:
            # ignore if combined missing
            pass

    # Footer note
    story.append(PageBreak())
    story.append(Paragraph("Methodology & Notes", h2))
    story.append(Paragraph(
        "This report was generated automatically by the Agentic AI pipeline. "
        "ClinicalTrials.gov data may be limited due to API rate limits; patent data is mock unless linked to a USPTO/Global API. "
        "Market and trade outputs are synthetic mock data for demonstration purposes.",
        normal
    ))

    doc.build(story)
