import unittest

from games import sound
from games.flappy import Flappy


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


class TestFlappy(unittest.TestCase):
    def setUp(self):
        sound.set_enabled(False)

    def test_flap_sets_negative_velocity(self):
        g = _StubGrid()
        game = Flappy(g)

        game.bird_vy = 1.0
        game.bird_vy = game.flap_velocity
        self.assertLess(game.bird_vy, 0.0)

    def test_score_increments_after_passing_pipe(self):
        g = _StubGrid()
        game = Flappy(g)

        # Force a single pipe just behind the bird so update() counts it as passed.
        pipe = {"x": float(game.bird_x) - 0.1, "gap": 9}
        game.pipes = [pipe]
        game._passed = set()

        s0 = game.score
        game.update(0.0)
        self.assertEqual(game.score, s0 + 1)

        # Calling update again should NOT increment again (pipe already in _passed).
        game.update(0.0)
        self.assertEqual(game.score, s0 + 1)

    def test_pipe_collision_sets_game_over(self):
        g = _StubGrid()
        game = Flappy(g)

        # Put bird at a y that will collide with the pipe gap.
        game.bird_y = 0.0
        game.bird_vy = 0.0

        # Create a pipe aligned with bird_x and with a gap far away.
        game.pipes = [{"x": float(game.bird_x), "gap": 15}]
        game.update(0.0)

        self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()
