import unittest

from church_horror.graphics import MeshBuilder


class MeshTests(unittest.TestCase):
    def test_quad_is_two_triangles_with_interleaved_attributes(self):
        mesh = MeshBuilder()
        mesh.quad(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), "stone")
        self.assertEqual(len(mesh.batches["stone"]), 6 * 11)

    def test_materials_get_separate_draw_ranges(self):
        mesh = MeshBuilder()
        mesh.quad(((0, 0, 0), (1, 0, 0), (1, 1, 0), (0, 1, 0)), "stone")
        mesh.triangle(((0, 0, 0), (0, 1, 0), (1, 0, 0)), "solid")
        self.assertEqual(set(mesh.batches), {"stone", "solid"})
        self.assertEqual(len(mesh.batches["solid"]), 3 * 11)


if __name__ == "__main__":
    unittest.main()
