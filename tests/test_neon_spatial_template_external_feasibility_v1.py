import unittest

from analysis.audit_neon_spatial_template_external_feasibility_v1 import build_support


class TestNeonSpatialTemplateExternalFeasibility(unittest.TestCase):
    def test_shared_ids_are_removed_before_species_support(self):
        targets = {"A":"Species A","B":"Species B","C":"Species C"}
        mapping = {}
        captures = []
        for event, dates in (("E1",("2025-01-01","2025-01-02")),("E2",("2025-02-01","2025-02-02"))):
            for d in dates:
                night=f"N{event}{d}"
                mapping[night]={"site":"SRER","plotID":"P1","eventID":event,"collectDate":d,"samplingType":"pathogen"}
            for sp in targets:
                # shared individual must be discarded
                captures.append({"site":"SRER","nightuid":f"N{event}{dates[0]}","plotID":"P1","collectDate":dates[0],"trapCoordinate":"A1","taxonID":sp,"tagID":f"{sp}_shared"})
                # two event-exclusive individuals per species
                for k in (1,2):
                    captures.append({"site":"SRER","nightuid":f"N{event}{dates[k-1]}","plotID":"P1","collectDate":dates[k-1],"trapCoordinate":"A2","taxonID":sp,"tagID":f"{sp}_{event}_{k}"})
        out=build_support(mapping,captures,targets)
        self.assertEqual(out["candidate_adjacent_bout_pairs"],1)
        self.assertEqual(out["eligible_adjacent_bout_units"],1)
        unit=out["eligible_units"][0]
        self.assertEqual(unit["shared_tagged_individuals_removed"],3)
        self.assertEqual(len(unit["eligible_species"]),3)
        self.assertTrue(unit["eligible"])

    def test_one_night_event_is_not_usable(self):
        targets={"A":"A","B":"B","C":"C"}
        mapping={"N1":{"site":"SRER","plotID":"P1","eventID":"E1","collectDate":"2025-01-01","samplingType":"pathogen"}}
        captures=[
            {"site":"SRER","nightuid":"N1","plotID":"P1","collectDate":"2025-01-01","trapCoordinate":"A1","taxonID":"A","tagID":"x"}
        ]
        out=build_support(mapping,captures,targets)
        self.assertEqual(out["usable_pathogen_plot_events"],0)
        self.assertEqual(out["eligible_adjacent_bout_units"],0)

    def test_diversity_grid_is_excluded(self):
        targets={"A":"A","B":"B","C":"C"}
        mapping={
            "N1":{"site":"SRER","plotID":"P1","eventID":"E1","collectDate":"2025-01-01","samplingType":"diversity"},
            "N2":{"site":"SRER","plotID":"P1","eventID":"E1","collectDate":"2025-01-02","samplingType":"diversity"},
        }
        captures=[
            {"site":"SRER","nightuid":"N1","plotID":"P1","collectDate":"2025-01-01","trapCoordinate":"A1","taxonID":"A","tagID":"x"},
            {"site":"SRER","nightuid":"N2","plotID":"P1","collectDate":"2025-01-02","trapCoordinate":"A2","taxonID":"A","tagID":"x"},
        ]
        out=build_support(mapping,captures,targets)
        self.assertEqual(out["usable_pathogen_plot_events"],0)


if __name__ == "__main__":
    unittest.main()
