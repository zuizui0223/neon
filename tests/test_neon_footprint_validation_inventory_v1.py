import unittest
from collections import defaultdict, Counter
from analysis.inventory_neon_footprint_validation_v1 import is_capture

class TestNeonFootprintInventory(unittest.TestCase):
    def test_capture_status(self):
        self.assertTrue(is_capture("5 - capture"))
        self.assertTrue(is_capture("4 - more than 1 capture in one trap"))
        self.assertFalse(is_capture("1 - no capture"))
        self.assertFalse(is_capture("2 - trap closed"))
if __name__=="__main__": unittest.main()
