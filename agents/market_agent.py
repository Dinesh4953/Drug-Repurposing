import random
import json
import os


class MarketAgent:

    def get_market_data(self, drug):

        mock = {
            "market_size_2024": f"${random.randint(1, 5)}B",
            "CAGR": f"{random.randint(4,12)}%",
            "competitors": ["Company A", "Company B", "Company C"]
        }

        return mock
