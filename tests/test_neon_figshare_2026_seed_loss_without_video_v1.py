"""No-source behavioral effect tests: 2026 original station-night seed census."""
from __future__ import annotations
import unittest
from analysis.audit_neon_figshare_2026_seed_loss_without_video_v1 import (
    descriptive,parse_seed_count,
)

class TestOriginalStationSeedLossWithoutVideo(unittest.TestCase):
    def example(self):
        nights=[]
        events=[]
        for n in range(288):
            key={"Grid":"G1","Site":f"S{n}","Session":"S","Night":"1"}
            row={**key,"Night.set":"setup","Morning.check":"check",
                 "WP.seeds.set":"5","WP.seeds.left":"4" if n<136 or (136<=n<146) else "5",
                 "RO.seeds.set":"3","RO.seeds.left":"3"}
            nights.append(row)
            if n<136:
                events.append({**key,"Visit.ID":"v1"})
        while len(events)<3243:
            events.append({**nights[0],"Visit.ID":"repeat"})
        nights.extend([
            {"Grid":"","Site":"","Session":"","Night":"",
             "WP.seeds.set":"5","WP.seeds.left":"4",
             "RO.seeds.set":"3","RO.seeds.left":"3"},
            {"Grid":"","Site":"","Session":"","Night":"",
             "WP.seeds.set":"10","RO.seeds.set":"10"},
            {"Grid":"","Site":"","Session":"","Night":"",
             "WP.seeds.set":"7","RO.seeds.set":"7"}
        ])
        return nights,events

    def test_two_video_opportunity_classes_seed_loss_not_imputed_animal(self):
        nights,events=self.example()
        result=descriptive(nights,events)
        self.assertEqual(result["status"],
            "RETROSPECTIVE_STATION_SOURCE_SEED_DISAPPEARANCE_DESCRIPTIVE_ONLY")
        counts=result["seed_disappearance_effect_or_descriptive_numerators"]
        self.assertEqual(counts["recorded_camera_event"]["source_nights_with_any_seed_missing"],136)
        self.assertEqual(counts["no_recorded_camera_event"]["source_nights_with_any_seed_missing"],10)
        self.assertEqual(counts["no_recorded_camera_event"]["original_WP_seeds_missing"],10)
        self.assertTrue(result["original_source_frozen_all_291_station_row_GO_remains_FAILED"])

    def test_more_remaining_than_set_fails_retro_QA_not_clipped(self):
        nights,events=self.example()
        nights[164]["RO.seeds.left"]="9"
        output=descriptive(nights,events)
        self.assertEqual(output["status"],"SOURCE_STOP_SEED_COUNT_QUALITY_OR_STRATUM_SUPPORT")
        self.assertIsNone(output["seed_disappearance_effect_or_descriptive_numerators"])

    def test_bad_source_numeric_fails_closed(self):
        for t in ("-1","1.1","inf"):
            with self.assertRaisesRegex(ValueError,"NONINTEGER|NEGATIVE_OR_NONFINITE"):
                parse_seed_count(t)
        # Original NAN is an explicit missingness marker, not a numeric zero.
        self.assertIsNone(parse_seed_count("nan"))

    def test_blank_source_field_reduces_data_not_zero(self):
        nights,events=self.example()
        for n in range(136,206):
            nights[n]["RO.seeds.left"]=""
        result=descriptive(nights,events)
        self.assertEqual(result["status"],"SOURCE_STOP_SEED_COUNT_QUALITY_OR_STRATUM_SUPPORT")
        self.assertEqual(result["numeric_complete_station_nights_by_video_event_class"]["no_recorded_camera_event"],82)

if __name__=="__main__":
    unittest.main()
