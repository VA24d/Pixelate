import unittest

from games import sound
from games.basketball import Basketball


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


class TestBasketball(unittest.TestCase):
    def setUp(self):
        sound.set_enabled(False)

    def test_shot_probability_decreases_with_distance(self):
        g = _StubGrid()
        game = Basketball(g)
        game.game_started = True

        # shooter near right hoop
        game.team1[0]["x"] = 14.0
        game.team1[0]["y"] = float(game.right_hoop_y)
        p_close = game._shot_probability(0, game.right_hoop_x, game.right_hoop_y)

        # shooter far from hoop
        game.team1[0]["x"] = 3.0
        game.team1[0]["y"] = 3.0
        p_far = game._shot_probability(0, game.right_hoop_x, game.right_hoop_y)

        self.assertGreater(p_close, p_far)


if __name__ == "__main__":
    unittest.main()
