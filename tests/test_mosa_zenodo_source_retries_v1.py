import unittest
from unittest.mock import patch
from urllib.error import HTTPError
from analysis.audit_mosa_zenodo_source_schema_v1 import _get

class FakeResponse:
    def __init__(self,body=b"verified"):
        self.body=body
    def __enter__(self):
        return self
    def __exit__(self,*args):
        return False
    def read(self):
        return self.body

class ZenodoTransportRetryTests(unittest.TestCase):
    @patch("analysis.audit_mosa_zenodo_source_schema_v1.time.sleep")
    @patch("analysis.audit_mosa_zenodo_source_schema_v1.urllib.request.urlopen")
    def test_504_then_success_retry(self, open_mock, sleep):
        url="https://zenodo.org/api/records/10049811"
        open_mock.side_effect=[
            HTTPError(url,504,"Gateway Timeout",None,None),
            FakeResponse()
        ]
        self.assertEqual(_get(url),b"verified")
        self.assertEqual(open_mock.call_count,2)
        self.assertEqual(sleep.call_count,1)

    @patch("analysis.audit_mosa_zenodo_source_schema_v1.time.sleep")
    @patch("analysis.audit_mosa_zenodo_source_schema_v1.urllib.request.urlopen")
    def test_no_retry_401(self, open_mock,sleep):
        url="https://zenodo.org/api/records/10049811"
        open_mock.side_effect=HTTPError(url,401,"Unauthorized",None,None)
        with self.assertRaises(HTTPError):
            _get(url)
        self.assertEqual(open_mock.call_count,1)
        self.assertEqual(sleep.call_count,0)

    @patch("analysis.audit_mosa_zenodo_source_schema_v1.time.sleep")
    @patch("analysis.audit_mosa_zenodo_source_schema_v1.urllib.request.urlopen")
    def test_persistent_504_fails_closed(self,open_mock,sleep):
        url="https://zenodo.org/api/records/10049811"
        open_mock.side_effect=HTTPError(url,504,"Gateway Timeout",None,None)
        with self.assertRaises(HTTPError):
            _get(url)
        self.assertEqual(open_mock.call_count,3)
        self.assertEqual(sleep.call_count,2)

if __name__=="__main__":
    unittest.main()
