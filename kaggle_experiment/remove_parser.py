"""Patch the pinned FASHN v1.5 source for flat-lay + segmentation-free use only.

No model is downloaded or run. Fails closed if upstream source is different.
"""
import argparse
from pathlib import Path


def replace_once(text: str, old: str, new: str) -> str:
    if text.count(old) != 1:
        raise ValueError("Unexpected upstream source: refusing to patch")
    return text.replace(old, new, 1)


def patch_tree(root: Path) -> None:
    pipeline_path = root / "src/fashn_vton/pipeline.py"
    agnostic_path = root / "src/fashn_vton/preprocessing/agnostic.py"
    pyproject_path = root / "pyproject.toml"
    pipeline = pipeline_path.read_text(encoding="utf-8")
    agnostic = agnostic_path.read_text(encoding="utf-8")
    project = pyproject_path.read_text(encoding="utf-8")

    pipeline = replace_once(pipeline,
        "from fashn_human_parser import CATEGORY_TO_BODY_COVERAGE, FashnHumanParser\n", "")
    pipeline = replace_once(pipeline, "        self._setup_hp_model()\n", "")
    start = pipeline.index("    def _setup_hp_model(self):")
    end = pipeline.index("    @torch.inference_mode()", start)
    pipeline = pipeline[:start] + pipeline[end:]
    marker = "        # Set seed\n"
    guard = (
        '        if not segmentation_free or garment_photo_type != "flat-lay":\n'
        '            raise ValueError("Parser-free pipeline requires segmentation_free and flat-lay")\n\n'
    )
    pipeline = replace_once(pipeline, marker, guard + marker)
    start = pipeline.index("        # Human parsing\n")
    end = pipeline.index("        # Resize/pad for model input\n", start)
    pipeline = pipeline[:start] + (
        "        # No segmentation: only segmentation-free person and flat-lay garment inputs.\n"
        "        ca_image = person_image_np.copy()\n"
        "        garment_image_processed = garment_image_np.copy()\n\n"
    ) + pipeline[end:]
    agnostic = replace_once(agnostic,
        "from fashn_human_parser import BODY_COVERAGE_TO_LABELS, IDENTITY_LABELS, LABELS_TO_IDS\n",
        "# Parser data are not available in this parser-free experiment.\n"
        "BODY_COVERAGE_TO_LABELS = {}\nIDENTITY_LABELS = ()\nLABELS_TO_IDS = {}\n")
    project = replace_once(project, '    "fashn-human-parser>=0.1.1",\n', "")

    if "from fashn_human_parser import" in pipeline or "from fashn_human_parser import" in agnostic:
        raise ValueError("Parser import remains")
    # Only write after every check succeeds.
    pipeline_path.write_text(pipeline, encoding="utf-8")
    agnostic_path.write_text(agnostic, encoding="utf-8")
    pyproject_path.write_text(project, encoding="utf-8")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    patch_tree(parser.parse_args().source)
