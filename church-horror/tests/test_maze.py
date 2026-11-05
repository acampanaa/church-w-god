import unittest

from church_horror.maze import DELTAS, Maze


class MazeTests(unittest.TestCase):
    def test_generated_maze_is_connected_and_symmetric(self):
        for seed in range(10):
            maze = Maze.generate(13, 13, seed)
            self.assertEqual(maze.reachable_count(), 169)
            for z in range(maze.height):
                for x in range(maze.width):
                    for direction, (dx, dz) in enumerate(DELTAS):
                        nx, nz = x + dx, z + dz
                        if maze.contains(nx, nz):
                            self.assertEqual(
                                maze.has_wall(x, z, direction),
                                maze.has_wall(nx, nz, (direction + 2) % 4),
                            )
                        else:
                            self.assertTrue(maze.has_wall(x, z, direction))

    def test_seed_repeats_the_same_maze(self):
        self.assertEqual(Maze.generate(8, 8, 95).walls, Maze.generate(8, 8, 95).walls)


if __name__ == "__main__":
    unittest.main()
