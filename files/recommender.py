import os
import json
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a pharmaceutical strategy assistant.

Your job:
- Give a simple recommendation about drug repurposing.
- Only return JSON.
- Give 4–6 short reasons.
- Give a 3–5 line short summary.
- Keep it simple and business-friendly.
"""

def build_prompt(data):
    compact = {
        "drug": data.get("drug"),
        "pubmed_count": data.get("pubmed_count"),
        "clinical_trials": len(data.get("clinical_trials", [])),
        "patent_count": len(data.get("patents", [])),
        "unmet_needs": data.get("unmet_needs", []),
        "market": data.get("iqvia", {}),
        "exim": data.get("exim", {}),
    }
    return json.dumps(compact, indent=2)


def ai_recommendation(data):
    prompt = build_prompt(data)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ],
        max_tokens=400,
        temperature=0.2
    )

    text = response.choices[0].message.content

    # Extract JSON safely
    import re
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except:
            pass

    # fallback
    return {
        "recommendation": "UNCLEAR",
        "reasons": ["AI summary failed."],
        "short_summary": "No automated reasoning available."
    }
