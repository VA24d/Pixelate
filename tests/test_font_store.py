import tempfile
import unittest


from games.font_store import FontStore


class TestFontStore(unittest.TestCase):
    def test_roundtrip_save_load(self):
        with tempfile.TemporaryDirectory() as td:
            path = f"{td}/font_overrides.json"
            store = FontStore(path=path)
            store.set_glyph("A", [[1, 0, 1], [0, 1, 0], [1, 1, 1], [0, 1, 0], [1, 0, 1]])
            store.save()

            store2 = FontStore(path=path)
            store2.load()
            g = store2.get_glyph("a")
            self.assertIsNotNone(g)
            self.assertEqual(len(g), 5)
            self.assertEqual(len(g[0]), 3)
            self.assertEqual(g[0], [1, 0, 1])


if __name__ == "__main__":
    unittest.main()
