# agents/web_agent.py
import os, json
from collections import defaultdict

class WebAgent:
    """
    Simulates real-time web intelligence: finds guidelines, news and RWE snippets.
    Produces hyperlinked-style 'citation' entries (mock URLs) and short extracts.
    """

    def _mock_results(self, drug):
        # produce 4 mock search hits
        hits = []
        hits.append({
            "title": f"World Health Organization guidance on {drug}",
            "source": "who.int",
            "url": f"https://who.int/guidance/{drug.replace(' ','-')}",
            "snippet": f"WHO guidance highlights safe use and special population considerations for {drug}."
        })
        hits.append({
            "title": f"Recent review: off-label uses of {drug}",
            "source": "journal-review.org",
            "url": f"https://journal-review.org/{drug.replace(' ','-')}-review",
            "snippet": "Review summarizes potential new therapeutic areas with emerging evidence."
        })
        hits.append({
            "title": f"Patient forum discussion on {drug} side effects",
            "source": "healthforums.example",
            "url": f"https://healthforums.example/{drug.replace(' ','-')}",
            "snippet": "Users report common adverse events and dosing preferences across regions."
        })
        hits.append({
            "title": f"Regulatory safety update on {drug}",
            "source": "regulator.example",
            "url": f"https://regulator.example/alerts/{drug.replace(' ','-')}",
            "snippet": "Regulatory agency reminds prescribers about dose limits and monitoring."
        })
        return hits

    def search(self, drug):
        res = self._mock_results(drug)
        os.makedirs(f"data/{drug}", exist_ok=True)
        with open(f"data/{drug}/web_intel.json","w",encoding="utf-8") as f:
            json.dump(res, f, indent=2)
        return res
