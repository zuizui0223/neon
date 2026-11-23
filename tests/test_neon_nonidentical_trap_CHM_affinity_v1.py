"""Synthetic-only frozen canopy-affinity test and trap fixed-margin null."""
from __future__ import annotations

import unittest
from analysis.neon_nonidentical_trap_CHM_affinity_v1 import (
    TRAPS,rank100,exclusive_score,original_unit_test,summarize_original_sites
)
from analysis.run_neon_nonidentical_trap_CHM_affinity_v1 import (
    OriginalRESTHistoryStop,_audit_rest_history_rows
)

def height_gradient():
    return {x:float(ord(x[0])-65) for x in TRAPS}

def pair():
    A={"genus_alpha":{"J1","J2"},"genus_beta":{"A1","A2"},
       "genus_gamma":{"F1","F2"}}
    B={"genus_alpha":{"J3","J4"},"genus_beta":{"A3","A4"},
       "genus_gamma":{"F3","F4"}}
    return A,B

class TestOtherTrapCanopyAssociation(unittest.TestCase):
    def test_midrank_ties_are_not_random_jitter(self):
        h=height_gradient()
        r=rank100(h)
        self.assertAlmostEqual(r["A1"],r["A10"])
        self.assertLess(r["A1"],r["J10"])
        self.assertAlmostEqual(sum(r.values())/100,0.5)
        self.assertEqual(len(r),100)

    def test_B_identical_old_stations_contributes_no_false_novel_canopy_signal(self):
        A,_=pair()
        h=height_gradient()
        score,n=exclusive_score(A,A,rank100(h),rank100(h))
        self.assertEqual(score,0.)
        self.assertEqual(n,0)

    def test_new_B_stations_can_retain_genus_canopy_affinity(self):
        A,B=pair()
        h=height_gradient()
        sc,n=exclusive_score(A,B,rank100(h),rank100(h))
        self.assertGreater(sc,0)
        self.assertEqual(n,3)

    def test_fixed_margin_genus_x_station_source_null_returns_finite_z(self):
        A,B=pair()
        h=height_gradient()
        v=original_unit_test(A,B,h,h,seed=13,n_draws=250,
                             burnin=300,swaps=10,min_ess=5)
        self.assertEqual(v["status"],"INFORMATIVE_NONIDENTICAL_TRAP_CANOPY_NULL")
        self.assertTrue(v["source_CHM_may_follow_animal_capture"])
        self.assertEqual(v["null_draws"],250)
        self.assertGreater(v["approx_null_effective_draws"],5)
        self.assertGreater(v["z"],0.)

    def test_no_canopy_variance_is_uninformative_not_negative_ecology(self):
        A,B=pair()
        v=original_unit_test(A,B,{t:0. for t in TRAPS},
                             height_gradient(),seed=1,n_draws=50)
        self.assertEqual(v["status"],"UNINFORMATIVE_ONE_CANOPY_HEIGHT")
        self.assertNotIn("z",v)

    def test_missing_original_trap_coverage_fails_closed(self):
        A,B=pair()
        h=height_gradient()
        h.pop("A10")
        with self.assertRaisesRegex(ValueError,"NOT_ORIGINAL_100_CHM_STATIONS"):
            original_unit_test(A,B,h,height_gradient(),seed=1,n_draws=10)

    def test_36_pairs_and_twelve_physical_sites_signflip_not_pseudoreplicated(self):
        rows=[{"status":"INFORMATIVE_NONIDENTICAL_TRAP_CANOPY_NULL",
               "z":1.} for _ in range(36)]
        groups={f"physical-site-{j}":[1.,1.,1.] for j in range(12)}
        o=summarize_original_sites(rows,groups,source_pairs=36,
                                  source_sites=12,source_plots=21)
        self.assertEqual(o["status"],"EXPLORATORY_CANOPY_AFFINITY_SUPPORTED_CONDITIONAL")
        self.assertEqual(o["original_source_informative_physical_sites"],12)
        self.assertEqual(o["site_level_canopy_ecological_effect"]["physical_sites"],12)
        self.assertEqual(o["source_selected_original_season_pairs"],36)
        self.assertNotIn("physical-site-1",str(o))

    def test_insufficient_sites_never_reports_exploratory_evidence(self):
        rows=[{"status":"INFORMATIVE_NONIDENTICAL_TRAP_CANOPY_NULL",
               "z":1.} for _ in range(30)]+[
               {"status":"UNINFORMATIVE_ZERO_NULL_VARIANCE"} for _ in range(6)]
        groups={"site"+str(i):[1.]*6 for i in range(5)}
        o=summarize_original_sites(rows,groups,source_pairs=36,
                                  source_sites=12,source_plots=21)
        self.assertEqual(o["status"],
            "STOP_CANOPY_AFFINITY_TOO_FEW_INFORMATIVE_SITES_OR_PAIRS")
        self.assertIsNone(o["site_level_canopy_ecological_effect"])

class TestOriginalRESTSourceAudit(unittest.TestCase):
    def test_anonymous_rest_error_is_a_cohort_stop(self):
        source_station=("PRIVATE_SITE","PRIVATE_PLOT","PRIVATE_STATION")
        good_station=("OTHER_PRIVATE_SITE","PRIVATE_PLOT","PRIVATE_STATION")
        rows=[
            (source_station,{"locationHistory":[{"synthetic":True}]},"sha1",None),
            (good_station,None,None,"HTTP_TRANSPORT_RETRIES_EXHAUSTED"),
        ]
        with self.assertRaises(OriginalRESTHistoryStop) as ctx:
            _audit_rest_history_rows(rows,expected=2)
        error=ctx.exception
        self.assertEqual(error.requested,2)
        self.assertEqual(error.valid,1)
        self.assertEqual(error.counts,{"HTTP_TRANSPORT_RETRIES_EXHAUSTED":1})
        self.assertNotIn("PRIVATE_SITE",str(error))
        self.assertNotIn("PRIVATE_SITE",str(error.counts))

    def test_complete_original_rest_source_has_no_selective_replacement(self):
        rows=[
            (("A",1),{"source":"first"},"first_sha",None),
            (("B",2),{"source":"second"},"second_sha",None),
        ]
        documents,source_shas=_audit_rest_history_rows(rows,expected=2)
        self.assertEqual(len(documents),2)
        self.assertEqual(source_shas,["first_sha","second_sha"])
        with self.assertRaises(OriginalRESTHistoryStop) as ctx:
            _audit_rest_history_rows(rows+[rows[0]],expected=3)
        self.assertEqual(ctx.exception.counts,{"DUPLICATE_ORIGINAL_STATION_KEY":1})


if __name__=="__main__":
    unittest.main()
