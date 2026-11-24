import unittest
from analysis.run_neon_xiao_seed_stage_v1 import coarse_bounds,note_confirms_binary,species,binary,analyze
class XiaoStageTests(unittest.TestCase):
    def test_bounds_and_attenuation(self):
        m={"released":540,"cache":30,"intact":25,"damage":5,"embryo_unknown":0}
        x={"released":270,"cache":40,"intact":20,"damage":20,"embryo_unknown":0}
        o=coarse_bounds(m,x)
        self.assertAlmostEqual(o["cache"]["conservative_bounds"][0],40/270-48/540)
        self.assertEqual(o["attenuation"],o["damage"])
    def test_literal_guard(self):
        self.assertTrue(note_confirms_binary(["1 = yes; 0 = no"]))
        self.assertFalse(note_confirms_binary(["binary data"]))
        self.assertEqual(species("Q. variabilis"),"oak")
        self.assertIsNone(species("1"))
        self.assertIsNone(binary("NA"))
        self.assertEqual(analyze([],["binary data"])["status"],"STOP_BINARY_CODE_NOT_EXPLICITLY_DOCUMENTED")
if __name__=="__main__":unittest.main()
