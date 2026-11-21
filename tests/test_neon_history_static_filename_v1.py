"""NEON history tables may be non-monthly files inside monthly packages."""
import unittest
from analysis.audit_neon_identification_evidence_v1 import extract_history_inventory

class StaticHistoryFilenameTests(unittest.TestCase):
    def test_history_table_without_embedded_month_is_retained(self):
        entry={'name':'NEON.D01.TEST.DP1.10072.001.mam_identificationHistory.basic.20260101T000000Z.csv',
               'size':100,'md5':'a'*32,'url':'https://data.neonscience.org/source.csv'}
        source={'data':{'releases':[{'release':'RELEASE-2026','packages':[{
            'siteCode':'TEST','month':'2020-07','packageType':'basic','files':[entry]}]}]}}
        selected,_=extract_history_inventory(source)
        self.assertEqual(len(selected),1)
        self.assertEqual(selected[0]['month'],'2020-07')
        self.assertEqual(selected[0]['table'],'mam_identificationHistory')

if __name__=='__main__': unittest.main()
