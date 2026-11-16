import unittest
from src.pipeline.intake import InvoicePipelineCoordinator


class TestPipelineCoordinator(unittest.TestCase):
    def test_pipeline_clean_flow(self):
        coordinator = InvoicePipelineCoordinator(expected_tax_rate=0.10, spending_limit=1000.0)

        # Simulated OCR words
        ocr_words = [
            # Header
            {"text": "ITEM", "x0": 20, "y0": 100, "x1": 50, "y1": 112},
            {"text": "DESCRIPTION", "x0": 55, "y0": 100, "x1": 130, "y1": 112},
            {"text": "EXTD", "x0": 300, "y0": 100, "x1": 340, "y1": 112},
            # Line 1
            {"text": "Engine", "x0": 20, "y0": 130, "x1": 60, "y1": 142},
            {"text": "Oil Filter", "x0": 65, "y0": 130, "x1": 120, "y1": 142},
            {"text": "45.00", "x0": 300, "y0": 130, "x1": 340, "y1": 142},
            # Line 2
            {"text": "Brake", "x0": 20, "y0": 160, "x1": 60, "y1": 172},
            {"text": "Caliper Service", "x0": 65, "y0": 160, "x1": 150, "y1": 172},
            {"text": "155.00", "x0": 300, "y0": 160, "x1": 340, "y1": 172},
            # Summary strip (should not be treated as a line item)
            {"text": "SUBTOTAL", "x0": 20, "y0": 220, "x1": 80, "y1": 232},
            {"text": "200.00", "x0": 300, "y0": 220, "x1": 340, "y1": 232},
            {"text": "TOTAL DUE", "x0": 20, "y0": 250, "x1": 90, "y1": 262},
            {"text": "220.00", "x0": 300, "y0": 250, "x1": 340, "y1": 262},
        ]

        metadata = {
            "invoice_number": "INV-88910",
            "supplier_name": "Freightliner Service Center",
            "invoice_date": "2026-11-15",
            "stated_subtotal": 200.00,
            "stated_tax": 20.00,
            "stated_total": 220.00,
        }

        result = coordinator.process_raw_ocr_payload(ocr_words, metadata)

        self.assertEqual(len(result.line_items), 2)
        self.assertEqual(result.line_items[0]["amount"], 45.00)
        self.assertEqual(result.line_items[1]["amount"], 155.00)
        self.assertFalse(result.needs_review)
        self.assertEqual(result.status, "APPROVED_FOR_EXPORT")

    def test_pipeline_flagged_flow_on_wrong_subtotal(self):
        coordinator = InvoicePipelineCoordinator(expected_tax_rate=0.10, spending_limit=5000.0)

        ocr_words = [
            {"text": "DESCRIPTION", "x0": 20, "y0": 100, "x1": 100, "y1": 112},
            {"text": "AMOUNT", "x0": 200, "y0": 100, "x1": 250, "y1": 112},
            {"text": "Transmission Repair", "x0": 20, "y0": 130, "x1": 140, "y1": 142},
            {"text": "500.00", "x0": 200, "y0": 130, "x1": 250, "y1": 142},
        ]

        metadata = {
            "invoice_number": "INV-ERROR-01",
            "supplier_name": "Mack Truck Repairs",
            "invoice_date": "2026-11-15",
            "stated_subtotal": 999.00,  # Does not match line sum 500.00
            "stated_tax": 50.00,
            "stated_total": 1049.00,
        }

        result = coordinator.process_raw_ocr_payload(ocr_words, metadata)

        self.assertTrue(result.needs_review)
        self.assertEqual(result.status, "PENDING_APPROVAL")
        self.assertTrue(len(result.math_validation["discrepancy_reasons"]) > 0)


if __name__ == "__main__":
    unittest.main()
