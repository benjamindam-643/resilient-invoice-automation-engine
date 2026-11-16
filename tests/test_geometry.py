import unittest
from src.parser.geometry import WordBox, cluster_words_into_lines


class TestGeometryClustering(unittest.TestCase):
    def test_cluster_words_same_horizontal_line(self):
        # 3 words on the same line (y0 around 100, y1 around 112)
        w1 = WordBox("INVOICE", 10.0, 100.0, 60.0, 112.0)
        w2 = WordBox("#10492", 65.0, 100.5, 110.0, 112.2)
        w3 = WordBox("TOTAL", 200.0, 101.0, 240.0, 112.5)

        lines = cluster_words_into_lines([w3, w1, w2])  # Pass in scrambled order
        self.assertEqual(len(lines), 1)
        self.assertEqual(lines[0].text, "INVOICE #10492 TOTAL")

    def test_cluster_distinct_vertical_lines(self):
        w1 = WordBox("Line 1", 10.0, 50.0, 50.0, 62.0)
        w2 = WordBox("Line 2", 10.0, 80.0, 50.0, 92.0)

        lines = cluster_words_into_lines([w2, w1])
        self.assertEqual(len(lines), 2)
        self.assertEqual(lines[0].text, "Line 1")
        self.assertEqual(lines[1].text, "Line 2")


if __name__ == "__main__":
    unittest.main()
