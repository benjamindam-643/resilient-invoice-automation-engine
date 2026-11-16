import unittest
from src.rules_engine.duplicate_detector import DuplicateDetector
from src.rules_engine.tax_checker import verify_tax_compliance


class TestRulesEngine(unittest.TestCase):
    def test_duplicate_fingerprint_detection(self):
        detector = DuplicateDetector()
        supplier = "FleetShop-42"
        inv_no = "INV-2026-991"
        amt = 1540.00
        date = "2026-11-10"

        # First encounter should not be duplicate
        is_dup = detector.check_duplicate(supplier, inv_no, amt, date)
        self.assertFalse(is_dup)

        # Second encounter must be detected as duplicate
        is_dup2 = detector.check_duplicate(supplier, inv_no, amt, date)
        self.assertTrue(is_dup2)

    def test_tax_rate_variance_rejection(self):
        # 15% GST expected (NZ standard). Subtotal 1000. Stated tax 50.00 (expected 150)
        res = verify_tax_compliance(subtotal=1000.0, reported_tax=50.0, expected_tax_rate=0.15)
        self.assertFalse(res.is_compliant)
        self.assertTrue(res.gst_error)
        self.assertTrue(any("GST discrepancy detected" in flag for flag in res.flags))

    def test_over_limit_spending_threshold(self):
        # Limit 5000, Total = 5500
        res = verify_tax_compliance(
            subtotal=5000.0,
            reported_tax=500.0,
            expected_tax_rate=0.10,
            spending_limit=5000.0,
        )
        self.assertFalse(res.is_compliant)
        self.assertTrue(res.over_limit)
        self.assertTrue(any("Spending limit exceeded" in flag for flag in res.flags))


if __name__ == "__main__":
    unittest.main()
