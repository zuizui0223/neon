from __future__ import annotations

import unittest

from analysis.multiscale_density_fixed_effects_v1 import (
    evaluate_frozen_model,
    fit_slope,
)


GENERA = [
    "Chaetodipus","Dipodomys","Microtus","Myodes",
    "Napaeozapus","Onychomys","Peromyscus","Sigmodon",
]


def synthetic_rows():
    rows = []
    for gi, genus in enumerate(GENERA):
        for si in range(2):
            series = f"{genus}|plot{si}"
            site = f"S{gi:02d}"
            for t in range(6):
                # Repeated month/year patterns leave within-series abundance variation.
                month = 1 + (t // 2)
                year = 2020 + (t % 2)
                # Non-additive within-series pattern so MNKA is not perfectly
                # explained by the frozen site-month + year nuisance terms.
                mnka_pattern = (2, 6, 3, 8, 7, 4)
                mnka = mnka_pattern[t] + si
                series_offset = 100.0 * si + 10.0 * gi
                calendar = 7.0 * month + 3.0 * (year - 2020)
                W = series_offset + calendar - 2.0 * mnka
                B = series_offset + calendar + 3.0 * mnka
                rows.append({
                    "genus": genus,
                    "site": site,
                    "series_id": series,
                    "site_month": f"{site}|{month:02d}",
                    "year": str(year),
                    "mnka": float(mnka),
                    "W_m2": W,
                    "B_debiased_m2": B,
                    "B_observed_m2": B + 1.0,
                    "D_m2": B - W,
                })
    return rows


class MultiscaleDensityFixedEffectsTests(unittest.TestCase):
    def test_fixed_effects_recovers_known_slope(self):
        rows = synthetic_rows()
        fit = fit_slope(rows, response="D_m2", genus_balanced=True)
        self.assertAlmostEqual(fit.beta, 5.0, places=9)

    def test_secondary_slopes_and_identity_difference(self):
        result = evaluate_frozen_model(
            synthetic_rows(), frozen_genera=GENERA
        )
        self.assertAlmostEqual(
            result["secondary_slopes"]["beta_W"], -2.0, places=9
        )
        self.assertAlmostEqual(
            result["secondary_slopes"]["beta_B_debiased"], 3.0, places=9
        )
        self.assertAlmostEqual(
            result["secondary_slopes"]["difference_identity_check"], 5.0,
            places=9,
        )
        self.assertAlmostEqual(
            result["primary_delta"]["beta"], 5.0, places=9
        )

    def test_generality_guard_passes_when_all_genera_positive(self):
        result = evaluate_frozen_model(
            synthetic_rows(), frozen_genera=GENERA
        )
        self.assertEqual(result["positive_genus_count"], 8)
        self.assertTrue(result["all_leave_one_genus_out_positive"])
        self.assertTrue(result["decision"]["development_cross_scale_support"])
        self.assertTrue(result["decision"]["strong_form_supported"])


if __name__ == "__main__":
    unittest.main()
