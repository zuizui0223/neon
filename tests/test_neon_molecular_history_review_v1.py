import unittest
import importlib
try:
    module=importlib.import_module('analysis.review_neon_molecular_history_v1')
except ModuleNotFoundError:
    module=None
class ReviewTests(unittest.TestCase):
    def api(self):
        self.assertTrue(module is not None and hasattr(module,'review_records'),'review_records missing')
        return module.review_records
    def test_documented_revision_not_confirmation(self):
        data=[{'identificationHistoryID':'SECRET1','sampleID':'EARSECRET','siteID':'TEST',
               'taxonID':'PEMA','scientificName':'Peromyscus maniculatus','endDate':'2025-01-01',
               'identificationRemarks':'Taxonomic identification updated based on DNA barcoding.',
               'identificationReferences':'BOLD', 'remarks':''}]
        r=self.api()(data)
        self.assertEqual(r['molecular_mention_rows'],1)
        self.assertEqual(r['molecular_and_revision_language_rows'],1)
        self.assertEqual(r['old_Peromyscus_molecular_rows'],1)
        self.assertEqual(r['unique_molecular_historyIDs'],1)
        self.assertFalse(r['DNA_species_calls_independently_confirmed'])
        self.assertNotIn('SECRET',str(r))
    def test_duplicate_rows_do_not_multiply(self):
        d={'identificationHistoryID':'X','siteID':'A','scientificName':'Peromyscus sp.',
           'identificationRemarks':'DNA barcode updated identification','endDate':'2025'}
        r=self.api()([d,d])
        self.assertEqual(r['unique_rows'],1)
    def test_negative_statements_not_revision_evidence(self):
        r=self.api()([{'identificationRemarks':'Identification updated; no DNA confirmation available.'}])
        self.assertEqual(r['molecular_mention_rows'],1)
        self.assertEqual(r['molecular_and_revision_language_rows'],0)
    def test_current_taxon_not_taken_from_history(self):
        r=self.api()([{'scientificName':'Peromyscus leucopus','identificationRemarks':'BOLD DNA barcode'}])
        self.assertFalse(r['history_taxon_treated_as_current'])
        self.assertEqual(r['rows_without_historyID'],1)
if __name__=='__main__':unittest.main()
