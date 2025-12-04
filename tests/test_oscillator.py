import unittest
from oscillator import Oscillator


class TestOscillator(unittest.TestCase):
    def test_positions(self):
        osc = Oscillator(center_y=100, amplitude=10, frequency_hz=20)
        self.assertEqual(osc.position_at(0.0), 110)
        self.assertEqual(osc.position_at(1.0 / (20 * 2)), 90)
        self.assertEqual(osc.top(), 110)
        self.assertEqual(osc.bottom(), 90)

    def test_offset(self):
        osc = Oscillator(center_y=0, amplitude=8, frequency_hz=15)
        self.assertEqual(osc.offset_at(0.0), 8)
        self.assertEqual(osc.offset_at(1.0 / (15 * 2)), -8)


if __name__ == "__main__":
    unittest.main()
