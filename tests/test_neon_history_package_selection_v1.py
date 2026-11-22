"""Prevent simple/detailed package duplication without inspecting outcomes."""
import unittest
from analysis.audit_neon_identification_evidence_v1 import select_history_files

class HistoryPackageSelectionTests(unittest.TestCase):
    def test_expanded_wins_without_duplicate_rows(self):
        base={'release':'RELEASE-2026','site':'TEST','month':'2020-07',
              'table':'mam_identificationHistory','name':'basic.csv','package':'basic','md5':'a'*32}
        expanded={**base,'name':'expanded.csv','package':'expanded','md5':'b'*32}
        self.assertEqual(select_history_files([base,expanded]),[expanded])
        self.assertEqual(select_history_files([expanded,base,expanded]),[expanded])
        with self.assertRaisesRegex(ValueError,'conflict'):
            select_history_files([expanded,{**expanded,'md5':'c'*32}])

if __name__=='__main__': unittest.main()
