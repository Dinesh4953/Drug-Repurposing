# agents/iqvia_agent.py
import os, json, random
from collections import Counter
import math

class IQVIAAgent:
    """
    Produces mock market-size, CAGR, competitor list and
    a short generative-style market insight using PubMed titles.
    """

    def _mock_market(self, drug):
        market_size_b = round(random.uniform(0.5, 8.0), 2)
        cagr = round(random.uniform(3.5, 12.0), 1)
        return {
            "market_size_2024_usd_billion": f"{market_size_b}B",
            "CAGR": f"{cagr}%",
            "top_competitors": [
                f"Competitor {c}" for c in ["A", "B", "C", "D"]
            ],
            "estimated_revenue_2025_usd_billion": f"{round(market_size_b * (1 + cagr/100),2)}B"
        }

    def _generate_insight(self, drug, pubmed_records):
        # simple keyword extraction from titles
        titles = [r.get("title","") for r in pubmed_records if r.get("title")]
        text = " ".join(titles).lower()
        stop = set(["the","and","in","of","a","to","for","with","on","is","by","an","are"])
        words = [w.strip(".,;:()[]") for w in text.split() if len(w)>3 and w not in stop]
        common = Counter(words).most_common(8)
        key_terms = ", ".join([t for t,_ in common])
        insight = (
            f"Market snapshot for {drug}: key research themes include {key_terms}. "
            "The therapy area shows steady research volume and potential for value-added formulations "
            "targeting safety or special populations."
        )
        return insight

    def get_market_data(self, drug, pubmed_records):
        result = self._mock_market(drug)
        result["market_insight"] = self._generate_insight(drug, pubmed_records)
        os.makedirs(f"data/{drug}", exist_ok=True)
        with open(f"data/{drug}/market_iqvia.json","w",encoding="utf-8") as f:
            json.dump(result, f, indent=2)
        return result
