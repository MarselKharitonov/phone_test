from stylist.sizing import recommend


def recommend_product(db, product_id, body, required):
    variants = []
    for v in db.execute("SELECT * FROM variants WHERE product_id=?", (product_id,)):
        measurements = {}
        for m in db.execute("SELECT * FROM size_measurements WHERE variant_id=?", (v["id"],)):
            if m["measurement_type"] == "body":
                measurements[m["dimension"]] = {
                    "type": "body", "min_cm": m["min_cm"], "max_cm": m["max_cm"]
                }
        variants.append({"size_label": v["size_label"], "stock_status": v["stock_status"],
                         "measurements": measurements})
    return recommend(variants, body, required)
