"""Synthetic-only tests: no biological outcome file or network access."""
import importlib.util
import unittest
import numpy as np

MODULE = 'analysis.neon_fixed_total_contrast_v1'
AVAILABLE = importlib.util.find_spec(MODULE) is not None
if AVAILABLE:
    from analysis.neon_fixed_total_contrast_v1 import (
        replacement_coefficients, component_contrasts, predictor_support,
    )

class ImplementationTest(unittest.TestCase):
    def test_module_providing_the_approved_contrast_exists(self):
        self.assertTrue(AVAILABLE, 'Fixed-total contrast implementation is missing')

@unittest.skipUnless(AVAILABLE, 'Awaiting implementation after the failing presence test')
class FixedTotalContrastTests(unittest.TestCase):
    def setUp(self):
        self.rng = np.random.default_rng(20261019)
        self.counts = self.rng.integers(2, 30, size=(96, 3)).astype(float)
        self.beta = np.array([[-4., 2.], [-1., 5.], [3., 7.]])

    def test_reparameterization_predicts_exactly_the_same_values(self):
        new_x = np.column_stack((self.counts.sum(axis=1), self.counts[:, 0], self.counts[:, 2]))
        np.testing.assert_allclose(new_x @ replacement_coefficients(self.beta), self.counts @ self.beta, atol=1e-10)

    def test_one_replacement_at_fixed_N_and_U_has_theta_effect(self):
        x = np.array([10., 20., 5.])
        changed = np.array([11., 19., 5.])
        self.assertEqual(x.sum(), changed.sum())
        out = component_contrasts(self.beta)
        np.testing.assert_allclose(changed @ self.beta - x @ self.beta, [out['theta_W'], out['theta_B']])

    def test_equal_component_changes_can_cancel_primary_Theta(self):
        out = component_contrasts(self.beta)
        self.assertEqual(out['theta_W'], -3.)
        self.assertEqual(out['theta_B'], -3.)
        self.assertEqual(out['Theta'], 0.)
        self.assertEqual(out['sum_contrast'], -6.)

    def test_opposite_component_changes_need_not_change_the_sum(self):
        out = component_contrasts(np.array([[-4., 3.], [-1., 0.], [0., 0.]]))
        self.assertEqual(out['Theta'], 6.)
        self.assertEqual(out['sum_contrast'], 0.)

    def test_equal_per_animal_associations_have_no_identity_contrast(self):
        beta = np.array([[-2., 3.], [-2., 3.], [-2., 3.]])
        out = component_contrasts(beta)
        self.assertEqual((out['theta_W'], out['theta_B'], out['Theta']), (0., 0., 0.))

    def test_paired_covariance_is_not_discarded(self):
        covariance = np.eye(6)
        covariance[0, 1] = covariance[1, 0] = 0.75
        out = component_contrasts(self.beta, covariance)
        self.assertAlmostEqual(out['variance_Theta'], 2.5)
        self.assertAlmostEqual(out['variance_theta_W'] + out['variance_theta_B'], 4.)
        self.assertAlmostEqual(out['covariance_theta_W_theta_B'], .75)

    def test_covariance_transform_matches_direct_full_linear_contrast(self):
        mat = self.rng.normal(size=(6, 6))
        cov = mat @ mat.T
        l = np.array([-1., 1., 1., -1., 0., 0.])
        self.assertAlmostEqual(component_contrasts(self.beta, cov)['variance_Theta'], float(l @ cov @ l), places=10)

    def test_invalid_covariance_and_coefficients_rejected(self):
        with self.assertRaises(ValueError):
            replacement_coefficients(np.ones((2, 2)))
        with self.assertRaises(ValueError):
            component_contrasts(self.beta, -np.eye(6))
        with self.assertRaises(ValueError):
            component_contrasts(np.full((3, 2), np.nan))

    def test_independent_U_leaves_both_predictors_identifiable(self):
        out = predictor_support(self.counts)
        self.assertEqual(out['rank_FC_after_nuisance'], 2)
        self.assertEqual(out['rank_FC_after_nuisance_and_U'], 2)
        self.assertEqual(out['rank_FCU_after_nuisance'], 3)
        self.assertTrue(out['fixed_total_replacement_contrast_estimable'])

    def test_U_equal_F_erases_the_replacement_contrast(self):
        x = self.counts.copy()
        x[:, 2] = x[:, 0]
        out = predictor_support(x)
        self.assertEqual(out['rank_FC_after_nuisance'], 2)
        self.assertEqual(out['rank_FC_after_nuisance_and_U'], 1)
        self.assertFalse(out['fixed_total_replacement_contrast_estimable'])

    def test_rank_deficiency_does_not_always_erase_the_contrast(self):
        x = self.counts.copy()
        x[:, 2] = x[:, 0] + x[:, 1]
        out = predictor_support(x)
        self.assertEqual(out['rank_FCU_after_nuisance'], 2)
        self.assertEqual(out['rank_FC_after_nuisance_and_U'], 1)
        self.assertTrue(out['fixed_total_replacement_contrast_estimable'])
        self.assertFalse(out['effect_release_authorized'])

    def test_constant_U_is_absorbed_not_a_spurious_failure(self):
        x = self.counts.copy()
        x[:, 2] = 10.
        out = predictor_support(x)
        self.assertEqual(out['rank_FC_after_nuisance_and_U'], 2)
        self.assertTrue(out['fixed_total_replacement_contrast_estimable'])

    def test_saturated_nuisance_erases_all_identifying_variation(self):
        out = predictor_support(self.counts, np.eye(len(self.counts)))
        self.assertEqual(out['rank_FCU_after_nuisance'], 0)
        self.assertFalse(out['fixed_total_replacement_contrast_estimable'])

    def test_permutation_invariance(self):
        group = np.arange(96) % 8
        z = np.eye(8)[group]
        p = self.rng.permutation(96)
        a = predictor_support(self.counts, z)
        b = predictor_support(self.counts[p], z[p])
        for key in ('rank_FCU_after_nuisance', 'rank_FC_after_nuisance_and_U', 'fixed_total_replacement_contrast_estimable'):
            self.assertEqual(a[key], b[key])
        self.assertAlmostEqual(a['replacement_predictor_residual_SS'], b['replacement_predictor_residual_SS'], places=8)

    def test_redundant_fixed_effect_columns_do_not_change_support(self):
        z = np.eye(8)[np.arange(96) % 8]
        a = predictor_support(self.counts, z)
        b = predictor_support(self.counts, np.column_stack((z, z, np.ones(96))))
        self.assertEqual(a['rank_FCU_after_nuisance'], b['rank_FCU_after_nuisance'])
        self.assertAlmostEqual(a['replacement_predictor_residual_SS'], b['replacement_predictor_residual_SS'], places=8)

    def test_counts_must_be_nonnegative_finite_and_FCU_only(self):
        for bad in (np.full((10, 3), -1), np.full((10, 3), np.nan), np.zeros((10, 4))):
            with self.assertRaises(ValueError):
                predictor_support(bad)

    def test_diagnostic_never_authorizes_an_ecological_fit(self):
        out = predictor_support(self.counts)
        self.assertFalse(out['effect_release_authorized'])
        self.assertFalse(out['spatial_outcomes_used'])
        self.assertNotIn('W_slope', out)
        self.assertNotIn('B_slope', out)

if __name__ == '__main__':
    unittest.main()
