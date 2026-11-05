import math
import unittest

from liminal_chill import math3d


class MatrixTests(unittest.TestCase):
    def test_identity_and_translation(self):
        matrix = math3d.translation(2, 3, 4)
        self.assertEqual(math3d.multiply(math3d.identity(), matrix), matrix)
        self.assertEqual(math3d.column_major(matrix)[12:15], (2, 3, 4))

    def test_view_faces_east_after_quarter_turn(self):
        matrix = math3d.view(0, 1.65, 0, math.pi / 2, 0)
        point = (1, 1.65, 0, 1)
        result = tuple(sum(matrix[row * 4 + col] * point[col] for col in range(4))
                       for row in range(4))
        self.assertAlmostEqual(result[0], 0, places=6)
        self.assertAlmostEqual(result[1], 0, places=6)
        self.assertAlmostEqual(result[2], -1, places=6)


if __name__ == "__main__":
    unittest.main()
