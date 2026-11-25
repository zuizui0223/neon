import unittest
from datetime import date
from analysis.audit_neon_seedfall_mammal_breeding_support_v1 import possible_alignment,phase,d
class SeedfallBreedingSupportTests(unittest.TestCase):
    def test_calendar_only_support(self):
        l={("a",2020):{date(2020,9,1),date(2020,10,1)},("a",2021):{date(2021,9,1)}}
        tags={str(i) for i in range(10)}
        b={("a",2021,"sp","spring"):tags,("a",2021,"sp","autumn"):tags}
        q=possible_alignment(l,b)
        self.assertEqual(q["candidate_site_year_taxon_cells"],1)
        self.assertEqual(q["candidate_cells_with_at_least_two_collection_dates_each_autumn"],0)
        self.assertTrue(q["necessary_only_no_complete_litter_interval_or_same_plot_claim"])
        self.assertEqual(possible_alignment({("a",2021):l["a",2021]},b)["candidate_site_years"],0)
    def test_no_guessed_season(self):
        self.assertEqual(phase(date(2022,3,1)),"spring")
        self.assertIsNone(phase(date(2022,8,1)))
        self.assertIsNone(d("2022/03/01"))
if __name__=="__main__":unittest.main()
