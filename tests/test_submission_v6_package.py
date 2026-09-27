from pathlib import Path
import subprocess
import unittest
import zipfile

ROOT=Path(__file__).resolve().parents[1]
DOCX=ROOT/"dist"/"oikos_main_text_anonymous.docx"
ZIP=ROOT/"dist"/"oikos_anonymous_review_package.zip"
FIG5=ROOT/"dist"/"figures"/"Figure_5.png"
TITLE="Local spatial cohesion in small mammals is redundant across species but context-dependent across sites"


class SubmissionV6PackageTests(unittest.TestCase):
    def test_v6_docx_figure5_and_fresh_evidence_are_packaged(self):
        subprocess.run(["python","analysis/build_paper_assets.py"],cwd=ROOT,check=True)
        subprocess.run(["python","analysis/build_carrier_turnover_figure_v1.py"],cwd=ROOT,check=True)
        subprocess.run(["python","analysis/build_carrier_mechanism_figure_v1.py"],cwd=ROOT,check=True)
        subprocess.run(["python","submission/build_oikos_figure_pngs.py"],cwd=ROOT,check=True)
        subprocess.run(["python","submission/build_oikos_manuscript_docx.py"],cwd=ROOT,check=True)
        subprocess.run(["python","submission/build_anonymous_review_package.py"],cwd=ROOT,check=True)

        self.assertTrue(FIG5.is_file())

        with zipfile.ZipFile(DOCX) as zf:
            xml=zf.read("word/document.xml").decode("utf-8",errors="ignore")
        self.assertIn(TITLE,xml)

        with zipfile.ZipFile(ZIP) as zf:
            names=set(zf.namelist())
        self.assertIn("results/carrier_prevalence_response_v1.json",names)
        self.assertIn("evidence/carrier_prevalence_protocol_v1.json",names)
        self.assertIn("analysis/count_conditioned_carrier_null_v1.py",names)
        self.assertIn("analysis/build_carrier_mechanism_figure_v1.py",names)


if __name__=="__main__":
    unittest.main()
