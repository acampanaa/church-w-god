import unittest

from church_horror.config import Settings
from church_horror.maze import Maze
from church_horror.navigation import Navigator


class NavigationTests(unittest.TestCase):
    def test_automatic_tour_stays_inside_maze(self):
        maze = Maze.generate(7, 7, seed=95)
        navigator = Navigator(maze, Settings())
        for _ in range(2000):
            navigator.update_auto(0.05)
            camera = navigator.camera
            self.assertGreaterEqual(camera.x, 0.5)
            self.assertGreaterEqual(camera.z, 0.5)
            self.assertLessEqual(camera.x, maze.width - 0.5)
            self.assertLessEqual(camera.z, maze.height - 0.5)

    def test_manual_motion_stops_at_outer_wall(self):
        maze = Maze.generate(5, 5, seed=95)
        navigator = Navigator(maze, Settings())
        navigator.toggle_auto()
        navigator.camera.x = 0.5
        navigator.camera.z = 0.5
        navigator.camera.yaw = 0.0
        for _ in range(20):
            navigator.update_manual(0.05, 1, 0, 0)
        self.assertAlmostEqual(navigator.camera.z, 0.16)


if __name__ == "__main__":
    unittest.main()
