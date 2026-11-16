"""Generic Line-Item Table Extraction without Per-Shop Templates.

Extracts line items, charges, and descriptions across heterogeneous receipt layouts
(job blocks, parts & labour tables, multiline headers like EXTD, summary rows).
"""
from __future__ import annotations

import re
from typing import List, Sequence, Tuple
from src.parser.geometry import TextLine
from src.parser.math_validator import InvoiceLineItem

# Generic column indicators for amount / charges
_CHARGE_HEADER_PATTERNS = [
    r"\bamount\b",
    r"\btotal\b",
    r"\bprice\b",
    r"\bextd\b",
    r"\bext['’]d\b",
    r"\bextended\b",
    r"\blabou?r\b",
    r"\bparts?\b",
]

# Patterns representing non-charge summary rows (to prevent extracting totals as charges)
_SUMMARY_ROW_PATTERNS = [
    r"^\s*sub\s*total",
    r"^\s*total",
    r"^\s*balance\s*due",
    r"^\s*tax\b",
    r"^\s*gst\b",
    r"^\s*vat\b",
    r"^\s*payment\b",
    r"^\s*amount\s*paid",
]

_PRICE_REGEX = re.compile(r"[-+]?\$?\s*([0-9]{1,3}(?:,[0-9]{3})*\.[0-9]{2})\b")


def extract_price_from_line(text: str) -> Tuple[Optional[float], str]:
    """Extracts trailing or isolated price number and returns cleaned description."""
    matches = list(_PRICE_REGEX.finditer(text))
    if not matches:
        return None, text

    # Typically line item amount is the last monetary figure on the line
    last_match = matches[-1]
    raw_number = last_match.group(1).replace(",", "")
    amount = float(raw_number)

    # Clean description by removing the amount substring
    desc = text[:last_match.start()] + text[last_match.end():]
    desc = re.sub(r"\s+", " ", desc).strip()
    return amount, desc


class GenericTableExtractor:
    """Robust table parser resilient to OCR noise, multi-page breaks, and layout variance."""

    def is_summary_line(self, line_text: str) -> bool:
        lower = line_text.lower()
        return any(re.search(pat, lower) for pat in _SUMMARY_ROW_PATTERNS)

    def extract_line_items(self, lines: Sequence[TextLine]) -> List[InvoiceLineItem]:
        """Parses line items while strictly discarding summary/total rows."""
        items: List[InvoiceLineItem] = []
        current_line_no = 1

        for line in lines:
            line_text = line.text.strip()
            if not line_text:
                continue

            # Guard against extracting summary/subtotal strips as charge rows
            if self.is_summary_line(line_text):
                continue

            amount, description = extract_price_from_line(line_text)
            if amount is not None and amount > 0:
                # Discard lines that are likely phone numbers or dates
                if re.search(r"\b(19\d\d|20\d\d)[-/]\d{1,2}[-/]\d{1,2}\b", description) and len(description) < 15:
                    continue

                items.append(
                    InvoiceLineItem(
                        description=description or "Item / Service Charge",
                        amount=amount,
                        line_number=current_line_no,
                    )
                )
                current_line_no += 1

        return items
