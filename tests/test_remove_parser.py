import tempfile
import unittest
from pathlib import Path

from kaggle_experiment.remove_parser import patch_tree, replace_once


class ParserPatchTests(unittest.TestCase):
    def test_replace_once_fails_on_missing_and_duplicate(self):
        for source in ("none", "xx"):
            with self.assertRaises(ValueError):
                replace_once(source, "x", "y")

    def test_unknown_source_is_not_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            (root / "src/fashn_vton/preprocessing").mkdir(parents=True)
            files = [root / "src/fashn_vton/pipeline.py",
                     root / "src/fashn_vton/preprocessing/agnostic.py",
                     root / "pyproject.toml"]
            for file in files:
                file.write_text("unexpected", encoding="utf-8")
            with self.assertRaises(ValueError):
                patch_tree(root)
            self.assertTrue(all(file.read_text(encoding="utf-8") == "unexpected" for file in files))
