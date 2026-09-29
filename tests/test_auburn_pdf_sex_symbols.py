from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_auburn_pdf_sex_symbols_v1 as m


class AuburnPdfSexSymbolAuditTests(unittest.TestCase):
    def test_symbol_class(self):
        self.assertEqual(m.symbol_class("♂"),"M")
        self.assertEqual(m.symbol_class("♀"),"F")
        self.assertIsNone(m.symbol_class("?"))

    def test_layout_rows_detect_symbols(self):
        text=(
            "Appendix 2 continued.\n"
            "A1   D. ordii   ♂   adult   scrotal 74 910 X X X\n"
            "A5   D. ordii   ♀   adult   lactating 61 911 X X X\n"
            "Appendix 3. Number of burrows\n"
            "Appendix 4 continued.\n"
            "910 ad ♂ scrotal 70 2 2 bur 1-2 11.1 y\n"
            "911 ad ♀ lactating 61 3 4 bur 1-2 21.1 y\n"
            "Appendix 5. Captures\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"layout.txt"
            path.write_text(text,encoding="utf-8")
            out=m.audit_layout_text(path)
        self.assertTrue(out["direct_sex_symbol_extraction_usable"])
        self.assertEqual(out["appendix2"]["male_symbol_rows"],1)
        self.assertEqual(out["appendix4"]["female_symbol_rows"],1)


if __name__=="__main__":
    unittest.main()
