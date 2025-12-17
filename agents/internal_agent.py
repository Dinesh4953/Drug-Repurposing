import os, json, re
from dotenv import load_dotenv
from groq import Groq


# ---------- OCR SAFE BLOCK ----------
OCR_ENABLED = False   # Render cloud does NOT support OCR

if OCR_ENABLED and os.name == "nt":  # only for Windows local
    try:
        import pytesseract
        from pdf2image import convert_from_path
        from PIL import Image

        pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"
        POPPLER_PATH = r"C:\Users\gnane\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin"
    except:
        OCR_ENABLED = False
# ----------------------------------

try:
    import PyPDF2
    from docx import Document
except:
    PyPDF2 = None
    Document = None

load_dotenv()
client = Groq(api_key=os.getenv("GROQ_API_KEY"))


class InternalAgent:

    # --------------------------------------------------
    # READ DOCUMENTS (TEXT PDFs, DOCX, TXT)
    # --------------------------------------------------
    def _read_internal_docs(self, drug):
        folder = f"data/{drug}/internal_docs"
        os.makedirs(folder, exist_ok=True)

        texts = []

        for file in os.listdir(folder):
            path = os.path.join(folder, file)
            content = ""

            if file.lower().endswith(".txt"):
                with open(path, "r", encoding="utf-8", errors="ignore") as f:
                    content = f.read()

            elif file.lower().endswith(".pdf") and PyPDF2:
                try:
                    reader = PyPDF2.PdfReader(open(path, "rb"))
                    content = " ".join(p.extract_text() or "" for p in reader.pages)
                except Exception as e:
                    print("❌ PyPDF2 error:", e)

            elif file.lower().endswith(".docx") and Document:
                try:
                    doc = Document(path)
                    content = " ".join(p.text for p in doc.paragraphs)
                except Exception as e:
                    print("❌ DOCX error:", e)

            if content.strip():
                texts.append(content.strip())

        return texts


    # --------------------------------------------------
    # OCR FALLBACK (SCANNED PDFs)
    # --------------------------------------------------
    def _ocr_pdf(self, folder):
        text = ""
        for file in os.listdir(folder):
            if file.lower().endswith(".pdf"):
                path = os.path.join(folder, file)
                print("🔍 OCR processing:", path)
                try:
                    images = convert_from_path(path,dpi=300,poppler_path=r"C:\Users\gnane\Downloads\Release-25.12.0-0\poppler-25.12.0\Library\bin")
                    print("📄 OCR pages:", len(images))

                    for i, img in enumerate(images[:5]):  # limit for speed
                        page_text = pytesseract.image_to_string(img)
                        print(f"OCR page {i} length:", len(page_text))
                        text += page_text

                except Exception as e:
                    print("❌ OCR ERROR:", e)

        return text.strip()


    # --------------------------------------------------
    # AI PROMPT
    # --------------------------------------------------
    def _build_prompt(self, text):
        return f"""
Return ONLY valid JSON.

Format:
{{
  "executive_points": [],
  "key_findings": [],
  "risks": [],
  "opportunities": [],
  "repurposing_signals": [],
  "confidence_note": ""
}}

TEXT:
{text[:12000]}
"""


    # --------------------------------------------------
    # GROQ SUMMARIZATION
    # --------------------------------------------------
    def _groq_summarize(self, text):
        response = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You summarize pharmaceutical internal documents."},
                {"role": "user", "content": self._build_prompt(text)}
            ],
            temperature=0.1,
            max_tokens=900
        )

        raw = response.choices[0].message.content
        try:
            match = re.search(r"\{(.|\n)*\}", raw)
            return json.loads(match.group(0))
        except:
            return None


    # --------------------------------------------------
    # FALLBACK SUMMARY
    # --------------------------------------------------
    def _fallback_summary(self, note):
        return {
            "executive_points": ["Internal document uploaded."],
            "key_findings": [],
            "risks": [],
            "opportunities": [],
            "repurposing_signals": [],
            "confidence_note": note
        }


    # --------------------------------------------------
    # MAIN ENTRY
    # --------------------------------------------------
    def summarize(self, drug):
        folder = f"data/{drug}/internal_docs"

        if not os.listdir(folder):
            return {"source": "mock_internal", "document_count": 0}

        # ---- Step 1: Extract text normally ----
        texts = self._read_internal_docs(drug)
        combined_text = " ".join(texts).strip()

        print("📄 TEXT LENGTH (PyPDF2):", len(combined_text))

        # ---- Step 2: OCR if text weak ----
        if len(combined_text) < 300:
            ocr_text = self._ocr_pdf(folder)
            combined_text += " " + ocr_text

        combined_text = combined_text.strip()
        print("📄 FINAL TEXT LENGTH:", len(combined_text))

        drug_lower = drug.lower()
        text_lower = combined_text.lower()

        # ---- Step 3: Drug-name detection (robust) ----
        drug_found = (
            drug_lower in text_lower or
            drug_lower.replace(" ", "") in text_lower.replace(" ", "")
        )

        # ---- Step 4: Decision ----
        if drug_found and len(combined_text) > 300:
            summary = self._groq_summarize(combined_text)
            if not summary:
                summary = self._fallback_summary(
                    "Drug name detected, but AI summarization failed."
                )

        elif   OCR_ENABLED and len(combined_text) < 300:
            ocr_text = self._ocr_pdf(folder)
            combined_text += " " + ocr_text


        else:
            summary = self._fallback_summary(
                "Uploaded document appears unrelated to the specified drug."
            )
            summary["suggestions"] = [
                "Upload a PDF related to the drug name",
                "Prefer clinical trials, formulation, or safety documents",
                "Ensure the drug name appears in the document"
            ]

        # ---- Metadata ----
        summary.update({
            "source": "uploaded_docs",
            "document_count": len(os.listdir(folder)),
            "raw_text_preview": combined_text[:3000]
        })

        # ---- Save ----
        os.makedirs(f"data/{drug}", exist_ok=True)
        with open(f"data/{drug}/internal_summary.json", "w", encoding="utf-8") as f:
            json.dump(summary, f, indent=2)

        return summary
