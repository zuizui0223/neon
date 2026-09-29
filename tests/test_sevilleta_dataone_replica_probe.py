from __future__ import annotations

import unittest

from analysis import probe_sevilleta_dataone_replica_v1 as m


class DataOneProbeTests(unittest.TestCase):
    def test_candidate_nodes_are_deduplicated(self):
        doc={
            "authoritativeMN":"urn:node:A",
            "replicaMN":["urn:node:A","urn:node:B"],
            "datasource":["urn:node:B","urn:node:C"],
        }
        self.assertEqual(
            m.candidate_nodes(doc),
            ["urn:node:A","urn:node:B","urn:node:C"],
        )

    def test_object_url_for_mn_v2(self):
        url=m.object_url(
            "https://example.org/mn/v2",
            "https://example.org/a b",
        )
        self.assertTrue(url.startswith("https://example.org/mn/v2/object/"))
        self.assertIn("%20",url)


if __name__=="__main__":
    unittest.main()
