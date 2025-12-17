# agents/exim_agent.py
import os, json, random
from datetime import datetime

from files.paracetamol_real_exim import PARACETAMOL_EXPORTS, PARACETAMOL_IMPORTS


class EXIMAgent:

    def _mock_yearly(self):
        return {
            "2022": random.randint(5000, 15000),
            "2023": random.randint(6000, 16000),
            "2024": random.randint(7000, 17000),
        }

    def _mock_countries(self):
        countries = ["USA", "UK", "China", "Germany", "Brazil", "UAE"]
        random.shuffle(countries)
        return {
            "2024": [[c, random.randint(300, 5000)] for c in countries[:5]]
        }

    def _get_real_paracetamol(self):
        return {
            "export_data": {
                "export_volume_kgs": PARACETAMOL_EXPORTS["export_volume_kgs"],
                "export_value_crores": PARACETAMOL_EXPORTS["export_value_crores"],
                "top_export_countries": PARACETAMOL_EXPORTS.get("top_export_countries", {})
            },
            "import_data": {
                "import_volume_kgs": PARACETAMOL_IMPORTS["import_volume_kgs"],
                "import_value_crores": PARACETAMOL_IMPORTS["import_value_crores"],
                "top_import_countries": PARACETAMOL_IMPORTS.get("top_import_countries", {})
            },

            # Summary for table
            "summary": [
                "Paracetamol exports increased significantly over the past 3 years.",
                "India remains a top exporter to USA, UK, Brazil.",
                "Imports still depend heavily on China for API supply."
            ],

            # These fields prevent template crash
            "trade_history": [],
            "bullets": []
        }

    def get_trade_data(self, drug):

        if drug.lower() == "paracetamol":
            data = self._get_real_paracetamol()

        else:
            # FULL MOCK STRUCTURE ALWAYS PRESENT
            data = {
                "export_data": {
                    "export_volume_kgs": self._mock_yearly(),
                    "export_value_crores": self._mock_yearly(),
                    "top_export_countries": self._mock_countries(),
                },
                "import_data": {
                    "import_volume_kgs": self._mock_yearly(),
                    "import_value_crores": self._mock_yearly(),
                    "top_import_countries": self._mock_countries(),
                },

                "summary": [
                    "Moderate export performance.",
                    "Import dependency moderately stable.",
                    "Potential growth in emerging markets."
                ],

                # mock simple table
                "trade_history": [
                    {
                        "year": y,
                        "export_volume_mt": random.randint(8, 22),
                        "import_dependence_percent": random.randint(20, 70)
                    }
                    for y in range(2020, 2025)
                ],

                "bullets": [
                    "Export market shows controlled volatility.",
                    "Import dependency varies with API availability.",
                    "Suitable candidate for domestic manufacturing incentives."
                ]
            }

        # Save file
        os.makedirs(f"data/{drug}", exist_ok=True)
        with open(f"data/{drug}/exim_trade.json", "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return data
