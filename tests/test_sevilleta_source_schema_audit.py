from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from analysis import audit_sevilleta_source_schema_v1 as m


class SevilletaSourceAuditTests(unittest.TestCase):
    def test_tab_schema_detects_required_structural_fields(self):
        text=(
            "date\tsite\tweb\tstake\tnight\tspecies\tsex\ttag\n"
            "2015-01-01\tA\t1\t12\t1\tDM\tM\tT1\n"
            "2015-01-02\tA\t1\t13\t2\tDM\tM\tT1\n"
        )
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.txt"
            path.write_text(text,encoding="utf-8")
            out=m.audit_file(path)
        self.assertTrue(out["source_adequacy_for_next_estimability_design"])
        self.assertTrue(out["identity_column_present"])
        self.assertEqual(out["data_row_count"],2)
        self.assertFalse(out["sex_specific_effects_inspected"])

    def test_audit_does_not_require_effect_calculation(self):
        text="date\tsite\tweb\tstake\tnight\tspecies\tsex\n2015\tA\t1\t1\t1\tDM\tF\n"
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/"x.txt"
            path.write_text(text,encoding="utf-8")
            out=m.audit_file(path)
        self.assertFalse(out["identity_column_present"])
        self.assertFalse(out["movement_distances_computed"])
        self.assertFalse(out["packing_effects_computed"])
        self.assertEqual(out["ecological_effect_models_fit"],0)


if __name__=="__main__":
    unittest.main()
