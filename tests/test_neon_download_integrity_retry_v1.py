"""Strict NEON inventory-byte integrity under intermittent transport errors."""
import hashlib
import http.client
import unittest
from unittest.mock import patch

from analysis.run_multiscale_density_estimability_release2026_v3 import _download_one


class Response:
    def __init__(self, data=None, exc=None):
        self.data, self.exc = data, exc

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def read(self):
        if self.exc:
            raise self.exc
        return self.data


class DownloadRetryTests(unittest.TestCase):
    def row(self, data=b"stable-scientific-data"):
        return {"url": "https://example.test/data.csv",
                "name": "fake-data.csv",
                "size": len(data),
                "md5": hashlib.md5(data).hexdigest()}

    @patch("analysis.run_multiscale_density_estimability_release2026_v3.time.sleep")
    @patch("analysis.run_multiscale_density_estimability_release2026_v3.urllib.request.urlopen")
    def test_transient_truncation_retries(self, open_mock, sleep_mock):
        b = b"stable-scientific-data"
        open_mock.side_effect = [
            Response(exc=http.client.IncompleteRead(b[:4], 17)),
            Response(data=b)
        ]
        self.assertEqual(_download_one(self.row(b), "test-token"), b)
        self.assertEqual(open_mock.call_count, 2)
        self.assertEqual(sleep_mock.call_count, 1)

    @patch("analysis.run_multiscale_density_estimability_release2026_v3.time.sleep")
    @patch("analysis.run_multiscale_density_estimability_release2026_v3.urllib.request.urlopen")
    def test_persistent_truncation_fails_closed(self, open_mock, sleep_mock):
        open_mock.side_effect = [
            Response(exc=http.client.IncompleteRead(b"x", 10))
            for _ in range(3)
        ]
        with self.assertRaises(http.client.IncompleteRead):
            _download_one(self.row(), "test-token")
        self.assertEqual(open_mock.call_count, 3)
        self.assertEqual(sleep_mock.call_count, 2)

    @patch("analysis.run_multiscale_density_estimability_release2026_v3.urllib.request.urlopen")
    def test_checksum_mismatch_never_accepted_or_retried(self, open_mock):
        b = b"stable-scientific-data"
        open_mock.return_value = Response(data=b"X" + b[1:])
        with self.assertRaisesRegex(RuntimeError, "md5 mismatch"):
            _download_one(self.row(b), "test-token")
        self.assertEqual(open_mock.call_count, 1)

    @patch("analysis.run_multiscale_density_estimability_release2026_v3.urllib.request.urlopen")
    def test_length_mismatch_never_accepted(self, open_mock):
        open_mock.return_value = Response(data=b"short")
        with self.assertRaisesRegex(RuntimeError, "size mismatch"):
            _download_one(self.row(), "test-token")
        self.assertEqual(open_mock.call_count, 1)


if __name__ == "__main__":
    unittest.main()
