from pathlib import Path
import json
import unittest

ROOT=Path(__file__).resolve().parents[1]
MANIFEST=ROOT/"validation"/"public_mammal_space_use_v1"/"source_manifest_v1.json"

import importlib.util
MODULE=ROOT/"analysis"/"public_mammal_source_contracts_v1.py"
spec=importlib.util.spec_from_file_location("contracts",MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class PublicMammalSourceContractTests(unittest.TestCase):
    def test_manifest_pins_portal_and_neon_sources(self):
        manifest=m.load_source_manifest(MANIFEST)
        self.assertEqual(
            manifest["portal"]["repository"],
            "weecology/PortalData",
        )
        self.assertEqual(
            manifest["portal"]["commit_sha"],
            "72d7ff8568052763bf6899dc462e285684cf20f6",
        )
        self.assertEqual(
            manifest["neon"]["product_code"],
            "DP1.10072.001",
        )
        self.assertEqual(
            manifest["neon"]["release"],
            "RELEASE-2026",
        )
        self.assertEqual(
            manifest["neon"]["inferential_status"],
            "retrospective_development_only",
        )

    def test_portal_required_files_are_complete(self):
        manifest=m.load_source_manifest(MANIFEST)
        m.validate_portal_contract(manifest)
        self.assertEqual(
            set(manifest["portal"]["required_files"]),
            {
                "Rodents/Portal_rodent.csv",
                "Rodents/Portal_rodent_trapping.csv",
                "Rodents/Portal_rodent_species.csv",
                "SiteandMethods/Portal_plots.csv",
                "SiteandMethods/Portal_UTMCoords.csv",
            },
        )

    def test_neon_required_tables_are_complete(self):
        manifest=m.load_source_manifest(MANIFEST)
        m.validate_neon_contract(manifest)
        self.assertEqual(
            set(manifest["neon"]["required_tables"]),
            {
                "mam_perplotnight",
                "mam_pertrapnight",
                "mam_identificationHistory",
            },
        )

    def test_manifest_never_contains_token_value(self):
        text=MANIFEST.read_text(encoding="utf-8")
        self.assertNotIn("NEON_API_TOKEN=",text)
        manifest=json.loads(text)
        self.assertEqual(
            manifest["neon"]["authentication"]["environment_variable"],
            "NEON_API_TOKEN",
        )


if __name__=="__main__":
    unittest.main()
