# import requests
# import json
# import os

# class ClinicalTrialsAgent:

#     API_URL = "https://clinicaltrials.gov/api/v2/studies"

#     def get_trials(self, drug):
#         print("ClinicalTrials Agent: Fetching trial data using API v2...")

#         params = {
#             "query.intr": drug,     # CORRECT parameter for drugs
#             "countTotal": "true",
#             "pageSize": 50
#         }

#         try:
#             response = requests.get(self.API_URL, params=params, timeout=20)
#             response.raise_for_status()

#             data = response.json()
#             studies = data.get("studies", [])

#             cleaned = []
#             for s in studies:
#                 p = s.get("protocolSection", {})

#                 cleaned.append({
#                     "nct_id": p.get("identificationModule", {}).get("nctId"),
#                     "title": p.get("identificationModule", {}).get("officialTitle"),
#                     "status": p.get("statusModule", {}).get("overallStatus"),
#                     "conditions": p.get("conditionsModule", {}).get("conditions", []),
#                     "phases": p.get("designModule", {}).get("phases", [])
#                 })

#             # save output
#             os.makedirs(f"data/{drug}", exist_ok=True)
#             with open(f"data/{drug}/clinical_trials.json", "w", encoding="utf-8") as f:
#                 json.dump(cleaned, f, indent=2)

#             print(f"ClinicalTrials: Retrieved {len(cleaned)} trials.")
#             return cleaned

#         except Exception as e:
#             print("ClinicalTrials ERROR:", e)
#             print("Returning empty trial list.")
#             return []


# agents/clinical_trials_agent.py
import requests
import json
import os

class ClinicalTrialsAgent:

    API_URL = "https://clinicaltrials.gov/api/v2/studies"

    def get_trials(self, drug):
        print("ClinicalTrials Agent: Fetching detailed trial data...")

        params = {
            "query.intr": drug,
            "countTotal": "true",
            "pageSize": 50
        }

        try:
            response = requests.get(self.API_URL, params=params, timeout=20)
            response.raise_for_status()

            data = response.json()
            studies = data.get("studies", [])

            cleaned = []

            for s in studies:
                p = s.get("protocolSection", {})

                cleaned.append({
                    "nct_id": p.get("identificationModule", {}).get("nctId"),
                    "title": p.get("identificationModule", {}).get("officialTitle"),
                    "status": p.get("statusModule", {}).get("overallStatus"),

                    # Conditions / phase
                    "conditions": p.get("conditionsModule", {}).get("conditions", []),
                    "phases": p.get("designModule", {}).get("phases", []),

                    # NEW FIELDS (needed for modal)
                    "brief_summary": p.get("descriptionModule", {}).get("briefSummary"),
                    "detailed_description": p.get("descriptionModule", {}).get("detailedDescription"),

                    "interventions": p.get("armsInterventionsModule", {}).get("interventions", []),

                    "sponsors": p.get("sponsorsModule", {}).get("leadSponsor", {}).get("name"),

                    "locations": p.get("contactsLocationsModule", {}).get("locations", []),

                    "eligibility": p.get("eligibilityModule", {}).get("eligibilityCriteria"),

                    "study_type": p.get("designModule", {}).get("studyType"),
                    "start_date": p.get("statusModule", {}).get("startDateStruct", {}).get("date"),
                    "completion_date": p.get("statusModule", {}).get("completionDateStruct", {}).get("date"),
                    "last_update_posted": p.get("statusModule", {}).get("lastUpdatePostDateStruct", {}).get("date"),

                    "enrollment": p.get("designModule", {}).get("enrollmentInfo", {}).get("count")
                })

            os.makedirs(f"data/{drug}", exist_ok=True)
            with open(f"data/{drug}/clinical_trials.json", "w", encoding="utf-8") as f:
                json.dump(cleaned, f, indent=2)

            print(f"ClinicalTrials: Retrieved {len(cleaned)} detailed trials.")
            return cleaned

        except Exception as e:
            print("ClinicalTrials ERROR:", e)
            return []
