from utils.pdf_generator import create_pdf
import os


class ReportAgent:

    def generate_summary(self, drug, pubmed, trials, patents, unmet, market):

        output_file = f"data/{drug}/final_summary.pdf"

        create_pdf(
            output_file,
            drug,
            pubmed,
            trials,
            patents,
            unmet,
            market
        )

        return output_file
