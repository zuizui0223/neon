import unittest,json
from fractions import Fraction
from analysis.audit_neon_seed_fate_stage_ontology_v2 import primary_identity,heading,AUTHOR_CITED
from analysis.neon_seed_stage_attenuation_bounds_v1 import metrics,paired,summarize

class SourceIdentityTests(unittest.TestCase):
    def test_exact_author_filename_not_keyword_guess(self):
        obj={"id":3189775,"title":AUTHOR_CITED,"version":1,"doi":"10.6084/m9.figshare.3189775.v1",
             "files":[{"id":4,"name":AUTHOR_CITED,"size":10,"computed_md5":"a"*32,"download_url":"https://ndownloader.figshare.com/files/4"}]}
        _,f=primary_identity(json.dumps(obj).encode())
        self.assertEqual(f["id"],4)
        obj["files"][0]["name"]="other.xls"
        with self.assertRaises(ValueError):primary_identity(json.dumps(obj).encode())
    def test_numeric_value_not_header(self):
        self.assertEqual(heading(2),"<nonheader-value>")
        self.assertEqual(heading("seed fate"),"seed fate")

class StageBoundsTests(unittest.TestCase):
    def c(self,i,d,n,u,e=0):return dict(intact=i,damaged=d,noncache=n,unknown=u,cache_embryo_unknown=e)
    def test_exhaustive_categories(self):
        with self.assertRaises(ValueError):metrics(30,self.c(1,1,1,1))
    def test_coupled_attenuation_bound(self):
        m=self.c(6,12,10,2);s=self.c(8,2,45,5)
        x=paired(m,s)
        self.assertEqual(x["attenuation_difference_bounds"],(Fraction(17,60),Fraction(13,30)))
        self.assertEqual(x["cache_known_difference"]-x["intact_known_difference"],x["damage_known_difference"])
        self.assertEqual(summarize([[(m,s)]*3]*3)["status"],"DESCRIPTIVE_CACHE_GAIN_AND_ATTENUATION_ROBUST_TO_UNKNOWN_FATE")
    def test_unknown_fate_can_remove_support(self):
        m=self.c(6,4,10,10);s=self.c(8,2,25,25)
        self.assertEqual(summarize([[(m,s)]*3]*3)["status"],"ROBUST_ATTENUATION_NOT_ESTABLISHED")
        with self.assertRaises(ValueError):summarize([[(m,s)]*3]*2)
if __name__=="__main__":unittest.main()
