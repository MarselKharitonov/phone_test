import tempfile
import unittest
from pathlib import Path
from kaggle_experiment.inference import run, validate


class KaggleExperimentTests(unittest.TestCase):
    def test_partial_frames_reject_lower_body(self):
        for frame in ("waist", "shoulders"):
            for category in ("bottoms", "one-pieces"):
                with self.subTest(frame=frame, category=category):
                    with self.assertRaises(ValueError):
                        validate(category, frame)

    def test_supported_combination(self):
        validate("tops", "waist")
        validate("bottoms", "full")

    def test_no_input_files_no_model_load(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaises(FileNotFoundError):
                run(root / "missing", root / "also_missing", root, root, "tops", "waist")

    def test_does_not_overwrite(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "person").touch()
            (root / "garment").touch()
            (root / "result.png").touch()
            with self.assertRaises(FileExistsError):
                run(root / "person", root / "garment", root, root, "tops", "waist")
