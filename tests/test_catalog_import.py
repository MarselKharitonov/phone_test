import sqlite3
import unittest
from pathlib import Path
from stylist.catalog import connect
from stylist.catalog_import import import_products
from server.catalog_api import recommend_product


class CatalogImportTests(unittest.TestCase):
    def setUp(self):
        self.db = connect(Path(":memory:"))
        self.addCleanup(self.db.close)
        self.product = {"source": "manual", "external_id": "1", "title": "Shirt", "category": "tops",
                        "updated_at": "2026-11-19", "variants": [
                            {"size_label": "M", "stock_status": "available", "observed_at": "2026-11-19",
                             "measurements": [{"dimension": "chest", "type": "body", "min_cm": 95,
                                               "max_cm": 100, "source_url": "https://example.com/chart"}]}]}

    def test_import_and_match(self):
        self.assertEqual(import_products(self.db, [self.product]), 1)
        self.assertEqual(recommend_product(self.db, 1, {"chest": 98}, ["chest"])["size"], "M")

    def test_atomic_on_invalid_data(self):
        with self.assertRaises((ValueError, sqlite3.IntegrityError)):
            import_products(self.db, [self.product, {"source": "bad"}])
        self.assertEqual(self.db.execute("SELECT count(*) FROM products").fetchone()[0], 0)

    def test_import_twice_does_not_duplicate(self):
        import_products(self.db, [self.product])
        import_products(self.db, [self.product])
        self.assertEqual(self.db.execute("SELECT count(*) FROM variants").fetchone()[0], 1)
