"""Private, manual Kaggle experiment. Not an online service or production pipeline.

Run after installing the dependencies and weights as documented in README.md.
"""
import argparse
import json
import time
from pathlib import Path


def validate(category: str, frame: str) -> None:
    if category not in {"tops", "bottoms", "one-pieces"}:
        raise ValueError("Unsupported category")
    if frame not in {"shoulders", "waist", "full"}:
        raise ValueError("Unsupported frame")
    if frame != "full" and category != "tops":
        raise ValueError("Partial frames only permit visible upper garments")


def run(person_path: Path, garment_path: Path, weights_path: Path, output_dir: Path,
        category: str, frame: str) -> None:
    validate(category, frame)
    if not person_path.is_file() or not garment_path.is_file():
        raise FileNotFoundError("Both input images are required")
    if not weights_path.is_dir():
        raise FileNotFoundError("Weights directory not found")
    if not output_dir.is_dir():
        raise FileNotFoundError("Output directory must already exist")
    output = output_dir / "result.png"
    report = output_dir / "result-metadata.json"
    if output.exists() or report.exists():
        raise FileExistsError("Use a new output directory for each experiment")

    from PIL import Image, ImageOps
    from fashn_vton import TryOnPipeline

    with Image.open(person_path) as image:
        person = ImageOps.exif_transpose(image).convert("RGB")
    with Image.open(garment_path) as image:
        garment = ImageOps.exif_transpose(image).convert("RGB")
    start = time.monotonic()
    pipeline = TryOnPipeline(weights_dir=str(weights_path))
    loaded = time.monotonic()
    generated = pipeline(person_image=person, garment_image=garment,
                         category=category, garment_photo_type="flat-lay",
                         segmentation_free=True).images[0]
    finished = time.monotonic()
    # No resize or crop: size differences are explicit and require manual review.
    with output.open("xb") as target:
        generated.save(target, format="PNG")
    metadata = {
        "experimental_only": True,
        "manual_review_required": True,
        "category": category,
        "frame_operator_declared": frame,
        "input_dimensions": list(person.size),
        "output_dimensions": list(generated.size),
        "dimensions_match": person.size == generated.size,
        "model_load_seconds": round(loaded - start, 3),
        "inference_seconds": round(finished - loaded, 3),
        "warning": "No automated checks of frame, body, identity, background or garment fidelity.",
    }
    with report.open("x", encoding="utf-8") as target:
        json.dump(metadata, target, ensure_ascii=False, indent=2)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--person", required=True, type=Path)
    parser.add_argument("--garment", required=True, type=Path)
    parser.add_argument("--weights", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--category", required=True, choices=["tops", "bottoms", "one-pieces"])
    parser.add_argument("--frame", required=True, choices=["shoulders", "waist", "full"])
    args = parser.parse_args()
    run(args.person, args.garment, args.weights, args.output_dir, args.category, args.frame)


if __name__ == "__main__":
    main()
