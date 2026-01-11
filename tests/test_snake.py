import unittest

from games import sound
from games.snake import Snake


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


class TestSnake(unittest.TestCase):
    def setUp(self):
        # Ensure unit tests never try to initialize pygame.mixer.
        sound.set_enabled(False)

    def test_prevent_immediate_reverse(self):
        g = _StubGrid()
        game = Snake(g)
        self.assertEqual(game.direction, (1, 0))
        self.assertEqual(game.next_direction, (1, 0))

        # Attempt to reverse from RIGHT to LEFT should be ignored.
        game._set_next_dir((-1, 0))
        self.assertEqual(game.next_direction, (1, 0))

    def test_step_moves_head_and_keeps_length_without_food(self):
        g = _StubGrid()
        game = Snake(g)

        initial_len = len(game.snake)
        old_head = game.snake[-1]

        # Put food far away so we don't grow.
        game.food = (0, 0)
        game._step()

        new_head = game.snake[-1]
        self.assertEqual(len(game.snake), initial_len)
        self.assertEqual(new_head, (old_head[0] + 1, old_head[1]))
        self.assertFalse(game.game_over)

    def test_spawn_food_never_on_snake(self):
        g = _StubGrid()
        game = Snake(g)

        for _ in range(50):
            game._spawn_food()
            self.assertNotIn(game.food, game.snake)

    def test_wall_collision_sets_game_over(self):
        g = _StubGrid()
        game = Snake(g)

        # Place head at right edge and move right.
        game.snake.clear()
        game.snake.extend([(17, 10), (18, 10)])
        game.direction = (1, 0)
        game.next_direction = (1, 0)

        game._step()
        self.assertTrue(game.game_over)


if __name__ == "__main__":
    unittest.main()
