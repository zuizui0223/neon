"""Synthetic data only: source provenance is not independent DNA identity."""
import importlib
import json
import unittest

try:
    audit = importlib.import_module('analysis.audit_neon_identification_evidence_v1')
except ModuleNotFoundError:
    audit = None


def payload(files, release='RELEASE-2026', package='expanded'):
    return {'data': {'releases': [{'release': release, 'packages': [{
        'siteCode':'TEST', 'month':'2020-07', 'packageType':package,
        'files':files}]}]}}


def meta(table='mam_identificationHistory'):
    return {'name':f'NEON.D01.TEST.DP1.10072.001.{table}.2020-07.expanded.20260101T000000Z.csv',
            'size':100,'md5':'a'*32,'url':'https://data.neonscience.org/source.csv'}


class IdentificationEvidenceTests(unittest.TestCase):
    def feature(self, name):
        self.assertTrue(audit is not None and callable(getattr(audit, name, None)), name+' not implemented')
        return getattr(audit,name)

    def test_inventory_never_downloads_spatial_response(self):
        f=self.feature('extract_history_inventory')
        selected, overview=f(payload([meta(),meta('mam_pertrapnight')]))
        self.assertEqual(len(selected),1)
        self.assertEqual(selected[0]['table'],'mam_identificationHistory')
        self.assertEqual(overview['all_csv_tables']['mam_pertrapnight'],1)
        self.assertEqual(selected[0]['release'],'RELEASE-2026')

    def test_bad_hash_and_duplicate_manifest_fail(self):
        f=self.feature('extract_history_inventory')
        bad=meta();bad['md5']='oops'
        with self.assertRaisesRegex(ValueError,'MD5'):
            f(payload([bad]))
        conflicting=meta();conflicting['size']=101
        with self.assertRaisesRegex(ValueError,'conflict'):
            f(payload([meta(),conflicting]))

    def test_csv_candidate_is_not_confirmation_and_ids_not_exported(self):
        f=self.feature('summarize_history_csv')
        raw=(
            'identificationHistoryID,taxonID,identificationMethod,remarks\n'
            'SECRET1,PEMA,morphology,field check\n'
            'SECRET2,PELE,DNA barcode,COI comparison with BOLD\n'
            'SECRET3,PEMA,review,no DNA confirmation available\n'
        ).encode()
        result=f(raw)
        self.assertEqual(result['rows'],3)
        self.assertEqual(result['explicit_molecular_method_rows'],1)
        self.assertEqual(result['any_molecular_mention_rows'],2)
        self.assertEqual(result['negative_or_pending_evidence_rows'],1)
        self.assertFalse(result['molecular_species_identity_proven'])
        self.assertFalse(result['historical_taxon_is_current_taxon'])
        self.assertNotIn('SECRET',json.dumps(result))
        self.assertNotIn('field check',json.dumps(result))

    def test_missing_rationale_is_not_negative_genetic_result(self):
        f=self.feature('summarize_history_csv')
        result=f(b'identificationHistoryID,taxonID\nSECRET1,PEMA\n')
        self.assertFalse(result['rationale_columns_present'])
        self.assertEqual(result['any_molecular_mention_rows'],0)
        self.assertEqual(result['evidence_status'],'NO_RATIONALE_COLUMNS')

    def test_ragged_header_and_unbounded_disclosures_rejected(self):
        f=self.feature('summarize_history_csv')
        for raw in [b'a,a\n1,2\n', b'a,b\n1\n']:
            with self.assertRaises(ValueError):
                f(raw)

    def test_releases_not_merged(self):
        f=self.feature('extract_history_inventory')
        data=payload([meta()]); later=payload([meta()],release='PROVISIONAL')
        data['data']['releases'] += later['data']['releases']
        selected,overview=f(data)
        self.assertEqual({r['release'] for r in selected},{'RELEASE-2026','PROVISIONAL'})
        self.assertEqual(len(selected),2)

    def test_remarks_not_personal_names_matching_dna(self):
        f=self.feature('summarize_history_csv')
        result=f(b'identificationHistoryID,identifiedBy,remarks\nSECRET1,BOLD Jones,field review\n')
        self.assertEqual(result['any_molecular_mention_rows'],0)
        self.assertNotIn('BOLD Jones',json.dumps(result))


if __name__=='__main__':
    unittest.main()
