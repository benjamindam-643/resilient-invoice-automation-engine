"""Pipeline Intake & Workflow Coordinator.

Integrates OCR bounding-box parsing, deterministic mathematical validation,
business rules enforcement, and automated approval dispatching.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence

from src.parser.geometry import WordBox, cluster_words_into_lines
from src.parser.table_extractor import GenericTableExtractor
from src.parser.math_validator import InvoiceLineItem, MathValidationResult, validate_invoice_math
from src.rules_engine.duplicate_detector import DuplicateDetector
from src.rules_engine.tax_checker import ComplianceResult, verify_tax_compliance
from src.pipeline.approval_dispatcher import ApprovalDispatcher


@dataclass
class ProcessingResult:
    invoice_number: str
    supplier_name: str
    invoice_date: str
    subtotal: float
    tax_amount: float
    total: float
    line_items: List[Dict[str, Any]]
    math_validation: Dict[str, Any]
    rule_violations: List[str]
    needs_review: bool
    status: str  # "APPROVED_FOR_EXPORT" or "PENDING_APPROVAL"
    fingerprint_hash: str


class InvoicePipelineCoordinator:
    """
    End-to-End Orchestrator:
    1. Parse OCR tokens via geometric clustering.
    2. Extract line-item tables deterministically without shop-specific templates.
    3. Run accounting math checks (cross-footing, line summation).
    4. Run business rules (duplicate prevention, statutory tax variance, spending limits).
    5. Route to MS Teams / Webhook if human-in-the-loop review is required.
    """

    def __init__(
        self,
        duplicate_detector: Optional[DuplicateDetector] = None,
        dispatcher: Optional[ApprovalDispatcher] = None,
        expected_tax_rate: float = 0.10,
        spending_limit: Optional[float] = 5000.0,
    ) -> None:
        self.table_extractor = GenericTableExtractor()
        self.duplicate_detector = duplicate_detector or DuplicateDetector()
        self.dispatcher = dispatcher or ApprovalDispatcher()
        self.expected_tax_rate = expected_tax_rate
        self.spending_limit = spending_limit

    def process_raw_ocr_payload(
        self,
        ocr_words: List[Dict[str, Any]],
        header_metadata: Dict[str, Any],
    ) -> ProcessingResult:
        """
        Processes raw OCR page words and header metadata.
        header_metadata expects:
            - invoice_number (str)
            - supplier_name (str)
            - invoice_date (str)
            - stated_subtotal (float)
            - stated_tax (float)
            - stated_total (float)
        """
        # Step 1: Geometry clustering
        word_boxes = [
            WordBox(
                text=str(w["text"]),
                x0=float(w["x0"]),
                y0=float(w["y0"]),
                x1=float(w["x1"]),
                y1=float(w["y1"]),
                confidence=float(w.get("confidence", 1.0)),
            )
            for w in ocr_words
        ]
        clustered_lines = cluster_words_into_lines(word_boxes)

        # Step 2: Deterministic Table Extraction
        extracted_lines = self.table_extractor.extract_line_items(clustered_lines)

        stated_subtotal = float(header_metadata.get("stated_subtotal", 0.0))
        stated_tax = float(header_metadata.get("stated_tax", 0.0))
        stated_total = float(header_metadata.get("stated_total", 0.0))
        supplier_name = str(header_metadata.get("supplier_name", "UNKNOWN"))
        invoice_number = str(header_metadata.get("invoice_number", "UNKNOWN"))
        invoice_date = str(header_metadata.get("invoice_date", ""))

        # Step 3: Mathematical Consistency & Cross-Footing
        math_res = validate_invoice_math(
            line_items=extracted_lines,
            reported_subtotal=stated_subtotal,
            reported_tax=stated_tax,
            reported_total=stated_total,
        )

        # Step 4: Business Rules Engine
        rule_violations: List[str] = []

        # Duplicate check
        is_dup = self.duplicate_detector.check_duplicate(
            supplier_id=supplier_name,
            invoice_number=invoice_number,
            total_amount=stated_total,
            date_str=invoice_date,
        )
        fingerprint = self.duplicate_detector.generate_fingerprint(
            supplier_id=supplier_name,
            invoice_number=invoice_number,
            total_amount=stated_total,
            date_str=invoice_date,
        )
        if is_dup:
            rule_violations.append(f"Duplicate invoice detected for {supplier_name} #{invoice_number}.")

        # Tax variance & spending limits
        tax_res = verify_tax_compliance(
            subtotal=stated_subtotal,
            reported_tax=stated_tax,
            expected_tax_rate=self.expected_tax_rate,
            spending_limit=self.spending_limit,
        )
        if not tax_res.is_compliant:
            rule_violations.extend(tax_res.flags)

        # Overall needs_review flag
        needs_review = math_res.needs_review or (len(rule_violations) > 0)
        status = "PENDING_APPROVAL" if needs_review else "APPROVED_FOR_EXPORT"

        result = ProcessingResult(
            invoice_number=invoice_number,
            supplier_name=supplier_name,
            invoice_date=invoice_date,
            subtotal=stated_subtotal,
            tax_amount=stated_tax,
            total=stated_total,
            line_items=[
                {
                    "description": item.description,
                    "amount": item.amount,
                    "line_number": item.line_number,
                }
                for item in extracted_lines
            ],
            math_validation=asdict(math_res),
            rule_violations=rule_violations,
            needs_review=needs_review,
            status=status,
            fingerprint_hash=fingerprint,
        )

        # Step 5: Dispatch to Teams / Notification if review needed
        if needs_review:
            invoice_summary = {
                "invoice_number": invoice_number,
                "supplier_name": supplier_name,
                "total": stated_total,
            }
            all_flags = math_res.discrepancy_reasons + rule_violations
            self.dispatcher.dispatch_for_review(invoice_summary, all_flags)

        return result
