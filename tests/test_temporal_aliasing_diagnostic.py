from __future__ import annotations

# AI assistance disclosure: This test file was drafted or refactored with OpenAI ChatGPT (GPT-5.6 Sol, September 2026); it remains under author responsibility and is verified in repository workflows.

import unittest

from analysis import temporal_aliasing_diagnostic_v1 as m


class TemporalAliasingDiagnosticTests(unittest.TestCase):
    def test_repeat_group_span(self):
        rows=[
            {"id":"a","night":"1","t":"1","x":"0","y":"0"},
            {"id":"a","night":"1","t":"2","x":"3","y":"4"},
            {"id":"b","night":"1","t":"1","x":"0","y":"0"},
        ]
        spans,qc=m.first_last_spans(
            rows,
            individual_col="id",
            night_col="night",
            time_col="t",
            coordinate_cols=["x","y"],
        )
        self.assertEqual(qc["repeat_observation_individual_nights"],1)
        self.assertAlmostEqual(spans[0]["span"],5.0)

    def test_summary_material_threshold(self):
        spans=[{"span":0.0,"elapsed_time":1.0},{"span":6.25,"elapsed_time":2.0},{"span":12.5,"elapsed_time":3.0}]
        out=m.summarize_spans(spans,material_scale=6.25)
        self.assertAlmostEqual(out["material_shift_fraction"],2/3)
        self.assertAlmostEqual(out["median_span_in_material_scales"],1.0)

    def test_wilson_boundary_endpoints(self):
        self.assertEqual(m.wilson_interval(0,50)[0],0.0)
        self.assertEqual(m.wilson_interval(50,50)[1],1.0)

    def test_state_mixing_scale_and_ratio(self):
        # Two exposed spans among four total occasions:
        # sqrt((3^2+4^2)/(2*4)) = sqrt(25/8).
        scale=m.observed_transition_energy_scale([3,4],4)
        self.assertAlmostEqual(scale,(25/8)**0.5)
        out=m.state_mixing_sensitivity([3,4],4,sigma_ref=5)
        self.assertAlmostEqual(out["state_mixing_ratio_A_sigma"],scale/5)
        self.assertAlmostEqual(
            out["second_moment_predicted_sigma_ratio"],
            (1+(scale/5)**2)**0.5,
        )
        self.assertAlmostEqual(
            out["ten_percent_materiality_A_sigma"],
            (1.10**2-1)**0.5,
        )

    def test_state_mixing_denominator_validation(self):
        with self.assertRaises(ValueError):
            m.observed_transition_energy_scale([1,2],1)

    def test_bounds(self):
        self.assertEqual(m.movement_sensitivity_bound(2,3),5)
        self.assertEqual(m.mpd_sensitivity_bound([2,4]),6)
        self.assertEqual(m.standardized_mpd_sensitivity_bound([2,4],2),3)


if __name__=="__main__":
    unittest.main()
