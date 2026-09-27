import csv
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/"data"/"derived"/"combine_carrier_traits_v1.csv"

def cliffs(a,b):
    gt=sum(x>y for x in a for y in b)
    lt=sum(x<y for x in a for y in b)
    return (gt-lt)/(len(a)*len(b))

class CombineCarrierTraitTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        with DATA.open(newline="",encoding="utf-8") as fh:
            cls.rows=list(csv.DictReader(fh))

    def test_complete_carrier_set(self):
        self.assertEqual(len(self.rows),32)
        self.assertEqual(len({r["species_name"] for r in self.rows}),32)

    def test_core_traits_complete(self):
        for trait in ("adult_mass_g","dispersal_km","habitat_breadth_n","det_diet_breadth_n","trophic_level"):
            self.assertEqual(sum(bool(r[trait]) for r in self.rows),32)

    def test_density_is_largest_continuous_effect_candidate(self):
        effects={}
        for trait in ("adult_mass_g","dispersal_km","habitat_breadth_n","det_diet_breadth_n","home_range_km2","density_n_km2"):
            a=[float(r[trait]) for r in self.rows if int(r["carrier_site_count"])>=2 and r[trait]]
            b=[float(r[trait]) for r in self.rows if int(r["carrier_site_count"])==1 and r[trait]]
            effects[trait]=abs(cliffs(a,b))
        self.assertEqual(max(effects,key=effects.get),"density_n_km2")
        self.assertAlmostEqual(effects["density_n_km2"],0.3202614379084967)

    def test_generalism_mobility_effects_are_small(self):
        for trait in ("adult_mass_g","dispersal_km","habitat_breadth_n","det_diet_breadth_n","home_range_km2"):
            a=[float(r[trait]) for r in self.rows if int(r["carrier_site_count"])>=2 and r[trait]]
            b=[float(r[trait]) for r in self.rows if int(r["carrier_site_count"])==1 and r[trait]]
            self.assertLess(abs(cliffs(a,b)),0.15)

if __name__=="__main__":
    unittest.main()
