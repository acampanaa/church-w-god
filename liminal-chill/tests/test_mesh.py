import unittest

from liminal_chill.graphics import MeshBuilder


class MeshTests(unittest.TestCase):
    def test_quad_is_two_triangles_with_interleaved_attributes(self):
        mesh = MeshBuilder()
        mesh.quad(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), "tile")
        self.assertEqual(len(mesh.batches["tile"]), 6 * 11)

    def test_materials_get_separate_draw_ranges(self):
        mesh = MeshBuilder()
        mesh.quad(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), "tile")
        mesh.triangle(((0, 0, 0), (0, 1, 0), (1, 0, 0)), "solid")
        self.assertEqual(set(mesh.batches), {"tile", "solid"})
        self.assertEqual(len(mesh.batches["solid"]), 3 * 11)


if __name__ == "__main__":
    unittest.main()
