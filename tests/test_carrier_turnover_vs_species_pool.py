import importlib.util
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
MODULE=ROOT/'analysis'/'audit_carrier_turnover_vs_species_pool_v1.py'
spec=importlib.util.spec_from_file_location('carrier_pool_audit',MODULE)
m=importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class CarrierPoolTurnoverAuditTests(unittest.TestCase):
    def test_jaccard(self):
        self.assertEqual(m.jaccard({'a','b'},{'b','c'}),1/3)
        self.assertEqual(m.jaccard({'a'},{'b'}),0.0)

    def test_null_is_deterministic(self):
        sites=[
            {'site':'A','pool':['a','b','c'],'carrier_count':1},
            {'site':'B','pool':['b','c','d'],'carrier_count':1},
        ]
        a=m.simulate_mean_carrier_jaccard(sites,replicates=1000,seed=123)
        b=m.simulate_mean_carrier_jaccard(sites,replicates=1000,seed=123)
        self.assertEqual(a,b)
        self.assertEqual(len(a),1000)


if __name__=='__main__':
    unittest.main()
