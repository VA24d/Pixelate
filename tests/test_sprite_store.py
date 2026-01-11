import tempfile
import unittest

from games.sprite_store import SpriteStore


class TestSpriteStore(unittest.TestCase):
    def test_roundtrip_save_load(self):
        with tempfile.TemporaryDirectory() as td:
            path = f"{td}/sprites.json"
            store = SpriteStore(path=path)
            s = store.get_or_create("test", w=3, h=3)
            s.set(1, 1, (10, 20, 30))
            store.save()

            store2 = SpriteStore(path=path)
            store2.load()
            s2 = store2.get("test")
            self.assertIsNotNone(s2)
            self.assertEqual(s2.w, 3)
            self.assertEqual(s2.h, 3)
            self.assertEqual(s2.get(1, 1), (10, 20, 30))


if __name__ == "__main__":
    unittest.main()
