"""Source-only NEON mammal barcoding results against immutable receipts.

Protect no-data-leak/no-genetics claims as important as successful sample joins.
NEVER opens DNA sequences, W/B, species-space coefficients or animal IDs.
"""
import json
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]

def read(path):
    return json.loads((ROOT/path).read_text(encoding="utf-8"))


class BarcodeSourceReceiptTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.schema=read("results/neon_barcode_release2026_schema_receipt_20261018.json")
        cls.join=read("results/neon_barcode_capture_sample_key_linkage_receipt_20261018.json")
        cls.bold=read("results/neon_bold_public_coi_single_sample_probe_receipt_20261018.json")
        cls.dev=read("results/multiscale_density_development_result_v1.json")
        cls.future=read("results/future_neon_provisional_holdout_decision_v1.json")

    def test_barcode_source_release_is_immutable_and_2016_2023_window(self):
        s=self.schema
        self.assertEqual(s["status"],"BARCODE_SOURCE_SCHEMA_VERIFIED_NO_BIOLOGICAL_MATCHES")
        self.assertEqual(s["release"],"RELEASE-2026")
        self.assertEqual(s["inventory_unique_files"],3536)
        self.assertEqual(s["published_product_metadata_site_count"],46)
        for x in ("mam_BOLDtaxonomy","mam_BOLDvoucherInfo",
                  "mam_BOLDcollectionData","mam_BOLDspecimenDetails"):
            d=s["release_files_by_table"][x]
            self.assertEqual(d["source_files"],884)
            self.assertEqual(d["source_sites"],46)
            self.assertEqual(d["earliest_month"],"2016-03")
            self.assertEqual(d["latest_month"],"2023-11")
        self.assertEqual(s["release_files_by_table"]["mam_barcodingqa"]["source_files"],0)
        self.assertFalse(s["W_B_or_MNKA_space_effect_opened"])

    def test_original_box_ear_to_bold_exact_key_counts(self):
        j=self.join
        self.assertEqual(j["status"],"BOLD_SAMPLE_ID_LINK_VERIFIED_METADATA_ONLY_NOT_DNA_VALIDATED")
        self.assertEqual(j["sources"]["box_pertrapnight_files_MD5_verified"],1605)
        self.assertEqual(j["capture_source_counts"]["all_trap_rows"],1930569)
        self.assertEqual(j["capture_source_counts"]["target_captures_with_ear_sampleID"],36744)
        q=j["source_sample_key_join"]
        self.assertEqual(q["captured_samples_with_nonblank_single_earSampleID"],36743)
        self.assertEqual(q["captured_sample_IDs_in_BOLD_taxonomy"],9646)
        self.assertEqual(q["captured_sample_IDs_in_BOLD_voucherInfo"],9646)
        self.assertEqual(q["capture_unique_histories_with_unambiguous_BOLD_join"],9617)
        self.assertEqual(q["capture_unique_Peromyscus_histories_with_unambiguous_BOLD_join"],4781)
        self.assertEqual(q["capture_unique_Peromyscus_histories_with_earSampleID"],19130)
        self.assertAlmostEqual(q["Peromyscus_history_sample_link_coverage_within_ear_sampled_histories"],
                               4781/19130,places=12)

    def test_all_taxonomy_labels_morphological_NOT_genetically_confirmed(self):
        j=self.join
        t=j["BOLD_taxonomy_source_counts"]
        self.assertEqual(t["source_rows"],10414)
        self.assertEqual(t["distinct_source_sampleIDs"],10412)
        self.assertEqual(t["taxonomy_identification_method_category_counts"],{"morphology":10414})
        q=j["source_sample_key_join"]
        self.assertEqual(q["BOLD_identificationMethod_count_in_linked_samples"],{"morphology":9646})
        d=q["metadata_taxonID_consistency_not_DNA_verification"]
        self.assertEqual(d["metadata_same_taxonID"],9121)
        self.assertEqual(d["metadata_different_taxonID"],523)
        self.assertEqual(d["BOLD_taxonID_outside_target_or_blank"],2)
        self.assertEqual(sum(d.values()),9646)
        self.assertFalse(q["DNA_sequence_quality_or_species_identity_proven"])
        self.assertFalse(j["scientific_boundary"]["DNA_sequence_quality_assessed"])
        self.assertFalse(j["scientific_boundary"]["sample_key_link_proves_genetic_species"])

    def test_no_source_tag_barcode_DNA_or_sequence_leaked(self):
        for document in (self.schema,self.join,self.bold):
            raw=json.dumps(document)
            self.assertNotIn("SECRET_SAMPLE",raw)
            self.assertNotIn("ATGCATGCATGC",raw)
        self.assertTrue(self.join["source_sample_key_join"]["no_raw_sample_IDs_or_animal_labels_exported"])
        self.assertFalse(self.join["scientific_boundary"]["W_B_spatial_metrics_opened"])
        self.assertFalse(self.join["scientific_boundary"]["biological_peromyscus_F_C_U_reclassified"])
        self.assertFalse(self.bold["raw_sample_ID_query_id_sequence_or_taxon_exported"])
        self.assertFalse(self.bold["W_B_or_crossscale_effects_opened"])

    def test_public_BOLD_API_403_does_not_imply_sequences_absent(self):
        b=self.bold
        self.assertEqual(b["status"],"STOP_BOLD_PUBLIC_ONE_SAMPLE_PROBE")
        self.assertEqual(b["sanitized_diagnostic"],"BOLD preprocessor API HTTP status 403")
        self.assertTrue(b["interpretation"]["no_COI_record_examined"])
        self.assertTrue(b["interpretation"]["no_DNA_species_identity_validated"])
        self.assertIn("not evidence that the specimen lacks a COI barcode",
                      b["interpretation"]["meaning"])

    def test_frozen_failed_8_genus_claim_and_mosa_hold_remain(self):
        self.assertEqual(self.dev["preregistered_guard"]["observed_positive_genus_count"],5)
        self.assertEqual(self.dev["preregistered_guard"]["required_positive_genus_count"],6)
        self.assertFalse(self.dev["preregistered_guard"]["passed"])
        self.assertFalse(self.future["scientific_decision"]["peromyscus_WB_positive_D_direction_replicated"])
        self.assertEqual(self.future["mode_replicability"]["full_five_genus_result"],
                         "NOT_ESTIMABLE_ALL_FIVE_FROZEN_GENERA")
        self.assertFalse(self.join["scientific_boundary"]["MOSA_spatial_effects_opened"])


if __name__=="__main__":
    unittest.main()
