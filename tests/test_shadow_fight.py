import unittest

from games import sound
from games.shadow_fight import ShadowFight


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


class TestShadowFight(unittest.TestCase):
    def setUp(self):
        sound.set_enabled(False)

    def test_p1_punch_reduces_ai_hp_when_in_range(self):
        g = _StubGrid()
        game = ShadowFight(g)

        # Put fighters close enough to hit.
        game.p1_x = 8.0
        game.ai_x = 9.0
        game.p1_y = float(game.ground_y)
        game.ai_y = float(game.ground_y)

        hp0 = game.ai_hp
        game.p1_attack_timer = 0.18
        game._resolve_hits()

        self.assertEqual(game.ai_hp, hp0 - 1)
        self.assertEqual(game.p1_attack_timer, 0.0)

    def test_game_over_and_winner_when_hp_reaches_zero(self):
        g = _StubGrid()
        game = ShadowFight(g)

        game.ai_hp = 1
        game.p1_x = 8.0
        game.ai_x = 9.0
        game.p1_attack_timer = 0.18

        game.update(0.0)
        self.assertTrue(game.game_over)
        self.assertEqual(game.winner, "YOU")


if __name__ == "__main__":
    unittest.main()
