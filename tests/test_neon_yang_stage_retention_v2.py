import unittest
from analysis.run_neon_yang_stage_retention_v2 import structure,treatment,summarize,DESIGN
class YangV2Tests(unittest.TestCase):
    def synthetic(self):
        rows=[]
        for g,(spp,years,patches) in DESIGN.items():
            for y in years:
                for p in patches:
                    # Preserve shared physical labels but deliberately reuse
                    # station indices across disjoint pairs.
                    for k in range(6):
                        for sp in spp:
                            rows.extend([[y,p,str(k),"mixed",sp,0,0,0]]*20)
                    for sp in spp:
                        for k in range(3):
                            # within pair monostation names distinct from mixed
                            rows.extend([[y,p,sp+str(k),"monspecific",sp,0,0,0]]*40)
        return rows
    def test_exact_structure_with_shared_patch_station_label(self):
        rows=self.synthetic()
        a,b,d=structure(rows)
        self.assertEqual(len(a),540)
        self.assertEqual(d["pair_patch_year_blocks"],45)
        self.assertTrue(d["literal_table1_patch_roster_match"])
        self.assertEqual(treatment("monspecific"),"mono")
        rows.pop()
        with self.assertRaises(ValueError):structure(rows)
    def test_source_label_variant_does_not_infer_physical_identity(self):
        rows=self.synthetic()
        for row in rows:
            if row[0]==2015 and row[1]=="F":row[1]="F_ARCHIVE"
        _,_,d=structure(rows)
        self.assertFalse(d["literal_table1_patch_roster_match"])
    def test_unchanged_edge_summary(self):
        a,by,d=structure(self.synthetic());b={}
        for (g,y),ps in by.items():
            for p in ps:
                for sp in DESIGN[g][0]:
                    b[g,y,p,sp]={"mixed":{"released":120,"removed":80,"removed_NA":0,"cache":40,"cache_NA":0,"winter":2,"winter_NA":0},
                                  "mono":{"released":120,"removed":60,"removed_NA":0,"cache":20,"cache_NA":0,"winter":5,"winter_NA":0}}
        v=summarize(b,by)
        self.assertEqual(v["classification_counts"],{"REVERSED":12})
        self.assertEqual(v["strict_reversal_edges"],10)
if __name__=="__main__":unittest.main()
