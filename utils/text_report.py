# utils/text_report.py
import json, os
from datetime import datetime

def safe_list(value):
    if isinstance(value, list):
        return value
    return []

def short(text, n=300):
    if not text:
        return ""
    t = text.strip()
    return t[:n] + "..." if len(t) > n else t

def build_text_report(drug):
    base = f"data/{drug}"
    out_file = f"{base}/final_summary.txt"
    combined_path = f"{base}/combined_summary.json"

    if not os.path.exists(combined_path):
        return f"Error: {combined_path} not found. Run main.py first."

    data = json.load(open(combined_path, encoding="utf-8"))

    lines = []
    lines.append(f"==============================\n")
    lines.append(f"  INNOVATION REPORT — {drug.upper()}\n")
    lines.append(f"  Generated: {datetime.now()}\n")
    lines.append(f"==============================\n\n")

    # PubMed
    pubmed = data.get("pubmed", [])
    lines.append(f"📌 PubMed Articles Found: {len(pubmed)}\n")
    lines.append("Top 10 Articles:\n")
    for i, r in enumerate(pubmed[:10]):
        lines.append(f"{i+1}. {short(r.get('title', ''), 200)}")
        lines.append(f"    Journal: {r.get('journal','')}, Date: {r.get('date','')}\n")

    # Clinical Trials
    trials = data.get("clinical_trials", [])
    lines.append("\n📌 Clinical Trials Summary\n")
    lines.append(f"Total trials: {len(trials)}\n")
    if trials:
        for t in trials[:10]:
            nct = safe_list(t.get("NCTId"))[:1]
            cond = ", ".join(safe_list(t.get("Condition"))[:2])
            title = t.get("BriefTitle") or ""
            phase = safe_list(t.get("Phase"))[:1]
            status = safe_list(t.get("Status"))[:1]
            lines.append(f"- {nct} | {cond} | {title[:100]}... | Phase {phase} | {status}")

    # Patents
    lines.append("\n📌 Patent Landscape\n")
    patents = data.get("patents", [])
    if patents:
        for p in patents:
            lines.append(f"- {p.get('patent_id')} | {p.get('title')} | {p.get('status')} | Expiry {p.get('expiry_year')}")
    else:
        lines.append("No patents.\n")

    # Unmet Needs
    lines.append("\n📌 Unmet Needs\n")
    unmet = data.get("unmet_needs", [])
    for u in unmet:
        lines.append(f"- {u}")

    # IQVIA Insights
    iqvia = data.get("iqvia", {})
    lines.append("\n📌 IQVIA Market Insights\n")
    for k, v in iqvia.items():
        lines.append(f"- {k}: {v}")

    # EXIM Trade Data
    exim = data.get("exim", {})
    lines.append("\n📌 EXIM Trade Insights\n")
    for b in exim.get("bullets", []):
        lines.append(f"- {b}")

    # Web Intelligence
    lines.append("\n📌 Web Intelligence Summary\n")
    web = data.get("web_intel", [])
    for w in web[:5]:
        lines.append(f"- {w['title']} | {w['url']}")

    # Internal Insights
    lines.append("\n📌 Internal Insights\n")
    internal = data.get("internal_summary", {})
    for b in internal.get("bullets", []):
        lines.append(f"- {b}")

    # Save file
    with open(out_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return f"Text report saved at: {out_file}"
