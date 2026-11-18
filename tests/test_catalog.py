import sqlite3
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

    def test_variant_measurements_and_source(self):
        product = self.db.execute(
            "INSERT INTO products(source,external_id,title,category,image_use,updated_at) VALUES(?,?,?,?,?,?)",
            ("test", "2", "Test trousers", "bottoms", "unverified", "2026-11-18"),
        ).lastrowid
        variant = self.db.execute(
            "INSERT INTO variants(product_id,size_label,stock_status,variant_url,observed_at) VALUES(?,?,?,?,?)",
            (product, "M", "available", None, "2026-11-18"),
        ).lastrowid
        self.db.execute(
            "INSERT INTO size_measurements(variant_id,dimension,measurement_type,min_cm,max_cm,source_url) VALUES(?,?,?,?,?,?)",
            (variant, "waist", "body", 80, 84, "https://example.com/chart"),
        )
        self.assertEqual(self.db.execute("SELECT count(*) FROM size_measurements").fetchone()[0], 1)

    def test_orphan_variant_rejected(self):
        with self.assertRaises(sqlite3.IntegrityError):
            self.db.execute(
                "INSERT INTO variants(product_id,size_label,stock_status,observed_at) VALUES(?,?,?,?)",
                (999, "M", "available", "2026-11-18"),
            )


if __name__ == "__main__":
    unittest.main()
