import unittest


from led_grid import LEDGrid


class TestLEDGridFontOverrides(unittest.TestCase):
    def test_render_text_uses_overrides(self):
        grid = LEDGrid(100, 100)

        # Define a custom glyph for 'A' that only lights the center pixel on the first row.
        overrides = {
            "A": [
                [0, 1, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
                [0, 0, 0],
            ]
        }
        grid.set_font_overrides(overrides)

        grid.clear((0, 0, 0))
        grid.render_text("A", 0, 0, (9, 8, 7), scale=1)

        # Only (1,0) should be set to the color.
        self.assertEqual(grid.get_pixel(1, 0), (9, 8, 7))
        self.assertEqual(grid.get_pixel(0, 0), (0, 0, 0))
        self.assertEqual(grid.get_pixel(2, 0), (0, 0, 0))


if __name__ == "__main__":
    unittest.main()
