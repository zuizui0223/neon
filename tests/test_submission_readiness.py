from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "neon_metacommunity_redundancy" / "MANUSCRIPT_V4_OIKOS_READY.md"

class SubmissionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MANUSCRIPT.read_text(encoding="utf-8")

    def test_abstract_within_oikos_limit(self):
        abstract = self.text.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
        words = re.findall(r"\b[\w–-]+\b", abstract)
        self.assertLessEqual(len(words), 300)

    def test_main_text_has_no_author_identity(self):
        forbidden = [
            "ZHANG RUIQI",
            "ZHANG Ruiqi",
            "rachelzhang",
            "github.com/zuizui0223",
            "zuizui0223",
        ]
        for token in forbidden:
            self.assertNotIn(token, self.text)

    def test_required_submission_statements_present(self):
        self.assertIn("## 7. Data and code availability", self.text)
        self.assertIn("## 8. Artificial intelligence use", self.text)
        self.assertIn("## 6. References", self.text)

if __name__ == "__main__":
    unittest.main()
