import unittest
from analysis.inventory_wisconsin_footprint_validation_v1 import event_inventory

class TestWisconsinInventory(unittest.TestCase):
    def test_wide_recaptures_reconstruct_support_only(self):
        rows=[{
            "Season":"Summer 2021","Site":"HW1","Session":"1","Species":"PELE",
            "Capture Date":"08/01/2021","Trap ID":"A1","Remove":"0",
            "Recap Date 1":"08/02/2021","Recap Trap 1":"A2",
            "Recap Date 2":"08/03/2021","Recap Trap 2":"A2",
        },{
            "Season":"Summer 2021","Site":"HW1","Session":"1","Species":"MYGA",
            "Capture Date":"08/01/2021","Trap ID":"B1","Remove":"0",
            "Recap Date 1":"","Recap Trap 1":"",
            "Recap Date 2":"","Recap Trap 2":"",
        }]
        out=event_inventory(rows)
        self.assertEqual(out["reconstructed_capture_events"],4)
        self.assertEqual(out["species_multi_night_individuals"]["PELE"],1)
        self.assertNotIn("MYGA",out["species_multi_night_individuals"])
        self.assertEqual(out["unit_support"][0]["species_with_multi_night_individuals"],1)

if __name__=="__main__":
    unittest.main()
