import importlib.util
import pathlib
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[1]
PATH = ROOT / "analysis" / "simulate_san_jacinto_scr_sigma_downstream_v1.py"
spec = importlib.util.spec_from_file_location("sigma_sim", PATH)
mod = importlib.util.module_from_spec(spec)
assert spec.loader is not None
spec.loader.exec_module(mod)


class TestSigmaDownstreamSimulation(unittest.TestCase):
    def test_representations_share_animals_and_nights(self):
        cfg = mod.SimulationConfig(population_n=80, nights=3, checks_per_night=3)
        y = mod.simulate_capture_array(7, 0.0, cfg)
        reps = mod.collapse_representations(y)
        self.assertEqual(reps["first_nightly"].shape, (80, 3))
        self.assertEqual(reps["last_nightly"].shape, (80, 3))
        self.assertEqual(reps["check_level"].shape, (80, 9))
        self.assertTrue(
            (
                (reps["first_nightly"] >= 0).any(axis=1)
                == (reps["last_nightly"] >= 0).any(axis=1)
            ).all()
        )

    def test_handling_zero_is_deterministic_given_seed(self):
        cfg = mod.SimulationConfig(population_n=60, nights=2, checks_per_night=3)
        a = mod.simulate_capture_array(11, 0.0, cfg)
        b = mod.simulate_capture_array(11, 0.0, cfg)
        self.assertTrue((a == b).all())

    def test_small_benchmark_schema(self):
        out = mod.run_benchmark(replicates=2, seed=13)
        self.assertEqual(
            out["schema"],
            "neon.san_jacinto_scr_sigma_downstream_simulation.v1",
        )
        self.assertEqual(len(out["cells"]), 7)
        self.assertEqual(out["cells"][0]["handling_median_m"], 0.0)
        for cell in out["cells"]:
            for representation in ("first_nightly", "last_nightly", "check_level"):
                self.assertGreaterEqual(
                    cell["fits"][representation]["convergence_fraction"],
                    0.5,
                )


if __name__ == "__main__":
    unittest.main()
