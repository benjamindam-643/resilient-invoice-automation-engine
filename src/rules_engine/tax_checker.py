"""Tax (GST/VAT) Compliance & Spending Limit Rule Engine.

Validates statutory tax rates (e.g. 10% or 15% GST) and enforces operational
purchase order expenditure limits before dispatching for approval.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ComplianceResult:
    is_compliant: bool
    gst_error: bool
    over_limit: bool
    expected_tax: float
    reported_tax: float
    variance: float
    flags: List[str]


def verify_tax_compliance(
    subtotal: float,
    reported_tax: float,
    expected_tax_rate: float = 0.10,  # e.g., 10% GST in AU or 15% in NZ
    spending_limit: Optional[float] = 5000.0,
    tolerance: float = 0.05,
) -> ComplianceResult:
    """Verifies calculated tax against reported tax and checks policy ceilings."""
    expected_tax = round(subtotal * expected_tax_rate, 2)
    variance = round(abs(expected_tax - reported_tax), 2)
    flags: List[str] = []

    gst_error = variance > tolerance
    if gst_error:
        flags.append(
            f"GST discrepancy detected: reported ${reported_tax:.2f}, expected ${expected_tax:.2f} (diff ${variance:.2f})."
        )

    over_limit = False
    total = subtotal + reported_tax
    if spending_limit is not None and total > spending_limit:
        over_limit = True
        flags.append(f"Spending limit exceeded: total ${total:.2f} > limit ${spending_limit:.2f}.")

    is_compliant = not gst_error and not over_limit

    return ComplianceResult(
        is_compliant=is_compliant,
        gst_error=gst_error,
        over_limit=over_limit,
        expected_tax=expected_tax,
        reported_tax=reported_tax,
        variance=variance,
        flags=flags,
    )
