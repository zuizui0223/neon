"""Synthetic tests for source-only fate audit and frozen seven-site genus cohort.

Unknown or missing fate must NOT be relabelled released; neither test
accesses original night-2/3 capture responses.
"""
import json, unittest
from analysis.neon_macro_firstnight_fate_source_v1 import (
    category, initial_fate_source,
)

def fixture():
    private={"event_source_dates":{},"event_source_night_index":{},
             "original_firstnight_tagged_animal_genus_by_event":{}}
    traps=[]
    plots=[]
    sites={f"FAKESITE{i}" for i in range(7)}
    for site in sorted(sites):
        event=(site,site+"_P",site+"_EVENT")
        first=site+"_N0"
        private["event_source_dates"][event]=first
        for k in range(3):
            private["event_source_night_index"][site+"_N"+str(k)]=event
            plots.append({"nightuid":site+"_N"+str(k),
                          "collectDate":f"2020-05-0{k+1}"})
        for g,alias in (("Microtus","M"),("Peromyscus","P")):
            for t in range(5):
                tag=site+"_"+alias+str(t)
                private["original_firstnight_tagged_animal_genus_by_event"][(event,tag)]=g
                traps.append({
                    "_site":site, "plotID":site+"_P",
                    "nightuid":first,
                    "trapCoordinate":"A"+str(t+1 if alias=="M" else t+6),
                    "trapStatus":"5 - capture",
                    "tagID":tag,"taxonID":g,
                    "fate":"Released",
                    "_fate_column_present":True,
                })
    return private,traps,plots,sites,{"Microtus":"Microtus","Peromyscus":"Peromyscus"}

def audit(d=None):
    private,traps,plots,sites,taxa=d or fixture()
    return initial_fate_source(
        private,traps,plots,taxa,selected_sites=sites,
        expected_sites=7,min_released_microtus=30,
        min_released_peromyscus=30,min_shared_sites=6,
        min_per_genus_site=5,min_known_fate_fraction=.8
    )

class FirstnightFateSourceTests(unittest.TestCase):
    def test_explicit_release_only_source_gate_go(self):
        r,p=audit()
        self.assertEqual(r["status"],"SOURCE_EXPLICIT_RELEASE_GATED_REENCOUNTER_GO")
        self.assertEqual(r["source_explicit_release_matched_sites"],7)
        self.assertEqual(r["released_individuals_in_source_qualified_sites_by_genus"],
                         {"Microtus":35,"Peromyscus":35})
        self.assertEqual(r["original_pre_reencounter_firstnight_tag_cohort"],70)
        self.assertTrue(r["new_post_result_source_thresholds"]["passed"])
        self.assertFalse(r["boundaries"]["day2_or3_tag_matching_or_return_outcome_opened"])
        self.assertNotIn("FAKESITE",json.dumps(r))

    def test_blank_and_missing_column_are_never_assumed_released(self):
        self.assertEqual(category("",True),"BLANK_OR_UNKNOWN")
        self.assertEqual(category("",False),"COLUMN_ABSENT")
        private,traps,plots,sites,taxa=fixture()
        traps[0]["fate"]=""
        report,_=audit((private,traps,plots,sites,taxa))
        self.assertEqual(report["fate_categorical_counts_overall"]["BLANK_OR_UNKNOWN"],1)
        self.assertFalse(report["new_post_result_source_thresholds"]["passed"])
        traps[0]["_fate_column_present"]=False
        report,_=audit((private,traps,plots,sites,taxa))
        self.assertEqual(report["fate_categorical_counts_overall"]["COLUMN_ABSENT"],1)

    def test_ambiguous_firstnight_fate_is_neither_release_nor_nonrelease(self):
        private,traps,plots,sites,taxa=fixture()
        row={**traps[0],"fate":"Dead"}
        traps.append(row)
        report,_=audit((private,traps,plots,sites,taxa))
        self.assertEqual(report["conflicting_original_firstnight_fates"],1)
        self.assertFalse(report["new_post_result_source_thresholds"]["passed"])
        self.assertIn("CONFLICTING_OR_DUPLICATED_DISPOSITION",
                      report["fate_categorical_counts_overall"])

    def test_unrecognized_codes_cannot_be_promoted_to_release(self):
        self.assertEqual(category("R1",True),"OTHER_UNMAPPED")
        self.assertEqual(category("301",True),"NUMERIC_FATE_UNMAPPED")
        self.assertEqual(category("not released",True),"OTHER_UNMAPPED")
        self.assertEqual(category("release after check",True),"RELEASE_TERM_UNMAPPED")
        self.assertEqual(category("Dead",True),"DEAD_EXPLICIT")

if __name__=="__main__":
    unittest.main()
