"""Public BOLD one-sample API pilot tests; synthetic data only."""
from __future__ import annotations
import json
import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from io import BytesIO

from analysis.audit_neon_bold_public_coi_pilot_v1 import (
    choose_pilot_files,select_source_candidate,
    _public_record_summary,public_json
)


class BoldOneSamplePublicProbeTests(unittest.TestCase):
    def test_metadata_only_earliest_file_per_source_site(self):
        def src(site,month):
            return dict(site=site,month=month,
                        name=f"NEON.D01.{site}.DP1.10076.001.mam_BOLDtaxonomy.{month}.basic.20260201T000000Z.csv")
        source=[src("SITE","2022-07"),src("SITE","2019-02"),
                src("AAAA","2020-09"),src("ZZZZ","2018-04")]
        picked=choose_pilot_files(source)
        self.assertEqual(len(picked),3)
        self.assertEqual([(x["site"],x["month"]) for x in picked],
                         [("AAAA","2020-09"),("SITE","2019-02"),("ZZZZ","2018-04")])

    def test_one_archival_sample_selected_without_ecological_response_peek(self):
        sources=[dict(site="TEST",month="2020-02")]
        raw=(
            "sampleID,taxonID,genus,identificationMethod\n"
            "ZZZ1,PELE,Peromyscus,morphology\n"
            "AAA1,PEMA,Peromyscus,morphology\n"
            "B22,SIHI,Sigmodon,morphology\n"
        ).encode()
        sid,receipt=select_source_candidate(
            sources,[raw],{"PELE":"Peromyscus","PEMA":"Peromyscus","SIHI":"Sigmodon"}
        )
        self.assertEqual(sid,"AAA1")
        self.assertEqual(receipt["candidate_archive_rows"],2)
        self.assertEqual(receipt["unique_candidate_sampleIDs"],2)
        self.assertNotIn("AAA1",str(receipt))
        self.assertTrue(receipt["no_sample_ID_returned_in_receipt"])

    def test_document_summary_does_not_emit_sequence_or_id(self):
        mock={
            "data":[{
                "sampleid":"SECRET_SAMPLE",
                "marker_code":"COI-5P",
                "nuc":"ATGC"*200,
                "taxon":"Peromyscus maniculatus",
            }]
        }
        r=_public_record_summary(mock,"SECRET_SAMPLE")
        self.assertEqual(r["parsed_document_count_guess"],1)
        self.assertTrue(r["exact_query_sample_value_appeared_in_public_record"])
        self.assertGreater(r["possible_nucleotide_sequence_property_count"],0)
        self.assertGreater(r["possible_marker_or_accession_property_count"],0)
        self.assertNotIn("SECRET_SAMPLE",str(r))
        self.assertNotIn("ATGCATGC",str(r))
        self.assertTrue(r["no_sequence_or_identification_exported"])

    def test_wrong_sample_id_is_not_public_validation(self):
        r=_public_record_summary({"records":[{"sampleid":"OTHER","nuc":"ACGT"}]},"SECRET")
        self.assertFalse(r["exact_query_sample_value_appeared_in_public_record"])

    def test_http_error_never_exposes_original_sample_id(self):
        err=HTTPError("https://portal.boldsystems.org/api/query?query=ids:sampleid:SECRET",
                      403,"Forbidden",{},BytesIO(b"IDSECRET"))
        with patch("analysis.audit_neon_bold_public_coi_pilot_v1.urllib.request.urlopen",side_effect=err):
            with self.assertRaisesRegex(RuntimeError,"BOLD query API HTTP status 403") as cm:
                public_json("query","/api/query",{"query":"ids:sampleid:SECRET"})
        self.assertNotIn("SECRET",str(cm.exception))

if __name__=="__main__":
    unittest.main()
