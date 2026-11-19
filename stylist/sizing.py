"""Conservative body-measurement matching; no invented garment allowances."""


def recommend(variants, measurements, required):
    if not required or any(not isinstance(measurements.get(k), (int, float))
                           or measurements[k] <= 0 for k in required):
        return {"status": "insufficient_data", "size": None}
    candidates = []
    incomplete = False
    for variant in variants:
        if variant.get("stock_status") != "available":
            continue
        charts = variant.get("measurements", {})
        if any(k not in charts or charts[k].get("type") != "body" for k in required):
            incomplete = True
            continue
        if all(charts[k]["min_cm"] <= measurements[k] <= charts[k]["max_cm"] for k in required):
            candidates.append(variant["size_label"])
    if len(candidates) == 1 and not incomplete:
        return {"status": "matched", "size": candidates[0], "confidence": "uncalibrated"}
    if candidates:
        return {"status": "ambiguous", "size": None, "candidates": candidates}
    return {"status": "insufficient_data" if incomplete else "no_match", "size": None}
