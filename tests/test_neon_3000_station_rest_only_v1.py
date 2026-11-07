"""Source-only 3000 official REST route guards; no mammal effects opened."""
import unittest
from pathlib import Path
from analysis.neon_graphql_dated_station_source_v1 import summarize_full_station_dated_coverage
from datetime import date

class OriginalRestRouteTests(unittest.TestCase):
    def test_new_3000_route_has_no_graphql_location_fetch(self):
        text=Path("analysis/run_neon_3000_station_dated_rest_v1.py").read_text()
        self.assertIn('REST_FULL_3000_LOCATION_HISTORIES',text)
        self.assertIn('ThreadPoolExecutor(max_workers=8)',text)
        self.assertIn('BASE+"locations/"+quote(full',text)
        self.assertNotIn('_gql(',text)
        self.assertNotIn('GRAPHQL_FULL_3000_BATCHES',text)
        self.assertIn('"previous_GraphQL_REST_preflight_STOP_preserved":True',text)

    def test_source_coverage_unchanged(self):
        source=Path("analysis/neon_graphql_dated_station_source_v1.py").read_text()
        self.assertIn('min_pairs:int=40,min_sites:int=8,min_plots:int=20',source)
        self.assertIn('fixed_original_station_date_attempts',source)
        self.assertIn('source_date_and_geographic_coverage_gate_passed',source)

    def test_no_source_effect_export(self):
        text=Path("analysis/run_neon_3000_station_dated_rest_v1.py").read_text()
        self.assertIn('"genus_habitat_detection_or_competition_effect_computed":False',text)
        self.assertIn('"raw_source_site_and_station_names_and_coords_exported":False',text)

if __name__=="__main__":
    unittest.main()
