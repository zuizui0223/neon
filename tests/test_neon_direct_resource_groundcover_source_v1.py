import json
import unittest
from hashlib import md5
from analysis.audit_neon_direct_resource_groundcover_source_v1 import audit_one, inventory, schema

class SourceInventoryTests(unittest.TestCase):
    def fixture(self,raw=b"animal_id,year,station\na,2020,1\n"):
        f={"id":10,"name":"captures.csv","size":len(raw),"computed_md5":md5(raw).hexdigest(),"download_url":"https://ndownloader.figshare.com/files/10"}
        return {"id":15029247,"title":"Pulsed resources and test","doi":"10.6084/m9.figshare.15029247.v1","version":1,"files":[f]},raw

    def test_checksums_and_header_only(self):
        meta,raw=self.fixture()
        out=audit_one(15029247,lambda u,n:json.dumps(meta).encode() if "api.figshare" in u else raw)
        self.assertEqual(out["status"],"CHECKSUM_SOURCE_GO_SCHEMA_ONLY")
        self.assertEqual(out["schema_receipts"][0]["headers"],["animal_id","year","station"])
        self.assertNotIn("2020",str(out))

    def test_corrupt_file_and_version_fail_closed(self):
        meta,raw=self.fixture()
        out=audit_one(15029247,lambda u,n:json.dumps(meta).encode() if "api.figshare" in u else b"x"*len(raw))
        self.assertEqual(out["status"],"STOP_INCOMPLETE_ORIGINAL_BYTES")
        meta["version"]=None
        with self.assertRaises(ValueError):
            inventory(meta,15029247)

    def test_headerless_numeric_not_exported(self):
        s=schema(b"1234,2020,88\n12,2021,0\n","a.csv")
        self.assertNotIn("headers",s)
        self.assertEqual(s["schema_status"],"HEADER_NOT_CONFIDENT_NO_VALUES_EXPORTED")

    def test_duplicate_file_rejected(self):
        meta,raw=self.fixture()
        meta["files"].append(dict(meta["files"][0]))
        with self.assertRaises(ValueError):
            inventory(meta,15029247)

    def test_missing_md5_no_partial_fetch(self):
        meta,raw=self.fixture()
        meta["files"][0].pop("computed_md5")
        called=[]
        def fetch(u,n):
            called.append(u)
            return json.dumps(meta).encode()
        out=audit_one(15029247,fetch)
        self.assertEqual(out["status"],"STOP_NO_COMPLETE_BOUNDED_CHECKSUM_SOURCE")
        self.assertEqual(len(called),1)

if __name__=="__main__":
    unittest.main()
