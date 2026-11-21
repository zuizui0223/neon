"""Synthetic source-only plant 1m2 plot and season matches."""
import unittest
from datetime import date
from analysis.neon_field_plant_source_support_v1 import (
 parse_1m2_source,plant_source_events,summarize_nearby_plant_bouts
)
class PlantSourceTests(unittest.TestCase):
 def test_1m2_validity_vs_absence(self):
    raw=("plotID,endDate,eventID,divDataType,percentCover,samplingImpractical\n"
         "AAAA_001,2022-06-01T00:00:00Z,e1,plantSpecies,14,OK\n"
         "AAAA_001,2022-06-01,e1,otherVariables,,OK\n"
         "AAAA_002,2022-10-01,e2,plantSpecies,20,not sampled\n").encode()
    rows,n=parse_1m2_source(raw)
    self.assertEqual(n,3);self.assertTrue(rows[0][3]);self.assertFalse(rows[1][3]);self.assertFalse(rows[2][3])
 def test_shared_ID_distinct_visits_are_not_trap_habitat(self):
    A=(date(2022,6,3),date(2022,6,4),date(2022,6,5))
    B=(date(2022,10,3),date(2022,10,4),date(2022,10,5))
    u={"site":"AAAA","site_plot":("AAAA","AAAA_001"),"capture_dates_A":A,"capture_dates_B":B}
    sources=[("AAAA",[("AAAA_001",date(2022,6,1),"e1",True,"plantSpecies"),("AAAA_001",date(2022,10,1),"e2",True,"plantSpecies"),("AAAA_002",date(2022,6,1),"e3",True,"plantSpecies")],3)]
    byplot,c=plant_source_events(sources,{("AAAA","AAAA_001")})
    self.assertEqual(c["rows_at_shared_plotID"],2)
    report=summarize_nearby_plant_bouts([u],byplot,expected_pairs=1,expected_plots=1,expected_sites=1)
    self.assertEqual(report["source_period_support_counts"]["numeric_365_distinct"],1)
    self.assertFalse(report["nearby_base_plot_numeric_cover_source_GO"])
    self.assertTrue(report["same_plotID_not_same_100_trap_locations"])
 def test_single_plant_event_cannot_be_two_distinct_annual_visits(self):
    A=(date(2022,6,3),date(2022,6,4),date(2022,6,5))
    B=(date(2022,10,3),date(2022,10,4),date(2022,10,5))
    u={"site":"AAAA","site_plot":("AAAA","AAAA_001"),"capture_dates_A":A,"capture_dates_B":B}
    byplot={("AAAA","AAAA_001"):{(date(2022,8,1),"e1"):True}}
    r=summarize_nearby_plant_bouts([u],byplot,expected_pairs=1,expected_plots=1,expected_sites=1)
    self.assertEqual(r["source_period_support_counts"]["numeric_365_both"],1)
    self.assertEqual(r["source_period_support_counts"]["numeric_365_distinct"],0)
 def test_missing_plot_never_imputed(self):
    A=(date(2022,6,3),date(2022,6,4),date(2022,6,5))
    B=(date(2022,10,3),date(2022,10,4),date(2022,10,5))
    u={"site":"AAAA","site_plot":("AAAA","AAAA_001"),"capture_dates_A":A,"capture_dates_B":B}
    r=summarize_nearby_plant_bouts([u],{},expected_pairs=1,expected_plots=1,expected_sites=1)
    self.assertEqual(r["source_period_support_counts"]["numeric_365_distinct"],0)
    self.assertEqual(r["plots_with_exact_ID_matched_base_plant_survey"],0)
if __name__=="__main__":unittest.main()
