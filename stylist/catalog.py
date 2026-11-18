"""Local experimental catalog. No network, scraper, or fabricated inventory."""
import sqlite3
from pathlib import Path


SCHEMA = """
CREATE TABLE IF NOT EXISTS products (
    id INTEGER PRIMARY KEY,
    source TEXT NOT NULL,
    external_id TEXT NOT NULL,
    title TEXT NOT NULL,
    category TEXT NOT NULL CHECK (category IN ('tops', 'bottoms', 'shoes', 'headwear', 'one-pieces', 'accessories')),
    price_minor INTEGER CHECK (price_minor IS NULL OR price_minor >= 0),
    currency TEXT,
    product_url TEXT,
    image_path TEXT,
    image_use TEXT NOT NULL CHECK (image_use IN ('unverified', 'test_authorized', 'commercial_authorized')),
    rights_note TEXT NOT NULL DEFAULT '',
    updated_at TEXT NOT NULL,
    UNIQUE(source, external_id)
);
"""


def connect(path: Path) -> sqlite3.Connection:
    db = sqlite3.connect(path)
    db.row_factory = sqlite3.Row
    db.executescript(SCHEMA)
    return db


def list_products(db: sqlite3.Connection, category: str | None = None) -> list[dict]:
    sql = "SELECT * FROM products"
    params = ()
    if category:
        sql += " WHERE category = ?"
        params = (category,)
    return [dict(row) for row in db.execute(sql + " ORDER BY id", params)]


def can_try_on(product: dict) -> bool:
    """Test authorization is not commercial authorization."""
    return bool(product.get("image_path")) and product.get("image_use") in {
        "test_authorized", "commercial_authorized"
    }
