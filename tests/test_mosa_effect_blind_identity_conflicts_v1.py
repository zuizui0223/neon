import unittest
from analysis.audit_mosa_effect_blind_identity_conflicts_v1 import audit_identity_conflicts

F=["TOE","SPECIES","DATE","X","Y","GRID","SEX"]
def row(tag,day,x="3",y="B",sex="M",sp="MN"):
    return dict(TOE=tag,SPECIES=sp,DATE=day,X=x,Y=y,GRID="MOSA",SEX=sex)
class Tests(unittest.TestCase):
    def test_duplicate_logging_not_distinct_stations(self):
        rows=[row("a","13/07/2000"),row("a","13/07/2000"),row("a","14/07/2000")]
        r=audit_identity_conflicts(rows,F,{"a"},set(),{"2000-07"})
        self.assertEqual(r["same_day_duplicate_same_station_keys"],1)
        self.assertEqual(r["same_day_multiple_station_keys"],0)
        self.assertEqual(r["months_with_repeat_supported_suspect_codes"],0)
    def test_conflicting_station_on_repeat_tag_affects_month(self):
        rows=[row("a","13/07/2000"),row("a","13/07/2000","4"),row("a","14/07/2000")]
        r=audit_identity_conflicts(rows,F,{"a"},set(),{"2000-07"})
        self.assertEqual(r["same_day_multiple_station_keys"],1)
        self.assertEqual(r["months_with_repeat_supported_suspect_codes"],1)
        self.assertFalse(r["ecological_effects_opened"])
    def test_excluded_collision_cannot_count(self):
        rows=[row("a","13/07/2000"),row("a","13/07/2000","4")]
        r=audit_identity_conflicts(rows,F,{"a"},{"a"},{"2000-07"})
        self.assertEqual(r["same_day_multiple_station_keys"],0)
    def test_cross_species_not_relabelled(self):
        rows=[row("a","13/07/2000"),row("a","14/07/2000"),row("a","15/07/2000",sp="TA")]
        r=audit_identity_conflicts(rows,F,{"a"},set(),{"2000-07"})
        self.assertEqual(r["cross_species_code_count"],1)
        self.assertEqual(r["months_with_repeat_supported_suspect_codes"],1)
if __name__=="__main__":unittest.main()
