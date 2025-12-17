# agents/pubmed_agent.py
import time
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import json
import os


class PubMedAgent:

    SEARCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi"
    SUMMARY_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esummary.fcgi"
    FETCH_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi"

    def __init__(self):
        self.session = self._create_session()

    # --------------------------------------------------
    # SAFE REQUEST SESSION
    # --------------------------------------------------
    def _create_session(self):
        session = requests.Session()

        retries = Retry(
            total=5,
            backoff_factor=1,
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["GET"]
        )

        adapter = HTTPAdapter(max_retries=retries)
        session.mount("https://", adapter)

        return session

    # --------------------------------------------------
    # SEARCH PUBMED (LIMITED)
    # --------------------------------------------------
    def search(self, drug):
        
        query = f'"{drug}"[Title] AND ("drug"[MeSH Terms] OR "pharmacology"[MeSH Terms])'

        params = {
            "db": "pubmed",
            "term": query,
            "sort": "relevance",
            "retmax": 50,          
            "retmode": "json"
        }

        resp = self.session.get(
            self.SEARCH_URL,
            params=params,
            timeout=15
        )
        resp.raise_for_status()

        data = resp.json()
        return data.get("esearchresult", {}).get("idlist", [])

    # --------------------------------------------------
    # FETCH METADATA + ABSTRACTS (BATCHED)
    # --------------------------------------------------
    def fetch(self, ids):
        all_records = []

        for i in range(0, len(ids), 10):   # 🔴 SMALL BATCH
            batch = ids[i:i + 10]
            id_str = ",".join(batch)

            try:
                # ---- Metadata ----
                meta_resp = self.session.get(
                    self.SUMMARY_URL,
                    params={"db": "pubmed", "id": id_str, "retmode": "xml"},
                    timeout=20
                )
                meta_resp.raise_for_status()
                meta_soup = BeautifulSoup(meta_resp.text, "xml")

                # ---- Abstracts ----
                abs_resp = self.session.get(
                    self.FETCH_URL,
                    params={"db": "pubmed", "id": id_str, "retmode": "xml"},
                    timeout=20
                )
                abs_resp.raise_for_status()
                abs_soup = BeautifulSoup(abs_resp.text, "xml")

                # Map PMID → abstract
                abstracts = {}
                for art in abs_soup.find_all("PubmedArticle"):
                    pmid = art.PMID.text if art.PMID else None
                    abstract_node = art.find("AbstractText")
                    abstracts[pmid] = (
                        abstract_node.get_text(" ", strip=True)
                        if abstract_node else "No abstract available."
                    )

                # Combine
                for doc in meta_soup.find_all("DocSum"):
                    pmid = doc.find("Id").text
                    title = doc.find("Item", {"Name": "Title"}).text
                    date = doc.find("Item", {"Name": "PubDate"}).text
                    journal = doc.find("Item", {"Name": "Source"}).text
                    authors = [a.text for a in doc.find_all("Item", {"Name": "Author"})]

                    all_records.append({
                        "pmid": pmid,
                        "title": title,
                        "date": date,
                        "journal": journal,
                        "authors": authors,
                        "abstract": abstracts.get(pmid)
                    })

                time.sleep(0.3)  # 🧠 Respect NCBI

            except Exception as e:
                print("❌ PubMed batch failed:", e)
                continue

        return all_records

    # --------------------------------------------------
    # MAIN ENTRY (FAIL-SAFE)
    # --------------------------------------------------
    def search_and_fetch(self, drug):
        try:
            ids = self.search(drug)
            print(f"PubMed: Found {len(ids)} articles.")

            records = self.fetch(ids)

            os.makedirs(f"data/{drug}", exist_ok=True)
            with open(f"data/{drug}/pubmed.json", "w", encoding="utf-8") as f:
                json.dump(records, f, indent=2)

            return records

        except Exception as e:
            print("❌ PubMedAgent fatal error:", e)
            return []
