import unittest

import numpy as np

from analysis.test_san_jacinto_individual_footprint_assortativity_v1 import (
    contrast,
    jaccard,
    permute_labels_within_size,
)


class TestIndividualFootprintAssortativity(unittest.TestCase):
    def test_jaccard(self):
        self.assertAlmostEqual(jaccard(frozenset({"A1","A2"}), frozenset({"A2","A3"})), 1/3)
        self.assertEqual(jaccard(frozenset({"A1"}), frozenset({"B1"})), 0)

    def test_contrast_positive_when_conspecifics_overlap_more(self):
        labels = np.array([0,0,1,1], dtype=np.int16)
        ii, jj = np.triu_indices(4, 1)
        fps = [
            frozenset({"A1","A2"}),
            frozenset({"A1","A2"}),
            frozenset({"G6","G7"}),
            frozenset({"G6","G7"}),
        ]
        sims = np.array([jaccard(fps[i],fps[j]) for i,j in zip(ii,jj)])
        d, con, het = contrast(labels, ii, jj, sims)
        self.assertGreater(d, 0)
        self.assertEqual(con, 1)
        self.assertEqual(het, 0)

    def test_permutation_stays_within_exact_size_strata(self):
        labels = np.array([0,1,2,0,1,2], dtype=np.int16)
        strata = {1: np.array([0,1,2]), 2: np.array([3,4,5])}
        rng = np.random.default_rng(7)
        out = permute_labels_within_size(labels, strata, rng)
        self.assertCountEqual(out[strata[1]].tolist(), labels[strata[1]].tolist())
        self.assertCountEqual(out[strata[2]].tolist(), labels[strata[2]].tolist())


if __name__ == "__main__":
    unittest.main()
