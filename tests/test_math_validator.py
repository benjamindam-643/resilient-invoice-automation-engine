import unittest
from src.parser.math_validator import InvoiceLineItem, validate_invoice_math


class TestMathValidator(unittest.TestCase):
    def test_clean_math_passes_without_review(self):
        items = [
            InvoiceLineItem(description="Tire Mount", amount=100.00, line_number=1),
            InvoiceLineItem(description="Brake Pad Replacement", amount=250.50, line_number=2),
            InvoiceLineItem(description="Shop Supplies", amount=49.50, line_number=3),
        ]
        res = validate_invoice_math(
            line_items=items,
            reported_subtotal=400.00,
            reported_tax=40.00,
            reported_total=440.00,
        )
        self.assertTrue(res.is_valid)
        self.assertFalse(res.needs_review)
        self.assertEqual(len(res.discrepancy_reasons), 0)

    def test_line_item_sum_mismatch_triggers_needs_review(self):
        items = [
            InvoiceLineItem(description="Tire Mount", amount=100.00, line_number=1),
            InvoiceLineItem(description="Brake Pad", amount=250.00, line_number=2),
        ]
        res = validate_invoice_math(
            line_items=items,
            reported_subtotal=400.00,
            reported_tax=40.00,
            reported_total=440.00,
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(res.needs_review)
        self.assertTrue(any("does not match reported subtotal" in r for r in res.discrepancy_reasons))

    def test_total_mismatch_triggers_needs_review(self):
        items = [InvoiceLineItem(description="Oil Change", amount=100.00, line_number=1)]
        res = validate_invoice_math(
            line_items=items,
            reported_subtotal=100.00,
            reported_tax=10.00,
            reported_total=125.00,  # Corrupted total (expected 110.00)
        )
        self.assertFalse(res.is_valid)
        self.assertTrue(res.needs_review)
        self.assertTrue(any("Subtotal" in r and "Total" in r for r in res.discrepancy_reasons))


if __name__ == "__main__":
    unittest.main()
