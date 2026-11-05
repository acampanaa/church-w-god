import math
import unittest

from liminal_chill.world import LiminalWorld, Navigator


class WorldTests(unittest.TestCase):
    def test_doorways_and_pool_walkways_are_open(self):
        world = LiminalWorld()
        self.assertTrue(world.can_stand(0, 22))
        self.assertTrue(world.can_stand(0, 10))
        self.assertTrue(world.can_stand(-5, 16))
        self.assertTrue(world.can_stand(5, 16))

    def test_pool_partitions_and_columns_block_player(self):
        world = LiminalWorld()
        self.assertFalse(world.can_stand(0, 16))
        self.assertFalse(world.can_stand(5, 22))
        self.assertFalse(world.can_stand(-6.8, 27))

    def test_player_stops_at_pool_and_outer_wall(self):
        navigator = Navigator(LiminalWorld())
        for _ in range(300):
            navigator.move(0.05, 1, 0)
        self.assertGreaterEqual(navigator.camera.z, 19.5)
        navigator.camera.yaw = math.pi / 2
        for _ in range(300):
            navigator.move(0.05, 1, 0)
        self.assertLessEqual(navigator.camera.x, 9 - navigator.world.player_radius)

    def test_jump_rises_and_lands_without_double_jump(self):
        navigator = Navigator(LiminalWorld())
        navigator.jump()
        navigator.update_vertical(0.05)
        self.assertGreater(navigator.camera.jump_height, 0)
        velocity = navigator.vertical_velocity
        navigator.jump()
        self.assertEqual(navigator.vertical_velocity, velocity)
        for _ in range(40):
            navigator.update_vertical(0.05)
        self.assertEqual(navigator.camera.jump_height, 0)
        self.assertEqual(navigator.vertical_velocity, 0)
        navigator.jump()
        self.assertGreater(navigator.vertical_velocity, 0)


if __name__ == "__main__":
    unittest.main()
