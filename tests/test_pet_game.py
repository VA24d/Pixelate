import unittest

from games.pet_game import PetGame


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


class TestPetGame(unittest.TestCase):
    def test_stats_decay_over_time(self):
        g = _StubGrid()
        game = PetGame(g)
        pet = game.pets[game.selected_index]
        h0, hap0, e0 = pet.hunger, pet.happiness, pet.energy

        game.update(1.0)

        self.assertLess(pet.hunger, h0)
        self.assertLess(pet.happiness, hap0)
        self.assertLess(pet.energy, e0)

    def test_stats_clamp_after_actions(self):
        g = _StubGrid()
        game = PetGame(g)

        for _ in range(50):
            game._rest()
            game._feed()
            game._play()

        pet = game.pets[game.selected_index]
        for v in (pet.hunger, pet.happiness, pet.energy):
            self.assertGreaterEqual(v, 0.0)
            self.assertLessEqual(v, 10.0)


if __name__ == "__main__":
    unittest.main()
