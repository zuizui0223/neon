import unittest

from analysis.inventory_wisconsin_footprint_replication_v1 import inventory


class TestWisconsinFootprintFeasibility(unittest.TestCase):
    def test_support_counts_without_overlap_outcomes(self):
        columns = [
            "Season","Site","Session","Capture Date","Trap ID","Species","Remove",
            *[f"Recap Date {k}" for k in range(1,9)],
            *[f"Recap Trap {k}" for k in range(1,9)],
            "Ear Tag L","Ear Tag R",
        ]
        rows=[]
        for sp in ("AA","BB","CC"):
            for i in range(3):
                row={c:"" for c in columns}
                row.update({
                    "Season":"Summer 2020","Site":"S1","Session":"1",
                    "Capture Date":"08/01/2020","Trap ID":f"T{i+1}",
                    "Species":sp,"Remove":"0",
                    "Recap Date 1":"08/02/2020","Recap Trap 1":f"T{i+2}",
                    "Ear Tag L":f"{sp}{i}","Ear Tag R":"",
                })
                rows.append(row)
        out=inventory(rows,columns)
        self.assertEqual(out["candidate_eligible_site_season_count"],1)
        self.assertEqual(out["site_seasons"][0]["support_eligible_species_count"],3)
        self.assertFalse(out["claim_boundary"]["jaccard_opened"])
        self.assertFalse(out["claim_boundary"]["conspecific_heterospecific_overlap_opened"])


if __name__=="__main__":
    unittest.main()
