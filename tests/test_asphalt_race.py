import unittest

from games import sound
from games.asphalt_race import AsphaltRace


class _StubGrid:
    grid_size = 19

    def clear(self, *args, **kwargs):
        pass

    def render_text(self, *args, **kwargs):
        pass

    def render_number(self, *args, **kwargs):
        pass

    def set_pixel(self, *args, **kwargs):
        pass


class TestAsphaltRace(unittest.TestCase):
    def setUp(self):
        sound.set_enabled(False)

    def test_road_width_increases_towards_bottom(self):
        g = _StubGrid()
        game = AsphaltRace(g)

        w_horizon = game._road_half_width(game.horizon_y)
        w_bottom = game._road_half_width(g.grid_size - 1)
        self.assertLessEqual(w_horizon, w_bottom)
        self.assertGreaterEqual(w_horizon, 2)

    def test_collision_detects_overlap_near_player(self):
        g = _StubGrid()
        game = AsphaltRace(g)

        px, py = game._player_pos()
        # Place a traffic car overlapping the player's position.
        # Compute traffic offset relative to road center at that y.
        car_x_offset = float(px - game._road_center_at(py))
        game.traffic = [{"x": car_x_offset, "y": float(py), "passed": False}]

        self.assertTrue(game._check_collision())


if __name__ == "__main__":
    unittest.main()
