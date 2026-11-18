import unittest
from pathlib import Path
from stylist.catalog import can_try_on, connect, list_products


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(Path(":memory:"))
        self.addCleanup(self.db.close)

    def test_no_fabricated_products(self):
        self.assertEqual(list_products(self.db), [])

    def test_unverified_asset_is_not_eligible(self):
        self.assertFalse(can_try_on({"image_path": "x.png", "image_use": "unverified"}))
        self.assertFalse(can_try_on({"image_path": "", "image_use": "test_authorized"}))
        self.assertTrue(can_try_on({"image_path": "x.png", "image_use": "test_authorized"}))

    def test_category_filter(self):
        self.db.execute(
            "INSERT INTO products(source,external_id,title,category,image_use,updated_at) VALUES(?,?,?,?,?,?)",
            ("test", "1", "Test shirt", "tops", "unverified", "2026-11-18"),
        )
        self.assertEqual(len(list_products(self.db, "tops")), 1)
        self.assertEqual(len(list_products(self.db, "shoes")), 0)


if __name__ == "__main__":
    unittest.main()
