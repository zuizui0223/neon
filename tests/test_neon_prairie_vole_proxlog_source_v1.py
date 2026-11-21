"""Pure tests of Figshare *metadata* audit; no external raw sensor rows."""
from __future__ import annotations
import unittest
from analysis.audit_neon_prairie_vole_proxlog_source_v1 import canonical_hash,PROJECT_ID
class PrairieVoleFigshareSourceTests(unittest.TestCase):
    def test_frozen_public_project_identifier(self):
        self.assertEqual(PROJECT_ID,228462)
    def test_source_metadata_digest_stable_across_object_key_order(self):
        a={"id":228462,"files":[{"size":12,"name":"foo.csv"}]}
        b={"files":[{"name":"foo.csv","size":12}],"id":228462}
        self.assertEqual(canonical_hash(a),canonical_hash(b))
    def test_source_metadata_digest_sensitive_to_file_size(self):
        a={"id":228462,"files":[{"size":12}]}
        b={"id":228462,"files":[{"size":13}]}
        self.assertNotEqual(canonical_hash(a),canonical_hash(b))
if __name__=="__main__":
    unittest.main()
