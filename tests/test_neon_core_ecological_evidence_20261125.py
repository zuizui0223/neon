import json,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]/"results"
def load(name):return json.loads((ROOT/name).read_text())
def exactp(x):return x["rank_comonotone_within_site_exact_marginal_stress"]["one_sided_plus_one_p"]
class CoreLedgerTests(unittest.TestCase):
    def test_13_rows_match_originating_receipts(self):
        l=load("neon_core_ecological_evidence_20261125.json")
        u=load("neon_uniform_null_correction_receipt_20261020.json")
        t=load("neon_exact_two_genus_ecological_receipt_20261025.json")
        n=load("neon_exact_two_new_sites_sensitivity_receipt_20261025.json")
        c=load("neon_macro_six_night_common_station_recurrence_receipt_20261025.json")
        p=load("neon_macro_10m_patch_conditional_20261025.json")
        q=load("neon_observed_rank_reversal_recurrence_20261125.json")["original_stdout_json"]
        def primary(x):return (x["seasonal_pairs"],x["physical_sites"],x["corrected_site_mean_Z"],x["positive_site_means"],x["within_site_comonotone_stress"]["plus_one_p"])
        def meta(x):return (x["seasonal_pairs"],x["sites"],x["observed_equal_site_mean_z"],None,exactp(x))
        def rank(x):return (x["informative_pairs"],x["sites"],x["effect"]["equal_site_mean_Z"],x["effect"]["positive_sites"],exactp(x["effect"]["conditional_null"]))
        tt=t["observed"];nn=n["observed_geographically_nonoverlap_sites"]
        nc=n["whole_site_source_reuse_exclusion"];cc=c["observed"]
        pp=p["observed"];pc=p["site_reused_season_exclusion"];rc=q["strict_rank_reversal_no_reused_season_sites"]
        expect={
            "strict":primary(u["full_14site"]),
            "strict_clean":primary(u["source_disjoint_12site"]),
            "two":(tt["informative_exact_two_genus_pairs"],tt["physical_sites"],tt["corrected_equal_site_mean_Z"],tt["positive_physical_site_mean_count"],exactp(t["full_exact_two_genus_conditional_meta_null"])),
            "two_clean":meta(t["source_disjoint_exact_two_genus_conditional_meta_null"]),
            "two_new":(nn["informative_exact_two_pairs"],nn["physical_sites"],nn["equal_site_mean_z"],nn["positive_site_mean_count"],exactp(n["conditional_new_site_meta_null"])),
            "two_new_clean":(nc["remaining_informative_pairs"],nc["remaining_physical_sites"],None,None,None),
            "common":(cc["informative_seasonal_pairs"],cc["independent_physical_sites"],cc["site_weighted_mean_Z"],cc["positive_site_mean_count"],exactp(c["conditional_meta_exact_two_row_marginal"])),
            "common_clean":meta(c["whole_site_reused_season_sensitivity"]),
            "patch":(pp["informative_source_pairs"],pp["physical_sites"],pp["equal_physical_site_mean_Z_neighbor_given_same_station_overlap"],pp["positive_site_mean_count"],p["conditional_site_meta_null"]["comonotone_within_site_marginal_null"]["one_sided_p"]),
            "patch_clean":(pc["remaining_informative_pairs"],pc["remaining_physical_sites"],pc["conditional_site_meta_null"]["observed_equal_site_weighted_mean_Z"],None,pc["conditional_site_meta_null"]["comonotone_within_site_marginal_null"]["one_sided_p"]),
            "rank_retained":rank(q["retained_rank_context_only"]),
            "rank_reversed":rank(q["strict_rank_reversal"]),
            "rank_reversed_clean":(rc["informative_pairs"],rc["sites"],None,None,None)}
        fields=("informative_pairs","physical_sites","site_equal_mean_Z","positive_sites","conditional_p_rank_coupled")
        self.assertEqual(len(l["recurrence"]),13)
        self.assertEqual({x["id"] for x in l["recurrence"]},set(expect))
        for x in l["recurrence"]:
            self.assertEqual(tuple(x[k] for k in fields),expect[x["id"]],x["id"])
            self.assertTrue((ROOT.parent/x["source_receipt"]).is_file())
        self.assertTrue(l["submission_hold"])
        self.assertEqual(q["status"],"REVERSAL_RECURRENCE_NOT_ESTABLISHED")
if __name__=="__main__":unittest.main()
