"""Import a user-prepared JSON catalog transactionally; no network requests."""
import argparse
import json
from pathlib import Path
from stylist.catalog import connect


def import_products(db, products):
    if not isinstance(products, list):
        raise ValueError("Expected a list of products")
    count = 0
    with db:
        for p in products:
            if not all(isinstance(p.get(k), str) and p[k].strip()
                       for k in ("source", "external_id", "title", "category", "updated_at")):
                raise ValueError("Missing product fields")
            cursor = db.execute(
                """INSERT INTO products(source,external_id,title,category,price_minor,currency,
                   product_url,image_path,image_use,rights_note,updated_at)
                   VALUES(?,?,?,?,?,?,?,?,?,?,?)
                   ON CONFLICT(source,external_id) DO UPDATE SET title=excluded.title,
                   category=excluded.category,price_minor=excluded.price_minor,currency=excluded.currency,
                   product_url=excluded.product_url,image_path=excluded.image_path,
                   image_use=excluded.image_use,rights_note=excluded.rights_note,updated_at=excluded.updated_at""",
                (p["source"], p["external_id"], p["title"], p["category"], p.get("price_minor"),
                 p.get("currency"), p.get("product_url"), p.get("image_path"),
                 p.get("image_use", "unverified"), p.get("rights_note", ""), p["updated_at"]),
            )
            row = db.execute("SELECT id FROM products WHERE source=? AND external_id=?",
                             (p["source"], p["external_id"])).fetchone()
            product_id = row["id"]
            # Update size rows only when explicitly supplied; an empty list clears them.
            if "variants" in p:
                ids = [r["id"] for r in db.execute("SELECT id FROM variants WHERE product_id=?", (product_id,))]
                for variant_id in ids:
                    db.execute("DELETE FROM size_measurements WHERE variant_id=?", (variant_id,))
                db.execute("DELETE FROM variants WHERE product_id=?", (product_id,))
                for variant in p["variants"]:
                    cur = db.execute(
                        "INSERT INTO variants(product_id,size_label,stock_status,variant_url,observed_at) VALUES(?,?,?,?,?)",
                        (product_id, variant["size_label"], variant["stock_status"],
                         variant.get("variant_url"), variant["observed_at"]))
                    for m in variant.get("measurements", []):
                        db.execute(
                            "INSERT INTO size_measurements(variant_id,dimension,measurement_type,min_cm,max_cm,source_url) VALUES(?,?,?,?,?,?)",
                            (cur.lastrowid, m["dimension"], m["type"], m["min_cm"], m["max_cm"], m["source_url"]))
            count += 1
    return count


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    parser.add_argument("--db", required=True, type=Path)
    args = parser.parse_args()
    with args.input.open(encoding="utf-8") as source:
        products = json.load(source)
    with connect(args.db) as db:
        print(f"Imported {import_products(db, products)} products.")


if __name__ == "__main__":
    main()
