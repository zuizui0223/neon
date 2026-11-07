#!/usr/bin/env python3
"""Algebra/support helpers for the existing NEON conspecific-congener hypothesis.

No downloads, no outcome fitting, and no changes to historical NEON results.
Counts are ordered F, C, U. Coefficients are rows F/C/U and columns W/B.
Re-expression in N=F+C+U, F, U retains the original primary Theta exactly.
"""
from __future__ import annotations
import numpy as np

# Maps coefficient rows [F, C, U] to [N, F-at-fixed-N-U, U-at-fixed-N-F].
REPARAMETERIZATION = np.array([[0., 1., 0.], [1., -1., 0.], [0., -1., 1.]])
# For row-major beta.reshape(-1): [FW, FB, CW, CB, UW, UB].
COMPONENT_MAP = np.array([[1., 0., -1., 0., 0., 0.],
                          [0., 1., 0., -1., 0., 0.]])
RELATIVE_RANK_TOL = 1e-9


def _beta_array(beta: object) -> np.ndarray:
    arr = np.asarray(beta, dtype=float)
    if arr.shape != (3, 2) or not np.all(np.isfinite(arr)):
        raise ValueError('Expected finite coefficient matrix: rows F/C/U, columns W/B')
    return arr


def replacement_coefficients(beta: object) -> np.ndarray:
    """Equivalent coefficients; not a new fit or a causal substitution estimate."""
    return REPARAMETERIZATION @ _beta_array(beta)


def component_contrasts(beta: object, covariance: object | None = None) -> dict:
    """Calculate the two component contrasts and original primary Theta.

    The optional 6x6 covariance must include paired W/B estimation covariance.
    The routine does not estimate it, assign p-values, or infer biological support.
    """
    original = _beta_array(beta)
    theta = COMPONENT_MAP @ original.reshape(-1)
    result = {
        'theta_W': float(theta[0]),
        'theta_B': float(theta[1]),
        'Theta': float(theta[1] - theta[0]),
        'sum_contrast': float(theta[1] + theta[0]),
        'primary_estimand_changed': False,
        'causal_interpretation_authorized': False,
    }
    if covariance is not None:
        cov = np.asarray(covariance, dtype=float)
        if cov.shape != (6, 6) or not np.all(np.isfinite(cov)):
            raise ValueError('Expected finite 6x6 joint coefficient covariance')
        if not np.allclose(cov, cov.T, atol=1e-10, rtol=1e-10):
            raise ValueError('Covariance must be symmetric')
        cov = (cov + cov.T) / 2.
        scale = max(1., float(np.linalg.norm(cov, ord=2)))
        if float(np.linalg.eigvalsh(cov).min()) < -1e-10 * scale:
            raise ValueError('Covariance must be positive semidefinite')
        paired = COMPONENT_MAP @ cov @ COMPONENT_MAP.T
        l = np.array([-1., 1.])
        result.update({
            'variance_theta_W': float(paired[0, 0]),
            'variance_theta_B': float(paired[1, 1]),
            'covariance_theta_W_theta_B': float(paired[0, 1]),
            'variance_Theta': float(l @ paired @ l),
        })
    return result


def _residualize(x: np.ndarray, z: np.ndarray) -> np.ndarray:
    # Orthogonal projection tolerates redundant fixed effects. Normalize
    # nuisance columns so mixed units alone do not create rank decisions.
    norms = np.linalg.norm(z, axis=0)
    scaled = z[:, norms > 0.] / norms[norms > 0.]
    left, singular, _ = np.linalg.svd(scaled, full_matrices=False)
    keep = singular > 1e-10 * max(1., float(singular[0]))
    basis = left[:, keep]
    return x - basis @ (basis.T @ x)


def _rank_parts(residuals: np.ndarray, tolerance: float) -> tuple:
    _, values, vt = np.linalg.svd(residuals, full_matrices=False)
    rank = int(np.sum(values > tolerance))
    return rank, values, vt


def predictor_support(counts: object, nuisance: object | None = None) -> dict:
    """Outcome-blind support for F/C before and after U adjustment.

    Required input columns: F, C, U, not N,F,C,U together (exact dependence).
    This is a numerical diagnostic, NOT a replacement for the frozen sample,
    taxonomy, geographical-replication or new-response release requirements.
    It reports contrast-specific estimability separately from full rank.
    """
    x = np.asarray(counts, dtype=float)
    if x.ndim != 2 or x.shape[1] != 3 or x.shape[0] < 4:
        raise ValueError('Supply at least four rows of F, C, U counts only')
    if not np.all(np.isfinite(x)) or np.any(x < 0.):
        raise ValueError('Counts must be finite and nonnegative')
    n = x.shape[0]
    z = np.ones((n, 1))
    if nuisance is not None:
        cov = np.asarray(nuisance, dtype=float)
        if cov.ndim != 2 or cov.shape[0] != n or not np.all(np.isfinite(cov)):
            raise ValueError('Nuisance matrix must be finite and have one row per session')
        z = np.column_stack((z, cov))
    tolerance = RELATIVE_RANK_TOL * max(1., float(np.linalg.norm(x, ord=2)))
    r_all = _residualize(x, z)
    rank_all, _, vt = _rank_parts(r_all, tolerance)
    rank_fc, _, _ = _rank_parts(r_all[:, :2], tolerance)
    r_fc_u = _residualize(x[:, :2], np.column_stack((z, x[:, 2])))
    rank_after_u, singular_fc_u, _ = _rank_parts(r_fc_u, tolerance)

    # beta_F-beta_C is estimable exactly when l is in row(X residualized on Z).
    # Full rank is sufficient but not necessary: U=F+C is a counterexample.
    l = np.array([1., -1., 0.])
    rowbasis = vt[:rank_all]
    null_component = l - rowbasis.T @ (rowbasis @ l)
    null_norm = float(np.linalg.norm(null_component))
    estimable = bool(null_norm <= 1e-7 * np.linalg.norm(l))

    # Direct equivalent support for the F coefficient with N and U held fixed.
    total = x.sum(axis=1)
    rf = _residualize(x[:, [0]], np.column_stack((z, total, x[:, 2])))
    replacement_ss = float(np.sum(rf ** 2))
    return {
        'schema': 'neon.fixed_total_predictor_support.v1',
        'rows': n,
        'rank_FC_after_nuisance': rank_fc,
        'rank_FC_after_nuisance_and_U': rank_after_u,
        'rank_FCU_after_nuisance': rank_all,
        'condition_FC_after_nuisance_and_U': (
            float(singular_fc_u[0] / singular_fc_u[1]) if rank_after_u == 2 else None
        ),
        'fixed_total_replacement_contrast_estimable': estimable,
        'contrast_nullspace_projection_norm': null_norm,
        'replacement_predictor_residual_SS': replacement_ss,
        'numerical_rank_tolerance': tolerance,
        'spatial_outcomes_used': False,
        'effect_release_authorized': False,
        'frozen_support_thresholds_replaced': False,
        'scope': 'Predictor-only algebra; conditional support is not species validation, power or causation',
    }
