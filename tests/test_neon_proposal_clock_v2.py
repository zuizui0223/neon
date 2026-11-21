import unittest
from collections import Counter
from itertools import combinations, product
from random import Random
from fractions import Fraction
from analysis.neon_proposal_clock_v2 import proposal_step, exact_kernel, corrected_unit


class UniformClockTests(unittest.TestCase):
    def states(self):
        masks=[sum(1<<k for k in p) for p in combinations(range(4),2)]
        return [s for s in product(masks,repeat=3) if tuple(sum(bool(x & (1<<j)) for x in s) for j in range(4))==(1,1,2,2)]

    def test_empirical_uniform_not_accepted_jump_chain(self):
        s=[12,12,3]
        freq=Counter()
        rng=Random(412)
        for t in range(180000):
            proposal_step(s,rng)
            if t>=10000:
                freq[tuple(s)]+=1
        self.assertEqual(len(freq),15)
        self.assertLess(max(abs(freq[x]/170000-1/15) for x in self.states()),0.004)

    def test_exact_transition_is_symmetric_and_uniform(self):
        ss=self.states()
        K={s:exact_kernel(s) for s in ss}
        for s in ss:
            self.assertEqual(sum(K[s].values()),1)
            self.assertGreaterEqual(K[s].get(s,0),Fraction(1,2))
            self.assertEqual(sum(K[t].get(s,0) for t in ss),1)
            for t in ss:
                self.assertEqual(K[s].get(t,0),K[t].get(s,0))

    def test_old_accepted_clock_is_not_uniform(self):
        ss=self.states()
        P={s:exact_kernel(s,lazy=False) for s in ss}
        J={s:{t:v/(1-P[s][s]) for t,v in P[s].items() if t!=s} for s in ss}
        self.assertTrue(any(sum(J[t].get(s,0) for t in ss)!=1 for s in ss))
        p=[1-P[s][s] for s in ss]
        total=sum(p)
        self.assertEqual(p[0]/total,Fraction(1,21))

    def test_preserves_margins_per_attempt(self):
        s=[12,12,3]
        rng=Random(1)
        for t in range(2000):
            proposal_step(s,rng)
            self.assertEqual([x.bit_count() for x in s],[2,2,2])
            self.assertEqual([sum(bool(x & (1<<j)) for x in s) for j in range(4)],[1,1,2,2])

    def test_two_chains_quality_and_reproducibility(self):
        A={'G1':{'A3','A4'},'G2':{'A3','A4'},'G3':{'A1','A2'}}
        d=[]
        x=corrected_unit(A,A,seed=5,draws_out=d,n_draws=1000,burn=2000,thin=50,min_ess=100)
        y=corrected_unit(A,A,seed=5,n_draws=1000,burn=2000,thin=50,min_ess=100)
        self.assertEqual(x,y)
        self.assertEqual(len(d),2000)
        self.assertAlmostEqual(x['null_mean'],10/3,delta=.13)
        self.assertGreater(x['z'],0)
        self.assertTrue(x['quality_pass'])

    def test_unmoving_matrix_is_no_information(self):
        A={g:{'A1','A2'} for g in ('a','b','c')}
        x=corrected_unit(A,A,seed=5,n_draws=100,burn=20,thin=5,min_ess=10)
        self.assertFalse(x['quality_pass'])
        self.assertIsNone(x['z'])

    def test_output_has_no_source_taxa_or_traps(self):
        A={g:{'A1','A2'} for g in ('GENUSSECRET1','GENUSSECRET2','GENUSSECRET3')}
        x=corrected_unit(A,A,seed=5,n_draws=100,burn=20,thin=5,min_ess=10)
        self.assertNotIn('SECRET',str(x))
        self.assertNotIn('A1',str(x))


if __name__=='__main__':
    unittest.main()
