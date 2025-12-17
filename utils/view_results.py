# utils/view_results.py
import json, sys, os

def print_sample(pubmed, n=5):
    print(f"\n-- Showing first {n} PubMed entries --")
    for i, r in enumerate(pubmed[:n]):
        print(f"{i+1}. {r.get('title')} ({r.get('date')}) - {r.get('journal')}")
        authors = r.get('authors') or []
        if authors:
            print("   Authors:", ", ".join(authors[:4]))
    print()

def main(drug):
    base = f"data/{drug}"
    if not os.path.exists(base):
        print("No data for", drug)
        return

    def load(fn):
        p = os.path.join(base,fn)
        if os.path.exists(p):
            return json.load(open(p,encoding="utf-8"))
        return None

    pub = load("pubmed.json") or load("pubmed_pubmed.json") or []
    trials = load("clinical_trials.json") or []
    patents = load("patents.json") or []
    combined = load("combined_summary.json") or {}

    print(f"\nResults for: {drug}")
    print("PubMed articles:", len(pub))
    print("Clinical trials:", len(trials))
    print("Patents:", len(patents))
    if combined.get("iqvia"):
        print("IQVIA market:", combined['iqvia'].get("market_size_2024_usd_billion"))
    if combined.get("exim"):
        print("EXIM trade years:", len(combined['exim'].get("trade_history",[])))
    print("\nFiles in folder:", os.listdir(base))
    print_sample(pub, n=5)
    print("Open the PDF report at:", os.path.join(base,"final_summary.pdf"))
    print()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python utils/view_results.py <drug>")
    else:
        main(sys.argv[1])
