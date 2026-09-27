from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
SCRIPT=ROOT/"analysis"/"build_carrier_mechanism_figure_v1.py"
FIG=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"generated"/"figure_5_fresh_mechanism.svg"
SITE=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"generated"/"table_s4_fresh_mechanism_sites.csv"
SPECIES=ROOT/"manuscript"/"neon_metacommunity_redundancy"/"generated"/"table_s5_fresh_species_mechanism.csv"


class CarrierMechanismFigureTests(unittest.TestCase):
    def test_builder_creates_figure_and_tables_with_frozen_findings(self):
        subprocess.run(["python",str(SCRIPT)],cwd=ROOT,check=True)
        self.assertTrue(FIG.exists())
        self.assertTrue(SITE.exists())
        self.assertTrue(SPECIES.exists())

        svg=FIG.read_text(encoding="utf-8")
        self.assertIn("Fresh validation: grid-scale allocation determines the local cohesion state",svg)
        self.assertIn("between-grid allocation",svg)
        self.assertIn("within-grid organization",svg)
        self.assertIn("10/15 repeated species switch",svg)
        self.assertIn("66/68",svg)

        site_lines=SITE.read_text(encoding="utf-8").strip().splitlines()
        species_lines=SPECIES.read_text(encoding="utf-8").strip().splitlines()
        self.assertEqual(len(site_lines),12)   # header + 11 sites
        self.assertEqual(len(species_lines),69)  # header + 68 species x site records


if __name__=="__main__":
    unittest.main()
