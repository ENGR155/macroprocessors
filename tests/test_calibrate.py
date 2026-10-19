import sys
import unittest
from pathlib import Path
import numpy as np
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "tools"))
from calibrate import fit, evaluate


class CalibrationTests(unittest.TestCase):
    def test_recover_affine_model(self):
        rng = np.random.default_rng(155)
        x = rng.uniform([500, 1000, 0], [3000, 3500, 0.4], (60, 3))
        y = 1 + 0.004*x[:, 0] + 0.001*x[:, 1] - 2*x[:, 2]
        a = np.column_stack((x, y))
        c = fit(a[:40])
        self.assertLess(evaluate(c, a[40:])[1], 1e-10)

    def test_reject_indistinguishable_signals(self):
        x = np.linspace(1000, 2000, 20)
        with self.assertRaises(ValueError):
            fit(np.column_stack((x, 2*x, x/10000, x/200)))

    def test_holdout_exposes_wrong_model(self):
        rng = np.random.default_rng(155)
        x = rng.uniform(1, 10, (30, 3))
        a = np.column_stack((x, x[:, 0]**2))
        self.assertGreater(evaluate(fit(a), a)[0], 1)


if __name__ == "__main__":
    unittest.main()
