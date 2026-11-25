import unittest
from hashlib import md5
from io import BytesIO
from zipfile import ZipFile
from analysis.audit_neon_cambodia_independent_source_v1 import verify,tabular,archive
class CambodiaSourceTests(unittest.TestCase):
    def test_provider_checksum(self):
        b=b"site,trap\nx,1\n"
        self.assertEqual(verify(b,len(b),"md5:"+md5(b).hexdigest())["bytes"],len(b))
        with self.assertRaises(ValueError):verify(b,len(b),"md5:"+"0"*32)
    def test_only_schema(self):
        x=tabular("capture.csv",b"site,tag,trap\nprivate,123,1\n")
        self.assertEqual(x["nonblank_data_rows"],1);self.assertNotIn("private",str(x))
    def test_archive_no_escape(self):
        b=BytesIO()
        with ZipFile(b,"w") as z:z.writestr("../bad.csv","a,b\n1,2")
        with self.assertRaises(ValueError):archive(b.getvalue())
if __name__=="__main__":unittest.main()
