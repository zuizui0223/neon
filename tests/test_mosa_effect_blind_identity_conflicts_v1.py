"""Synthetic-only tests: original full-history and frozen 153-month audit logic."""
import unittest
from analysis.audit_mosa_effect_blind_identity_conflicts_v1 import (
    audit_identity_conflicts,
)

FIELDS = ["TOE", "SPECIES", "DATE", "X", "Y", "GRID", "SX", "FLAGS"]
JULY = {"2000-07"}


def row(tag, day, x="3", y="B", *, sx="M", species="MN"):
    return {
        "TOE": tag, "SPECIES": species, "DATE": day, "X": x, "Y": y,
        "GRID": "MOSA", "SX": sx, "FLAGS": "",
    }


class EffectBlindIdentityTests(unittest.TestCase):
    def test_duplicate_same_station_is_not_different_station(self):
        rec = [row("a", "13/07/2000"), row("a", "13/07/2000"),
               row("a", "14/07/2000")]
        out = audit_identity_conflicts(
            rec, FIELDS, {"a"}, set(), JULY,
            expected_support_m={"2000-07": 1},
        )
        self.assertEqual(out["same_day_duplicate_same_station_keys_full_history"], 1)
        self.assertEqual(out["same_day_multiple_station_keys_full_history"], 0)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 0)
        self.assertFalse(out["ecological_effects_opened"])

    def test_same_day_two_stations_ambiguity_reaches_repeat_cohort(self):
        rec = [row("a", "13/07/2000"), row("a", "13/07/2000", "4"),
               row("a", "14/07/2000")]
        out = audit_identity_conflicts(rec, FIELDS, {"a"}, set(), JULY)
        self.assertEqual(out["same_day_multiple_station_keys_in_frozen_months"], 1)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 1)
        self.assertFalse(out["same_day_station_change_proves_code_reuse"])

    def test_excluded_collision_does_not_enter_cohort(self):
        rec = [row("a", "13/07/2000"), row("a", "13/07/2000", "4"),
               row("b", "13/07/2000"), row("b", "14/07/2000")]
        out = audit_identity_conflicts(
            rec, FIELDS, {"a", "b"}, {"a"}, JULY,
            expected_support_m={"2000-07": 1},
        )
        self.assertEqual(out["excluded_collision_codes"], 1)
        self.assertEqual(out["same_day_multiple_station_keys_full_history"], 0)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 0)

    def test_species_change_is_warning_not_MN_reassignment(self):
        rec = [row("a", "13/07/2000"), row("a", "14/07/2000"),
               row("a", "15/07/2000", species="TA")]
        out = audit_identity_conflicts(rec, FIELDS, {"a"}, set(), JULY)
        self.assertEqual(out["cross_species_codes_full_history"], 1)
        self.assertEqual(out["repeat_supported_code_month_pairs"], 1)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 1)

    def test_real_SX_sex_column_is_considered(self):
        rec = [row("a", "13/07/2000", sx="M"),
               row("a", "14/07/2000", sx="F")]
        out = audit_identity_conflicts(rec, FIELDS, {"a"}, set(), JULY)
        self.assertEqual(out["cross_sex_SX_codes_full_history"], 1)
        self.assertEqual(out["known_M_or_F_SX_MN_capture_rows"], 2)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 1)

    def test_unknown_SX_is_not_a_conflict(self):
        rec = [row("a", "13/07/2000", sx="M"),
               row("a", "14/07/2000", sx="NA")]
        out = audit_identity_conflicts(rec, FIELDS, {"a"}, set(), JULY)
        self.assertEqual(out["cross_sex_SX_codes_full_history"], 0)
        self.assertEqual(out["unknown_or_other_SX_MN_capture_rows"], 1)

    def test_suspect_only_single_night_not_affected(self):
        rec = [row("a", "13/07/2000", sx="M"),
               row("a", "14/07/2000", sx="F"),
               row("b", "13/07/2000"), row("b", "14/07/2000")]
        # The suspect a is excluded, b is the sole repeated cohort ID.
        out = audit_identity_conflicts(rec, FIELDS, {"a", "b"}, {"a"}, JULY)
        self.assertEqual(out["repeat_supported_distinct_codes"], 1)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 0)

    def test_full_history_warning_affects_frozen_month_only_as_upper_bound(self):
        rec = [row("a", "13/07/2000"), row("a", "14/07/2000"),
               row("a", "13/08/2000", sx="M"),
               row("a", "13/08/2000", x="4", sx="M")]
        out = audit_identity_conflicts(rec, FIELDS, {"a"}, set(), JULY)
        self.assertEqual(out["same_day_multiple_station_keys_full_history"], 1)
        self.assertEqual(out["same_day_multiple_station_keys_in_frozen_months"], 0)
        self.assertEqual(out["potentially_affected_months_upper_bound"], 1)

    def test_frozen_m_drift_is_error(self):
        rec = [row("a", "13/07/2000"), row("a", "14/07/2000")]
        with self.assertRaisesRegex(ValueError, "Frozen repeat-supported m"):
            audit_identity_conflicts(
                rec, FIELDS, {"a"}, set(), JULY,
                expected_support_m={"2000-07": 5},
            )

    def test_missing_real_SX_column_is_error(self):
        rec = [row("a", "13/07/2000"), row("a", "14/07/2000")]
        with self.assertRaisesRegex(ValueError, "SX"):
            audit_identity_conflicts(
                rec, [c for c in FIELDS if c != "SX"],
                {"a"}, set(), JULY,
            )

    def test_unexpected_grid_fails_closed(self):
        rec = [row("a", "13/07/2000"), row("a", "14/07/2000")]
        rec[0]["GRID"] = "OTHER"
        with self.assertRaisesRegex(ValueError, "unexpected grid"):
            audit_identity_conflicts(rec, FIELDS, {"a"}, set(), JULY)

    def test_no_individual_ids_or_dates_emitted(self):
        rec = [row("UNIQUE_ANIMAL_LABEL", "13/07/2000"),
               row("UNIQUE_ANIMAL_LABEL", "14/07/2000")]
        out = audit_identity_conflicts(
            rec, FIELDS, {"UNIQUE_ANIMAL_LABEL"}, set(), JULY
        )
        self.assertNotIn("UNIQUE_ANIMAL_LABEL", str(out))
        self.assertNotIn("2000-07", str(out))
        self.assertFalse(out["raw_TOE_values_or_calendar_dates_exported"])


if __name__ == "__main__":
    unittest.main()
