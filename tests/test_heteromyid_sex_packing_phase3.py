from __future__ import annotations

import unittest

from analysis import analyze_heteromyid_sex_packing_phase3_v1 as m


def row(source,species,unit,delta,n=3,pit=1.0,known=1.0):
    key="plot_id" if source=="Portal" else "site"
    return {
        "source":source,
        "species":species,
        key:unit,
        "delta_sex_packing":delta,
        "n_male":n,
        "n_female":n,
        "pit_reliable_fraction":pit if source=="Portal" else "",
        "known_sex_fraction":known,
    }


class Phase3EstimatorTests(unittest.TestCase):
    def test_species_effect_weights_units_not_sessions(self):
        rows=[
            row("Portal","A alpha","1",10.0),
            row("Portal","A alpha","1",10.0),
            row("Portal","A alpha","1",10.0),
            row("Portal","A alpha","2",0.0),
        ]
        out=m.source_effect(
            rows,
            source="Portal",
            species_set=["A alpha"],
            unit_field="plot_id",
            n_min=3,
        )
        self.assertAlmostEqual(out["species"][0]["effect"],5.0)
        self.assertNotAlmostEqual(out["species"][0]["effect"],7.5)

    def test_family_effect_weights_species_equally(self):
        rows=[
            row("Portal","A alpha","1",2.0),
            row("Portal","A alpha","2",2.0),
            row("Portal","B beta","1",0.0),
            row("Portal","B beta","2",0.0),
        ]
        out=m.source_effect(
            rows,
            source="Portal",
            species_set=["A alpha","B beta"],
            unit_field="plot_id",
            n_min=3,
        )
        self.assertAlmostEqual(out["family"]["effect"],1.0)

    def test_sensitivity_does_not_drop_missing_frozen_species(self):
        rows=[
            row("Portal","A alpha","1",1.0,n=5),
            row("Portal","A alpha","2",1.0,n=5),
            row("Portal","B beta","1",2.0,n=3),
            row("Portal","B beta","2",2.0,n=3),
        ]
        out=m.source_effect(
            rows,
            source="Portal",
            species_set=["A alpha","B beta"],
            unit_field="plot_id",
            n_min=5,
        )
        self.assertEqual(
            out["family"]["status"],
            "non_estimable_full_frozen_species_set",
        )

    def test_replicated_rule_is_strict(self):
        def source(name,low):
            return {
                "family":{"effect":1.0,"ci95_low":low},
                "species":[
                    {"species":"A alpha","effect":1.0},
                    {"species":"B beta","effect":1.0},
                    {"species":"C gamma","effect":-1.0},
                ],
            }
        yes=m.replicated_decision(
            source("Portal",0.1),source("NEON",0.2),
            shared_species=["A alpha","B beta","C gamma"],
        )
        self.assertEqual(yes["decision"],"replicated_positive_support")
        no=m.replicated_decision(
            source("Portal",-0.1),source("NEON",0.2),
            shared_species=["A alpha","B beta","C gamma"],
        )
        self.assertEqual(no["decision"],"no_replicated_positive_support")


if __name__=="__main__":
    unittest.main()
