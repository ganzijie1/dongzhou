import sys
import unittest
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parent))

from pcgrl_mobile import CELL_COUNT, FEATURE_COUNT, HEIGHT, WIDTH, build_features, hash_unit, heuristic_targets, map_metrics


class PcgrlMobileTest(unittest.TestCase):
    def test_features_are_deterministic_and_finite(self):
        left = build_features(0.5, 12345)
        right = build_features(0.5, 12345)
        self.assertEqual(left.shape, (CELL_COUNT, FEATURE_COUNT))
        self.assertTrue(np.array_equal(left, right))
        self.assertTrue(np.isfinite(left).all())

    def test_hash_is_reproducible(self):
        self.assertEqual(hash_unit(17, 23, 91), hash_unit(17, 23, 91))
        self.assertNotEqual(hash_unit(17, 23, 91), hash_unit(18, 23, 91))

    def test_safe_prior_keeps_spawns_connected(self):
        for difficulty in (0.0, 0.5, 1.0):
            tiles = heuristic_targets(difficulty, 20261102)
            metrics = map_metrics(tiles, difficulty)
            self.assertTrue(metrics["connected"])
            self.assertEqual(metrics["spawn_clear"], 1.0)

    def test_dimensions_match_mobile_contract(self):
        self.assertEqual((WIDTH, HEIGHT, CELL_COUNT), (19, 14, 266))


if __name__ == "__main__":
    unittest.main()
