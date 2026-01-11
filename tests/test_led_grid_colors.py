import unittest


from led_grid import LEDGrid


class _DummySurface:
    pass


class TestLEDGridColors(unittest.TestCase):
    def test_coerce_color_clamps_and_rounds(self):
        grid = LEDGrid(100, 100)
        # floats, negatives, and >255 should be coerced
        grid.set_pixel(0, 0, (12.7, -5, 9999))
        self.assertEqual(grid.get_pixel(0, 0), (13, 0, 255))

        # invalid shape should become black
        grid.set_pixel(1, 0, 123)  # type: ignore[arg-type]
        self.assertEqual(grid.get_pixel(1, 0), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
