from pathlib import Path
import subprocess
import unittest

ROOT=Path(__file__).resolve().parents[1]
GEN=ROOT/'manuscript'/'neon_metacommunity_redundancy'/'generated'
MANUSCRIPT=ROOT/'manuscript'/'neon_metacommunity_redundancy'/'MANUSCRIPT_V6_MECHANISM_VALIDATED_DRAFT.md'


class V6TerminologyAndFigureLayoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        subprocess.run(['python','analysis/build_paper_assets.py'],cwd=ROOT,check=True)
        subprocess.run(['python','analysis/build_carrier_turnover_figure_v1.py'],cwd=ROOT,check=True)

    def test_manuscript_uses_local_cohesion_for_active_metric(self):
        text=MANUSCRIPT.read_text(encoding='utf-8')
        self.assertNotIn('`taxonProtocolCategory = target`',text)
        self.assertIn('### 2.4 Local spatial-cohesion fraction',text)
        self.assertIn('### 3.1 Pooling never created additional local spatial cohesion',text)
        self.assertIn('### 3.4 Local spatial cohesion was redundant across species',text)
        self.assertNotIn('**Figure 2. Pooled-community versus best-species continuity fractions',text)
        self.assertNotIn('**Figure 3. Two-scale organization of spatial continuity.',text)

    def test_legacy_figures_use_local_cohesion_terminology(self):
        f1=(GEN/'figure_1_conceptual_outcomes.svg').read_text(encoding='utf-8')
        f2=(GEN/'figure_2_community_vs_species.svg').read_text(encoding='utf-8')
        f4=(GEN/'figure_4_ornl_weakest_link.svg').read_text(encoding='utf-8')
        self.assertIn('local spatial cohesion',f1)
        self.assertNotIn('spatial continuity',f1)
        self.assertIn('Pooling species never increased local spatial cohesion',f2)
        self.assertNotIn('spatial continuity',f2)
        self.assertIn('ORNL: pooling taxa reduced local spatial cohesion',f4)
        self.assertNotIn('spatial continuity',f4)

    def test_carrier_turnover_figure_reserves_annotation_space(self):
        f3=(GEN/'figure_3_two_scale_redundancy.svg').read_text(encoding='utf-8')
        self.assertIn('height="720"',f3)
        self.assertIn('turnover in local-cohesion carriers',f3)
        self.assertNotIn('turnover in continuity carriers',f3)


if __name__=='__main__':
    unittest.main()
