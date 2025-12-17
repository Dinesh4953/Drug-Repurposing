# agents/master_agent.py
import os

from agents.pubmed_agent import PubMedAgent
from agents.clinical_trials_agent import ClinicalTrialsAgent
from agents.patent_agent import PatentAgent
from agents.unmet_need_agent import UnmetNeedAgent
from agents.market_agent import MarketAgent
from agents.report_agent import ReportAgent

from agents.iqvia_agent import IQVIAAgent
from agents.exim_agent import EXIMAgent
from agents.web_agent import WebAgent
from agents.internal_agent import InternalAgent

from files.recommender import ai_recommendation
from files.repurpose_decision import repurpose_decision


class MasterAgent:

    def __init__(self):
        self.pubmed = PubMedAgent()
        self.clinical = ClinicalTrialsAgent()
        self.patents = PatentAgent()
        self.unmet = UnmetNeedAgent()
        self.market = MarketAgent()
        self.report = ReportAgent()

        self.iqvia = IQVIAAgent()
        self.exim = EXIMAgent()
        self.web = WebAgent()
        self.internal = InternalAgent()

    def run(self, drug_name):

        print(f"\n=== Master Agent: Starting analysis for {drug_name} ===\n")

        os.makedirs(f"data/{drug_name}", exist_ok=True)

        # ---------- Run agents ----------
        try:
            pubmed = self.pubmed.search_and_fetch(drug_name)
        except Exception as e:
            print("❌ PubMed failed:", e)
            pubmed = []

        trials = self.clinical.get_trials(drug_name)
        patents = self.patents.search(drug_name)
        unmet = self.unmet.generate(drug_name, pubmed)
        iqvia = self.iqvia.get_market_data(drug_name, pubmed)
        exim = self.exim.get_trade_data(drug_name)
        web = self.web.search(drug_name)

        # ✅ THIS is where PDF text + summary comes from
        internal = self.internal.summarize(drug_name)

        market_mock = self.market.get_market_data(drug_name)

        # ---------- Combine ----------
        combined = {
            "drug": drug_name,
            "pubmed_count": len(pubmed),
            "pubmed": pubmed,
            "clinical_trials": trials,
            "patents": patents,
            "unmet_needs": unmet,
            "iqvia": iqvia,
            "exim": exim,
            "web_intel": web,

            # ✅ INTERNAL SUMMARY PASSED DIRECTLY
            "internal_summary": internal,

            "market_mock": market_mock
        }

        # ---------- FINAL SUMMARY (NO INTERNAL DATA HERE) ----------
        combined["final_summary"] = self.build_final_summary(
            pubmed, trials, patents, iqvia, exim, unmet
        )

        combined["ai_recommendation"] = ai_recommendation(combined)
        combined["repurpose_decision"] = repurpose_decision(combined)

        return combined

    # ======================================================================
    # BUILD FINAL SUMMARY (PUBLIC DATA ONLY)
    # ======================================================================
    def build_final_summary(self, pubmed, trials, patents, iqvia, exim, unmet):

        export_trend = "Unknown"
        import_dep = "N/A"

        try:
            if "export_data" in exim:
                export_trend = "Rising"
                import_dep = exim["import_data"]["import_volume_kgs"]
            elif "trade_history" in exim:
                export_trend = "Mixed"
                import_dep = [
                    row["import_dependence_percent"]
                    for row in exim["trade_history"]
                ]
        except:
            pass

        return {
            "pubmed_articles": len(pubmed),
            "clinical_trials": len(trials),
            "patent_count": len(patents),

            "market_size": iqvia.get("market_size_2024_usd_billion", "N/A"),
            "cagr": iqvia.get("CAGR", "N/A"),

            "export_trend": export_trend,
            "import_dependence": import_dep,

            "unmet_needs": unmet
        }
