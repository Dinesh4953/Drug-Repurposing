import json
import os
import random


class PatentAgent:

    def search(self, drug):

        # Example therapeutic areas to choose from
        therapeutic_areas = [
            "Pain management",
            "Fever reduction",
            "Inflammation",
            "Liver safety formulations",
            "Pediatric dosing",
            "Extended-release technology",
            "Combination therapy"
        ]

        mock_patents = []

        for i in range(6):
            tid = random.randint(100000, 999999)
            expiry = random.randint(2025, 2040)
            ta = random.choice(therapeutic_areas)

            mock_patents.append({
                "patent_id": f"US{tid}A1",
                "title": f"{drug} {ta.lower()} novel formulation and delivery mechanism",
                "assignee": random.choice([
                    "Pfizer Inc.",
                    "Johnson & Johnson",
                    "Sun Pharma",
                    "Dr. Reddy’s Laboratories",
                    "Generic Pharma Co."
                ]),
                "inventors": [
                    random.choice(["John Doe", "Amit Sharma", "Sara Kim", "Michael Lee", "Priya Nair"]),
                    random.choice(["Emily Zhang", "Carlos Gomez", "Anna Petrova", "Rajesh Kumar"])
                ],
                "filing_year": random.randint(2015, 2022),
                "publication_year": random.randint(2017, 2024),
                "expiry_year": expiry,

                "therapeutic_area": ta,

                "abstract": (
                    f"This invention relates to an improved pharmaceutical formulation of {drug}, "
                    f"designed for enhanced {ta.lower()}. The composition includes modified excipients "
                    "which result in improved bioavailability, reduced first-pass metabolism, and superior "
                    "therapeutic control. The formulation offers manufacturing advantages and potential "
                    "clinical benefit compared to existing products."
                ),

                "status": random.choice(["Active", "Expired", "Pending"]),
                "pdf_link": "https://patents.google.com",  # placeholder
                "url": "https://patents.google.com"  # placeholder
            })

        # Save JSON
        os.makedirs(f"data/{drug}", exist_ok=True)
        with open(f"data/{drug}/patents.json", "w", encoding="utf-8") as f:
            json.dump(mock_patents, f, indent=2, ensure_ascii=False)

        return mock_patents
