from flask import Flask, render_template, request, send_file
from agents.master_agent import MasterAgent
import os, json

app = Flask(__name__)
agent = MasterAgent()



def is_valid_input(drug):
    if len(drug) < 4:
        return False
    if drug.isdigit():
        return False
    if drug.isalpha() and len(drug) <= 3:
        return False
    return True



# ===================== HOME =====================
@app.route("/")
def home():
    return render_template("index.html")


# ===================== ANALYZE =====================


from flask import request, render_template
from werkzeug.utils import secure_filename
import os

ALLOWED_EXTENSIONS = {"pdf", "txt", "docx"}

def allowed_file(filename):
    return (
        "." in filename
        and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS
    )


@app.route("/analyze", methods=["POST"])
def analyze():

    # ---------- 1. Validate drug name (MANDATORY) ----------
    drug = request.form.get("drug", "").strip().lower()

# ❌ Invalid / non-drug input
    if not drug or not is_valid_input(drug):
        return render_template(
        "drug_not_found.html",
        drug=drug
    )

    if not drug:
        return render_template("index.html", error="Drug name is mandatory.")

    # ---------- QUICK DRUG VALIDATION (PUBMED) ----------
    pubmed_count = agent.pubmed.search(drug)
    if not pubmed_count:
        return render_template(
            "drug_not_found.html",
            drug=drug
        )

    # ---------- 2. Prepare folders ----------
    base_path = f"data/{drug}"
    internal_folder = f"{base_path}/internal_docs"
    os.makedirs(internal_folder, exist_ok=True)
    
    # ---------- 3. 🔥 CLEAR OLD INTERNAL FILES (OPTION 1 FIX) ----------
    for old_file in os.listdir(internal_folder):
        old_path = os.path.join(internal_folder, old_file)
        if os.path.isfile(old_path):
            os.remove(old_path)

    # ---------- 4. Handle uploaded files (OPTIONAL + SAFE) ----------
    files = request.files.getlist("files")
    has_internal_docs = False

    for f in files:
        if f and f.filename:
            if allowed_file(f.filename):
                filename = secure_filename(f.filename)
                f.save(os.path.join(internal_folder, filename))
                has_internal_docs = True
            # Unsupported files are safely ignored

    # ---------- 4. Run all intelligence agents ----------
    results = agent.run(drug)

    # ---------- 5. Safe summary handling ----------
    summary = results.get("final_summary")

    if not summary:
        # Guaranteed fallback (never fails)
        summary = {
            "note": "Fallback summary (AI unavailable)",
            "pubmed_articles": len(results.get("pubmed", [])),
            "clinical_trials": len(results.get("clinical_trials", [])),
            "patent_count": len(results.get("patents", [])),
        }

    # ---------- 6. Render results ----------
    return render_template(
        "results.html",
        drug=drug,
        results=results,
        summary=summary,
        has_internal_docs=has_internal_docs
    )


# ===================== HELPER =====================
def load_cached_data(drug):
    drug = drug.lower()
    path = f"data/{drug}/combined_summary.json"

    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    data = agent.run(drug)

    os.makedirs(f"data/{drug}", exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)

    return data


# ===================== PUBMED PAGE =====================
@app.route("/pubmed/<drug>")
def pubmed_page(drug):

    data = load_cached_data(drug)
    pubmed_data = data.get("pubmed", [])

    return render_template(
        "pubmed.html",
        drug=drug,
        pubmed=pubmed_data,
        count=len(pubmed_data)
    )


# ===================== CLINICAL TRIALS PAGE =====================
@app.route("/clinical/<drug>")
def clinical_view(drug):

    data = load_cached_data(drug)
    trials = data.get("clinical_trials", [])

    return render_template(
        "clinical_trials.html",
        drug=drug,
        trials=trials,
        count=len(trials)
    )


# ===================== PATENTS PAGE =====================
@app.route("/patents/<drug>")
def patents_page(drug):

    drug = drug.lower()
    path = f"data/{drug}/combined_summary.json"

    if not os.path.exists(path):
        return "No patent data found", 404

    data = json.load(open(path, "r", encoding="utf-8"))
    patents = data.get("patents", [])

    return render_template(
        "patents.html",
        drug=drug,
        patents=patents
    )


# ===================== EXIM MAIN PAGE =====================
@app.route("/exim/<drug>")
def exim_view(drug):

    data = load_cached_data(drug)
    exim = data.get("exim", {})

    return render_template(
        "exim.html",
        drug=drug,
        exim=exim
    )


# ===================== EXIM MORE PAGE =====================
@app.route("/exim_more/<drug>")
def exim_more(drug):

    data = load_cached_data(drug)
    exim = data.get("exim", {})

    return render_template(
        "exim_more.html",
        drug=drug,
        exim=exim
    )

@app.route("/internal/<drug>")
def internal_view(drug):
    path = f"data/{drug}/internal_summary.json"

    if not os.path.exists(path):
        return render_template(
            "internal.html",
            drug=drug,
            internal=None
        )

    with open(path, "r", encoding="utf-8") as f:
        internal = json.load(f)

    return render_template(
        "internal.html",
        drug=drug,
        internal=internal
    )



# ===================== RUN APP =====================
if __name__ == "__main__":
    app.run(debug=True)
