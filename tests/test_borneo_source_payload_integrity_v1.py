"""Tests for strict scientific-file integrity, including HTML masquerading as CSV."""
import csv
import hashlib
import unittest

from analysis.diagnose_borneo_multiscale_density_schema_v1 import (
    _validate_publication_file, _csv_diagnostic, SourcePayloadError,
)

def meta(raw):
    return {"size": len(raw), "digest": hashlib.md5(raw).hexdigest(), "digestType": "md5"}


class DryadSourceValidationTests(unittest.TestCase):
    def test_valid_capture_csv(self):
        raw=b"individual,night,trap,species\na,1,AA1,X\nb,2,AA1,X\nc,3,AA2,Y\n"
        _validate_publication_file("Chapman_capturehistories.csv",raw,meta(raw))
        self.assertEqual(_csv_diagnostic(raw)["row_count"],3)

    def test_reject_cloud_challenge_even_if_size_and_digest_match(self):
        html=(b'<!doctype html><html lang="en"><head>'
              b'<title>Validating...</title></head><body>Access denied</body></html>')
        with self.assertRaisesRegex(SourcePayloadError,"HTML"):
            _validate_publication_file("Chapman_capturehistories.csv",html,meta(html))

    def test_reject_wrong_size(self):
        raw=b"individual,night,trap\na,1,AA1\nb,2,AA2\nc,3,AA1\n"
        m=meta(raw)
        m["size"]+=10
        with self.assertRaisesRegex(SourcePayloadError,"byte length mismatch"):
            _validate_publication_file("Chapman_capturehistories.csv",raw,m)

    def test_reject_wrong_checksum(self):
        raw=b"individual,night,trap\na,1,AA1\nb,2,AA2\nc,3,AA1\n"
        m=meta(raw)
        m["digest"]="0"*32
        with self.assertRaisesRegex(SourcePayloadError,"checksum mismatch"):
            _validate_publication_file("Chapman_capturehistories.csv",raw,m)

    def test_reject_html_even_named_readme(self):
        raw=b'<html><head><title>Validating...</title></head></html>'
        with self.assertRaisesRegex(SourcePayloadError,"HTML"):
            _validate_publication_file("README_for_Chapman_capturehistories.txt",raw,meta(raw))


if __name__ == "__main__":
    unittest.main()
