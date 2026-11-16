"""Deterministic Accounting & Math Integrity Invariant Gate.

Validates that individual line item charges reconcile mathematically with subtotals,
tax liabilities, and grand totals. Flashes the `needs_review` flag if any discrepancy occurs.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class InvoiceLineItem:
    description: str
    amount: float
    line_number: int


@dataclass
class MathValidationResult:
    is_valid: bool
    needs_review: bool
    calculated_subtotal: float
    reported_subtotal: Optional[float]
    reported_tax: Optional[float]
    reported_total: Optional[float]
    discrepancy_reasons: List[str]


def validate_invoice_math(
    line_items: List[InvoiceLineItem],
    reported_subtotal: Optional[float] = None,
    reported_tax: Optional[float] = None,
    reported_total: Optional[float] = None,
    tolerance: float = 0.02,
) -> MathValidationResult:
    """Zero-LLM deterministic math check ensuring absolute financial integrity."""
    calculated_subtotal = round(sum(item.amount for item in line_items), 2)
    reasons: List[str] = []

    # 1. Verify line item sum matches reported subtotal
    if reported_subtotal is not None:
        if abs(calculated_subtotal - reported_subtotal) > tolerance:
            reasons.append(
                f"Line items sum ({calculated_subtotal:.2f}) does not match reported subtotal ({reported_subtotal:.2f})."
            )

    # 2. Verify subtotal + tax equals grand total
    effective_subtotal = reported_subtotal if reported_subtotal is not None else calculated_subtotal
    if reported_total is not None:
        tax_amount = reported_tax if reported_tax is not None else 0.0
        expected_total = round(effective_subtotal + tax_amount, 2)
        if abs(expected_total - reported_total) > tolerance:
            reasons.append(
                f"Subtotal ({effective_subtotal:.2f}) + Tax ({tax_amount:.2f}) != Total ({reported_total:.2f})."
            )

    # 3. Check for empty charge lines
    if not line_items:
        reasons.append("Zero charge lines were extracted.")

    needs_review = len(reasons) > 0

    return MathValidationResult(
        is_valid=not needs_review,
        needs_review=needs_review,
        calculated_subtotal=calculated_subtotal,
        reported_subtotal=reported_subtotal,
        reported_tax=reported_tax,
        reported_total=reported_total,
        discrepancy_reasons=reasons,
    )
