"""Real Python3 vector division used by Follow Me ROI velocity."""
import importlib.util
from pathlib import Path
import unittest

SPEC = importlib.util.spec_from_file_location(
    "qualification_vector3", Path(__file__).resolve().parents[1] / "vector3.py")
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)
Vector3 = MODULE.Vector3


class VectorDivisionTests(unittest.TestCase):
    def test_scalar_division_returns_independent_vector_without_mutation(self):
        for divisor, expected in [(2, (6, -3, 1.5)),
                                  (0.5, (24, -12, 6)),
                                  (-2, (-6, 3, -1.5))]:
            with self.subTest(divisor=divisor):
                original = Vector3(12, -6, 3)
                result = original / divisor
                self.assertIsInstance(result, Vector3)
                self.assertIsNot(result, original)
                self.assertEqual(tuple(result), expected)
                self.assertEqual(tuple(original), (12, -6, 3))
                result.x = 99
                self.assertEqual(original.x, 12)

    def test_zero_divisor_raises_without_mutating_input(self):
        original = Vector3(12, -6, 3)
        with self.assertRaises(ZeroDivisionError):
            original / 0
        self.assertEqual(tuple(original), (12, -6, 3))


if __name__ == "__main__":
    unittest.main()
