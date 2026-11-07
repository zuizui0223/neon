from __future__ import annotations

import unittest

from analysis.lock_multiscale_density_target_taxa_v1 import lock


class MultiscaleDensityTargetTaxonLockTests(unittest.TestCase):
    def test_retains_target_composite_concept_without_forcing_species_rank(self):
        roster = {"primary_taxon_concepts": ["PEMA", "PELEPEMA", "RARA"]}
        payload = {
            "data": [
                {
                    "taxonID": "PEMA",
                    "dwc:scientificName": "Peromyscus maniculatus",
                    "dwc:taxonRank": "species",
                    "taxonProtocolCategory": "target",
                },
                {
                    "taxonID": "PELEPEMA",
                    "dwc:scientificName": "Peromyscus leucopus / maniculatus",
                    "dwc:taxonRank": "speciesGroup",
                    "taxonProtocolCategory": "target",
                },
                {
                    "taxonID": "RARA",
                    "dwc:scientificName": "Rattus rattus",
                    "dwc:taxonRank": "species",
                    "taxonProtocolCategory": "nonTarget",
                },
            ]
        }
        out = lock(roster, payload)
        self.assertEqual(out["target_taxon_count"], 2)
        self.assertEqual(out["non_target_taxon_count"], 1)
        ids = {x["taxon_id"] for x in out["target_taxon_concepts"]}
        self.assertEqual(ids, {"PEMA", "PELEPEMA"})
        ranks = {x["taxon_id"]: x["taxon_rank"] for x in out["target_taxon_concepts"]}
        self.assertEqual(ranks["PELEPEMA"], "speciesGroup")

    def test_missing_taxon_is_reported(self):
        out = lock(
            {"primary_taxon_concepts": ["MISSING"]},
            {"data": []},
        )
        self.assertEqual(out["missing_taxon_ids"], ["MISSING"])


if __name__ == "__main__":
    unittest.main()
