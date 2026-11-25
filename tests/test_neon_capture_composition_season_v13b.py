import csv,io,unittest
from unittest.mock import patch
from analysis.run_neon_capture_composition_season_v13b import sample,prob,distance,predict,site_result,focal_result
from analysis.neon_macro_6night_operable_trap_status_v1 import published_trap_status
class TestComposition(unittest.TestCase):
    def test_operable_codes(self):
        for v in ('4 - more than 1 capture in one trap','5 - capture','6 - trap set and empty','6'):
            self.assertTrue(published_trap_status(v)[1])
        for v in ('1 - trap not set','2 - disturbed','3 - door open with spoor','6 - not set',''):
            self.assertFalse(published_trap_status(v)[1])
    def test_tv(self):
        self.assertAlmostEqual(distance({'A':.8,'B':.2},{'A':.5,'B':.5}),.3)
        self.assertAlmostEqual(sum(predict({'A':.8,'B':.2},{'A':.4,'B':-.4}).values()),1)
    def test_heldout(self):
        def row(y):return {'year':y,'counts':{'early':{'A':8,'B':2},'late':{'A':5,'B':5}}}
        x=site_result([row(2017),row(2021),row(2022)])
        self.assertAlmostEqual(x['baseline_TV'],.3)
        self.assertAlmostEqual(x['forecast_TV'],0)
    def test_complete_empty_traps_and_conflict_exclusion(self):
        p=[];c=[]
        for month in (5,8):
            for n in range(1,4):
                night=f'{month}_{n}'
                day=f'2021-{month:02d}-{n:02d}'
                p.append(dict(siteID='TEST',plotID='p',nightuid=night,eventID=str(month),collectDate=day,gridCompletion='setting complete, processing complete'))
                for i in range(100):
                    base=dict(siteID='TEST',plotID='p',nightuid=night,collectDate=day,trapCoordinate=chr(65+i//10)+str(i%10+1),tagID='',taxonID='',replacedTag='')
                    if i<20 and n==1:base.update(trapStatus='5 - capture',tagID=f't{i}',taxonID='a' if i<10 else 'b')
                    else:base.update(trapStatus='6 - trap set and empty')
                    c.append(base)
        files=[{'site':'TEST','table':'mam_perplotnight'},{'site':'TEST','table':'mam_pertrapnight'}]
        with patch('analysis.run_neon_capture_composition_season_v13b.batch',return_value=iter(zip(files,[p,c]))),patch('analysis.run_neon_capture_composition_season_v13b.rows',side_effect=lambda x:([],iter(x))):
            out,issues=sample(files,'',{'a':'A','b':'B'})
        self.assertEqual(len(out['TEST']),1)
        self.assertEqual(issues['paired_plots_common90'],1)
        self.assertEqual(out['TEST'][0]['counts']['early'],{'A':10,'B':10})
        # Add contradictory records to 11 stations: 89 shared, no eligible pair.
        c.extend(dict(x,trapStatus='2 - disturbed') for x in c[:11])
        with patch('analysis.run_neon_capture_composition_season_v13b.batch',return_value=iter(zip(files,[p,c]))),patch('analysis.run_neon_capture_composition_season_v13b.rows',side_effect=lambda x:([],iter(x))):
            out,issues=sample(files,'',{'a':'A','b':'B'})
        self.assertEqual(len(out['TEST']),0)
        self.assertEqual(issues.get('paired_plots_common90',0),0)
if __name__=='__main__':unittest.main()
