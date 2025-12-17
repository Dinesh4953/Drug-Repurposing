import os
import json
import re
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

SYSTEM_PROMPT = """
You are a senior pharmaceutical strategy scientist.

Your job:
- Decide whether the drug SHOULD be repurposed.
- Decide among YES / NO / CONDITIONAL.
- Give 4–6 scientific and market reasons.
- Give a clear explanation (4–6 sentences).
- Use evidence from PubMed, clinical trials, patents, unmet needs, EXIM & IQVIA if available.
- If evidence is weak or missing → say so.

OUTPUT FORMAT (must follow exactly):

{
  "decision": "YES or NO or CONDITIONAL",
  "reasons": ["reason1", "reason2", ...],
  "explanation": "full paragraph here"
}
"""

def build_prompt(data):
    compact = {
        "drug": data.get("drug"),
        "pubmed_count": data.get("pubmed_count"),
        "trial_count": len(data.get("clinical_trials", [])),
        "patent_count": len(data.get("patents", [])),
        "unmet_needs": data.get("unmet_needs", []),
        "market": data.get("iqvia", {}),
        "exim": data.get("exim", {}),
        "internal": data.get("internal_summary", {}),
    }
    return json.dumps(compact, indent=2)


def extract_json(text):
    match = re.search(r"\{[\s\S]*\}", text)
    if match:
        try:
            return json.loads(match.group(0))
        except Exception:
            pass
    return None


def repurpose_decision(data):
    prompt = build_prompt(data)

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        temperature=0.2,
        max_tokens=500,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": prompt}
        ]
    )

    raw = response.choices[0].message.content
    parsed = extract_json(raw)

    if parsed:
        return parsed

    return {
        "decision": "UNCLEAR",
        "reasons": ["Model did not return proper JSON"],
        "explanation": raw
    }
