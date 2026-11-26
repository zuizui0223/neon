"""Synthetic-only checks of the unmodified V25 fit and the offline input gate.
No empirical records are included; no real-data results inferred.
"""
import copy,hashlib,io,math,pathlib,tempfile,unittest,zipfile
from analysis.run_neon_joyce_early_late_v25 import analyze,fit_score,FILES,SPECIES
from analysis.run_neon_joyce_local_v25 import parse_verified,run,MANIFEST

def fixture():
    strata=[(s,t) for s in sorted(SPECIES) for t in ("Restored","Remnant")]
    groups=[("S"+str(i+1),strata[(i+j)%8],i%3) for i in range(8) for j in range(5)]
    groups += [("HB",s,2) for s in strata[:4]]
    assert len(groups)==44
    # Synthetic N values, deliberately independent of unknown real species allocation.
    ns=[11]*8+[7]*16+[8]*20
    assert sum(ns)==360
    e=[];l=[]
    def add(g,n,retained):
        site,(sp,hab),k=g
        for station in range(1,5):
            for arm in ("caged","exposed"):
                base={"site":site,"species":sp,"trt":hab,"station":str(station),"exclosure":arm,"seeds_total":str(n)}
                early=n-1-(2*k if arm=="exposed" else 0)
                late=n-3-(k if arm=="exposed" else 0)
                assert 0<=late<=early<=n
                e.append({**base,"seeds_remaining":str(early),"seeds_missing":str(n-early)})
                if retained:l.append({**base,"seeds_established":str(late),"seeds_failed":str(n-late)})
    for g,n in zip(groups,ns):add(g,n,True)
    add(("HB",strata[4],1),7,False);add(("HB",strata[5],1),11,False)
    assert (len(e),len(l))==(368,352)
    assert sum(int(r["seeds_total"]) for r in e)==3024
    assert sum(int(r["seeds_total"]) for r in l)==2880
    return {FILES[0]:e,FILES[1]:l}

def recs(late_fn):
    return [{"site":str(i),"stratum":s,"early":e,"late":late_fn(s,e)}
            for i,e in enumerate([-.4,-.3,-.2,-.1,.1,.2,.3,.4])
            for s in ("A","B")]

class V25Tests(unittest.TestCase):
    def test_full_synthetic_pipeline_recovers_half_transmission(self):
        out={}
        analyze(fixture(),out)
        self.assertEqual(out["status"],"DESCRIPTIVE_PREDICTION_COMPLETE")
        self.assertEqual(out["support"]["matched_site_species_habitat_units"],44)
        self.assertEqual(out["support"]["physical_sites"],9)
        self.assertEqual(out["support"]["missing_final_rows"],16)
        p=out["prediction"]
        self.assertTrue(p["meets_descriptive_gate"])
        self.assertLess(p["site_equal_RMSE"]["early_augmented_mse"],1e-12)
        self.assertTrue(all(abs(x["train_slope"]-.5)<1e-12 for x in p["site_scores"]))
    def test_heldout_response_does_not_change_its_training_slope(self):
        d=recs(lambda s,e:(.1 if s=="A" else -.05)+.5*e)
        a=fit_score(d,False)
        d2=copy.deepcopy(d)
        for r in d2:
            if r["site"]=="0":r["late"]=.9
        b=fit_score(d2,False)
        self.assertAlmostEqual(a["site_scores"][0]["train_slope"],b["site_scores"][0]["train_slope"],places=14)
        self.assertNotEqual(a["site_scores"][0]["early_augmented_mse"],b["site_scores"][0]["early_augmented_mse"])
    def test_no_early_signal_fails_descriptive_gate(self):
        d=recs(lambda s,e:.25 if s=="A" else -.25)
        self.assertFalse(fit_score(d,False)["meets_descriptive_gate"])
    def test_unchanged_transmission_not_beaten(self):
        d=recs(lambda s,e:e)
        self.assertFalse(fit_score(d,False)["meets_descriptive_gate"])
    def test_constant_early_variation_stops(self):
        d=recs(lambda s,e:.25)
        for r in d:r["early"]=0.
        with self.assertRaisesRegex(ValueError,"no residual early variation"):fit_score(d,False)
    def test_unsupported_stratum_stops(self):
        d=recs(lambda s,e:.5*e)
        d=[r for r in d if r["stratum"]=="A" or r["site"]=="0"]
        with self.assertRaisesRegex(ValueError,"training stratum not supported"):fit_score(d,False)
    def test_duplicate_quadrat_rejected(self):
        d=fixture();d[FILES[0]][1]=copy.deepcopy(d[FILES[0]][0])
        with self.assertRaisesRegex(ValueError,"count partition or key duplication"):analyze(d,{})
    def test_invalid_fate_partition_rejected(self):
        d=fixture();d[FILES[1]][0]["seeds_failed"]="999"
        with self.assertRaisesRegex(ValueError,"count partition or key duplication"):analyze(d,{})
    def test_unexpected_final_deletion_rejected(self):
        d=fixture()
        # Swap a whole synthetic retained group with a lost group of the same
        # input denominator, preserving every count and the published totals.
        old=d[FILES[1]][0]
        k=(old["site"],old["species"],old["trt"])
        for r in d[FILES[1]]:
            if (r["site"],r["species"],r["trt"])==k:
                r["site"]="UNMATCHED"
        with self.assertRaisesRegex(ValueError,"final not subset of early"):analyze(d,{})
    def test_verified_csv_parser_and_hash_rejection(self):
        b=b"site,count\nA,1\n";expected=(len(b),hashlib.sha256(b).hexdigest())
        self.assertEqual(parse_verified(b,"synthetic.csv",expected),[{"site":"A","count":"1"}])
        with self.assertRaisesRegex(ValueError,"SHA256 mismatch"):parse_verified(b.replace(b"1",b"2"),"synthetic.csv",expected)
    def test_offline_fake_data_not_admitted(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"fake.zip"
            with zipfile.ZipFile(p,"w") as z:
                for name,(n,_) in MANIFEST.items():z.writestr(name,b"x"*n)
            r=run(p)
            self.assertFalse(r["outcome_opened"])
            self.assertEqual(r["status"],"STOP_LOCAL_INPUT_OR_SUPPORT")
            self.assertIn("SHA256 mismatch",r["reason"])
    def test_zip_duplicate_member_rejected_without_extraction(self):
        with tempfile.TemporaryDirectory() as td:
            p=pathlib.Path(td)/"ambiguous.zip"
            with zipfile.ZipFile(p,"w") as z:
                z.writestr("a/"+FILES[0],b"x");z.writestr("b/"+FILES[0],b"x")
            r=run(p)
            self.assertFalse(r["outcome_opened"])
            self.assertIn("absent or duplicated",r["reason"])

if __name__=="__main__":unittest.main()
