"""Synthetic tests for distinct conspecific versus congeneric predictor feasibility.

No W/B, trap distances or response outcomes anywhere in the test universe.
"""
import unittest

from analysis.conspecific_congeneric_predictor_support_v1 import (
    GROUP_TAXON_IDS,
    classify_history,
    event_predictors,
    response_predictor_rows,
    genus_support,
)

TAXONOMY={"PEMA":"Peromyscus","PELE":"Peromyscus",
          "PELEPEMA":"Peromyscus","DIOR":"Dipodomys"}
SPECIES={"PEMA","PELE","DIOR"}


def row(taxon="PEMA",site="A",plot="P",event="e3",year="2020",month="07"):
    return {"taxon":taxon,"genus":TAXONOMY[taxon],"site":site,
            "plot_id":plot,"event_id":event,"year":year,"month":month}


class ConspecificCongenericSupportTests(unittest.TestCase):
    def test_classification_resolved_group_and_genus_switch(self):
        self.assertEqual(classify_history(["PEMA"],TAXONOMY,SPECIES),
                         ("RESOLVED_SPECIES","Peromyscus","PEMA"))
        self.assertEqual(classify_history(["PELEPEMA"],TAXONOMY,SPECIES),
                         ("UNRESOLVED_IN_GENUS","Peromyscus",None))
        self.assertEqual(classify_history(["PELE","PEMA"],TAXONOMY,SPECIES),
                         ("UNRESOLVED_IN_GENUS","Peromyscus",None))
        self.assertEqual(classify_history(["PEMA","DIOR"],TAXONOMY,SPECIES),
                         ("CROSS_GENUS",None,None))
        self.assertIn("PELEPEMA", GROUP_TAXON_IDS)

    def test_qualifier_moves_single_species_history_to_unresolved_only_when_enabled(self):
        self.assertEqual(
            classify_history(["PEMA"],TAXONOMY,SPECIES,qualifier_warning=True),
            ("UNRESOLVED_IN_GENUS","Peromyscus",None))
        self.assertEqual(
            classify_history(["PEMA"],TAXONOMY,SPECIES,qualifier_warning=False),
            ("RESOLVED_SPECIES","Peromyscus","PEMA"))

    def test_qualifier_sensitivity_preserves_genus_N_and_frozen_events(self):
        histories=[
            dict(site="A",plot_id="P",taxon_ids=["PEMA"],
                 event_ids=["e1","e3"],qualifier_warning=True),
            dict(site="A",plot_id="P",taxon_ids=["PELE"],
                 event_ids=["e2","e3"],qualifier_warning=False),
            dict(site="A",plot_id="P",taxon_ids=["PELEPEMA"],
                 event_ids=["e2"],qualifier_warning=True),
        ]
        params=dict(ordered_events={("A","P"):["e1","e2","e3"]},
                    histories=histories,genus_by_taxon=TAXONOMY,
                    resolved_species_ids=SPECIES)
        baseline,bcount=event_predictors(**params)
        conservative,ccount=event_predictors(
            **params,respect_qualifier_warning=True)
        self.assertEqual(set(baseline),set(conservative))
        self.assertEqual(ccount["RESOLVED_SPECIES"],1)
        self.assertEqual(bcount["RESOLVED_SPECIES"],2)
        for key in baseline:
            self.assertEqual(baseline[key]["N"],conservative[key]["N"])
        key=("A","P","e2","Peromyscus")
        self.assertEqual(baseline[key]["N"],3)
        self.assertEqual(baseline[key]["unresolved"],1)
        self.assertEqual(conservative[key]["unresolved"],2)
        self.assertEqual(conservative[key]["resolved_species_counts"],{"PELE":1})

    def test_qualifier_never_makes_cross_genus_history_resolved(self):
        self.assertEqual(
            classify_history(["PEMA","DIOR"],TAXONOMY,SPECIES,qualifier_warning=True),
            ("CROSS_GENUS",None,None))

    def test_event_interval_and_exact_decomposition(self):
        histories=[
            dict(site="A",plot_id="P",taxon_ids=["PEMA"],event_ids=["e1","e3"]),
            dict(site="A",plot_id="P",taxon_ids=["PELE"],event_ids=["e2","e4"]),
            dict(site="A",plot_id="P",taxon_ids=["PELEPEMA"],event_ids=["e3"]),
            dict(site="A",plot_id="P",taxon_ids=["PELE","PEMA"],event_ids=["e2","e4"]),
            dict(site="A",plot_id="P",taxon_ids=["PEMA","DIOR"],event_ids=["e4"]),
        ]
        out,summary=event_predictors(
            ordered_events={("A","P"):["e1","e2","e3","e4"]},
            histories=histories,genus_by_taxon=TAXONOMY,
            resolved_species_ids=SPECIES,
        )
        self.assertEqual(summary["RESOLVED_SPECIES"],2)
        self.assertEqual(summary["UNRESOLVED_IN_GENUS"],2)
        self.assertEqual(summary["CROSS_GENUS"],1)
        self.assertEqual(out[("A","P","e1","Peromyscus")]["N"],1)
        self.assertEqual(out[("A","P","e3","Peromyscus")]["N"],4)
        self.assertEqual(out[("A","P","e4","Peromyscus")]["N"],2)
        rr,meta=response_predictor_rows([row(),row("PELE"),row("PELEPEMA")],
                                        out,resolved_species_ids=SPECIES)
        self.assertEqual((rr[0]["N"],rr[0]["F"],rr[0]["C"],rr[0]["U"]),
                         (4,1,1,2))
        self.assertEqual((rr[1]["F"],rr[1]["C"],rr[1]["U"]), (1,1,2))
        self.assertIsNone(rr[2]["F"])
        self.assertIsNone(rr[2]["C"])
        self.assertEqual(meta["species_group_response_sessions"],1)

    def test_history_cannot_claim_capture_outside_event_sequence(self):
        with self.assertRaisesRegex(ValueError,"not contained"):
            event_predictors(
                ordered_events={("A","P"):["e1","e2"]},
                histories=[dict(site="A",plot_id="P",taxon_ids=["PEMA"],event_ids=["e0"])],
                genus_by_taxon=TAXONOMY,resolved_species_ids=SPECIES,
            )

    def test_taxonomy_missing_fails_closed(self):
        with self.assertRaisesRegex(ValueError,"unknown target taxon"):
            classify_history(["UNKNOWN"],TAXONOMY,SPECIES)

    def test_full_rank_predictor_support_requires_joint_variation(self):
        observations=[]
        for g in range(8):
            site=f"Site{g}"
            for e in range(12):
                observations.append({
                    "taxon":"PEMA","genus":"Peromyscus","site":site,
                    "plot_id":"P","event_id":f"E{e}","series_id":f"PEMA|{site}|P",
                    "year":str(2020+e%3),"site_month":site+"|07",
                    "N":8+(g*e)%5+(2*g+3*e)%4,"F":3+(g*e)%5,
                    "C":1+(2*g+3*e)%4,"U":4,
                    "strictly_resolved_response_taxon":True,
                })
        result=genus_support(observations,all_genera=["Peromyscus","Sigmodon"])
        p=result["Peromyscus"]
        self.assertEqual(p["species_sessions_in_3plus_series"],96)
        self.assertEqual(p["sites_in_3plus_series"],8)
        self.assertEqual(p["series_joint_F_C_variation"],6)  # g=0 and g=5 have constant F
        self.assertEqual(p["fixed_effects_predictor_geometry"]["predictor_rank_after_FE"],2)
        self.assertEqual(p["state"],"PREDICTOR_ONLY_POTENTIALLY_IDENTIFIABLE")
        self.assertEqual(result["Sigmodon"]["state"],"PREDICTOR_ONLY_STRUCTURAL_LIMIT")
        self.assertTrue(p["no_spatial_effect_or_W_B_opened"])

    def test_collinear_predictors_not_identifiable_even_with_many_records(self):
        rr=[]
        for g in range(8):
            for e in range(12):
                f=3+(g*e)%4
                rr.append({
                    "taxon":"PEMA","genus":"Peromyscus","site":f"S{g}",
                    "plot_id":"P","event_id":str(e),
                    "series_id":f"PEMA|S{g}|P","year":str(2017+e%3),
                    "site_month":f"S{g}|05","N":f*3,"F":f,"C":2*f,
                    "U":0,"strictly_resolved_response_taxon":True,
                })
        r=genus_support(rr,all_genera=["Peromyscus"])["Peromyscus"]
        self.assertEqual(r["fixed_effects_predictor_geometry"]["predictor_rank_after_FE"],1)
        self.assertEqual(r["state"],"PREDICTOR_ONLY_STRUCTURAL_LIMIT")

    def test_unresolved_fraction_is_not_assumed_zero(self):
        rr=[{
            "taxon":"PEMA","genus":"Peromyscus","site":"S","plot_id":"P",
            "event_id":str(k),"series_id":"PEMA|S|P","year":"2020",
            "site_month":"S|07","N":10,"F":4,"C":2,"U":4,
            "strictly_resolved_response_taxon":True
        } for k in range(3)]
        o=genus_support(rr,all_genera=["Peromyscus"])["Peromyscus"]
        self.assertAlmostEqual(o["fraction_of_genus_N_unresolved"],0.4)
        self.assertEqual(o["state"],"PREDICTOR_ONLY_STRUCTURAL_LIMIT")


if __name__=="__main__":
    unittest.main()
