from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
LOCK=ROOT/"validation"/"public_mammal_space_use_v1"/"phase2_analysis_lock_v1.json"


class PublicMammalPhase2LockTests(unittest.TestCase):
    def setUp(self):
        self.lock=json.loads(LOCK.read_text(encoding="utf-8"))

    def test_source_artifacts_are_exactly_frozen(self):
        self.assertEqual(self.lock["source_artifacts"]["portal"]["artifact_id"],10929728652)
        self.assertEqual(
            self.lock["source_artifacts"]["portal"]["digest"],
            "sha256:eb031608a547092340592a0127361283a2560ca22db9a1b3dc9a368fbef07686",
        )
        self.assertEqual(self.lock["source_artifacts"]["portal"]["workflow_run_id"],36314012402)
        self.assertEqual(self.lock["source_artifacts"]["neon"]["artifact_id"],10931291060)
        self.assertEqual(
            self.lock["source_artifacts"]["neon"]["digest"],
            "sha256:865880ceac9cd0dbaffa160b515165c909380c2bd67eea14c70ab76756636cc9",
        )
        self.assertEqual(self.lock["source_artifacts"]["neon"]["workflow_run_id"],36315906620)

    def test_portal_primary_contract_is_frozen(self):
        p=self.lock["portal_primary"]
        self.assertEqual(p["species"],"Chaetodipus penicillatus")
        self.assertEqual(p["n_min"],5)
        self.assertEqual(p["treatments"],["control","kangaroo_rat_exclosure"])
        self.assertEqual(p["session_treatment_mapping"],{"control":"control","exclosure":"kangaroo_rat_exclosure"})
        self.assertEqual(p["formula"],"packing_z ~ treatment * z_logN")
        self.assertEqual(p["mixedlm_groups"],"constant_all_rows")
        self.assertEqual(p["re_formula"],"0")
        self.assertEqual(p["variance_components"],{"plot":"0 + C(plot_id)","period":"0 + C(period)"})

    def test_neon_primary_contract_is_frozen(self):
        n=self.lock["neon_primary"]
        self.assertEqual(n["species"],"Myodes rutilus")
        self.assertEqual(n["sites"],["BONA","DEJU"])
        self.assertEqual(n["habitats"],["forest","shrub_scrub"])
        self.assertEqual(n["n_min"],5)
        self.assertEqual(n["formula"],"packing_z ~ habitat_group + z_logN + site")

    def test_secondary_neon_family_is_fixed(self):
        self.assertEqual(
            self.lock["neon_secondary_within_site"],
            [
                {"species":"Chaetodipus hispidus","site":"OAES","habitats":["grassland_herbaceous","shrub_scrub"]},
                {"species":"Perognathus parvus","site":"ONAQ","habitats":["forest","shrub_scrub"]},
                {"species":"Peromyscus boylii","site":"SJER","habitats":["forest","grassland_herbaceous"]},
            ],
        )

    def test_modeling_and_standardization_are_frozen(self):
        self.assertEqual(self.lock["software"]["pandas"],"3.0.6")
        self.assertEqual(self.lock["software"]["scipy"],"1.18.1")
        self.assertEqual(self.lock["software"]["statsmodels"],"0.15.0")
        self.assertEqual(self.lock["z_logN"]["ddof"],0)
        self.assertEqual(self.lock["n_thresholds"],[3,5,8])
        self.assertEqual(self.lock["portal_primary"]["optimizer_sequence"],["lbfgs","bfgs","cg"])
        self.assertTrue(self.lock["portal_primary"]["reml"])
        self.assertEqual(self.lock["ecological_model_fits_at_lock"],0)


if __name__=="__main__":
    unittest.main()
