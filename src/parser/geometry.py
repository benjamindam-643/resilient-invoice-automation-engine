"""Geometric Word Clustering & Line Assembly Engine.

Groups OCR words with bounding boxes (x0, y0, x1, y1) into coherent horizontal text
lines using dynamic vertical overlap thresholds without hardcoded per-receipt rules.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List, Sequence


@dataclass
class WordBox:
    text: str
    x0: float
    y0: float
    x1: float
    y1: float
    confidence: float = 1.0

    @property
    def height(self) -> float:
        return max(1.0, self.y1 - self.y0)

    @property
    def center_y(self) -> float:
        return (self.y0 + self.y1) / 2.0


@dataclass
class TextLine:
    words: List[WordBox]
    y0: float
    y1: float

    @property
    def text(self) -> str:
        return " ".join(w.text for w in sorted(self.words, key=lambda w: w.x0))

    @property
    def x0(self) -> float:
        return min(w.x0 for w in self.words) if self.words else 0.0

    @property
    def x1(self) -> float:
        return max(w.x1 for w in self.words) if self.words else 0.0


def cluster_words_into_lines(words: Sequence[WordBox], y_overlap_ratio: float = 0.5) -> List[TextLine]:
    """Clusters bounding box words into ordered text lines based on dynamic vertical overlap."""
    if not words:
        return []

    # Sort words primarily from top to bottom, secondarily left to right
    sorted_words = sorted(words, key=lambda w: (w.y0, w.x0))
    lines: List[TextLine] = []

    for word in sorted_words:
        assigned = False
        for line in lines:
            # Calculate vertical overlap between current word and existing line
            overlap_y0 = max(word.y0, line.y0)
            overlap_y1 = min(word.y1, line.y1)
            overlap_height = max(0.0, overlap_y1 - overlap_y0)

            min_height = min(word.height, line.y1 - line.y0)
            if min_height > 0 and (overlap_height / min_height) >= y_overlap_ratio:
                line.words.append(word)
                line.y0 = min(line.y0, word.y0)
                line.y1 = max(line.y1, word.y1)
                assigned = True
                break

        if not assigned:
            lines.append(TextLine(words=[word], y0=word.y0, y1=word.y1))

    # Sort lines vertically from top to bottom
    lines.sort(key=lambda line: line.y0)
    return lines
