from __future__ import annotations

import unittest

from analysis import resolve_dryad_files_v1 as m


class DryadResolverTests(unittest.TestCase):
    def test_href_finds_hal_relation(self):
        obj={"_links":{"stash:files":{"href":"/api/v2/versions/1/files"}}}
        self.assertEqual(m._href(obj,"files"),"/api/v2/versions/1/files")

    def test_absolute_handles_relative_url(self):
        self.assertEqual(
            m._absolute("/api/v2/search"),
            "https://datadryad.org/api/v2/search",
        )

    def test_embedded_lists_collects_hal_arrays(self):
        obj={"_embedded":{"stash:files":[{"path":"x.csv"}]}}
        rows=m._embedded_lists(obj)
        self.assertTrue(any(r and r[0]["path"]=="x.csv" for r in rows))


if __name__=="__main__":
    unittest.main()
