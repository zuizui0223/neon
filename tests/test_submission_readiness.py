from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
MANUSCRIPT = ROOT / "manuscript" / "neon_metacommunity_redundancy" / "MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md"

class SubmissionReadinessTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.text = MANUSCRIPT.read_text(encoding="utf-8")

    def test_abstract_within_oikos_limit(self):
        abstract = self.text.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
        words = re.findall(r"\b[\w–-]+\b", abstract)
        self.assertLessEqual(len(words), 300)

    def test_abstract_has_no_unexplained_neon_acronym(self):
        abstract = self.text.split("## Abstract", 1)[1].split("## 1. Introduction", 1)[0]
        self.assertNotIn("NSF NEON", abstract)
        self.assertNotRegex(abstract, r"\bNEON\b")
        self.assertNotRegex(abstract, r"\bORNL\b")

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

    def test_data_availability_is_not_in_main_text(self):
        self.assertNotIn("## Data and code availability", self.text)
        self.assertNotIn("## 7. Data and code availability", self.text)

    def test_ai_statement_is_final_section(self):
        self.assertIn("## 7. Artificial intelligence use", self.text)
        tail = self.text.split("## 7. Artificial intelligence use", 1)[1].strip()
        self.assertTrue(tail)
        self.assertNotIn("\n## ", tail)

    def test_submission_only_internal_sections_removed(self):
        self.assertNotIn("## One-sentence claim", self.text)
        self.assertNotIn("## 5. Claim boundary", self.text)
        self.assertNotIn("Figure plan", self.text)

    def test_required_sections_present(self):
        for section in (
            "## Abstract",
            "## 1. Introduction",
            "## 2. Methods",
            "## 3. Results",
            "## 4. Discussion",
            "## 5. References",
            "## 6. Figure captions",
            "## 7. Artificial intelligence use",
        ):
            self.assertIn(section, self.text)

if __name__ == "__main__":
    unittest.main()
