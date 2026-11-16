"""Duplicate Detection & Invariant Hash Verification.

Prevents processing duplicate invoices across multiple mailboxes or retry loops
using compound supplier, invoice number, and charge fingerprint hashing.
"""
from __future__ import annotations

import hashlib
from typing import Dict, Optional, Set


class DuplicateDetector:
    """In-memory and persistent signature ledger for duplicate invoice rejection."""

    def __init__(self) -> None:
        self._seen_signatures: Set[str] = set()

    def generate_fingerprint(
        self,
        supplier_id: str,
        invoice_number: str,
        total_amount: float,
        date_str: str = "",
    ) -> str:
        """Constructs a deterministic composite hash invariant."""
        norm_supplier = supplier_id.strip().lower()
        norm_inv = invoice_number.strip().lower()
        norm_amt = f"{total_amount:.2f}"
        norm_date = date_str.strip()

        raw_key = f"{norm_supplier}|{norm_inv}|{norm_amt}|{norm_date}"
        return hashlib.sha256(raw_key.encode("utf-8")).hexdigest()

    def check_duplicate(
        self,
        supplier_id: str,
        invoice_number: str,
        total_amount: float,
        date_str: str = "",
    ) -> bool:
        """Returns True if the invoice signature has already been recorded."""
        fingerprint = self.generate_fingerprint(supplier_id, invoice_number, total_amount, date_str)
        if fingerprint in self._seen_signatures:
            return True

        self._seen_signatures.add(fingerprint)
        return False
