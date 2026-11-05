import unittest

from church_horror.church_world import ChurchNavigator, ChurchWorld


class ChurchWorldTests(unittest.TestCase):
    def test_entrance_and_center_aisle_are_walkable(self):
        world = ChurchWorld()
        self.assertTrue(world.can_stand(0, 24))
        self.assertTrue(world.can_stand(0, 5))
        self.assertTrue(world.can_stand(0, 3.8))

    def test_walls_columns_and_iconostasis_block_movement(self):
        world = ChurchWorld()
        self.assertFalse(world.can_stand(7, 15))
        self.assertFalse(world.can_stand(-4.6, 12))
        self.assertFalse(world.can_stand(3, 3.8))

    def test_camera_can_walk_to_sanctuary_through_center_gap(self):
        world = ChurchWorld()
        navigator = ChurchNavigator(world)
        for _ in range(175):
            navigator.move(0.05, forward=1, strafe=0)
        self.assertLess(navigator.camera.z, 3.5)
        self.assertTrue(world.can_stand(navigator.camera.x, navigator.camera.z))

    def test_camera_stops_at_outer_wall(self):
        navigator = ChurchNavigator(ChurchWorld())
        navigator.camera.yaw = 1.5707963267948966
        for _ in range(100):
            navigator.move(0.05, forward=1, strafe=0)
        self.assertLessEqual(navigator.camera.x, 6.75)

    def test_jump_rises_and_lands_without_double_jump(self):
        navigator = ChurchNavigator(ChurchWorld())
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
