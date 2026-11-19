"""Explicitly disabled remote adapter until isolation and deletion are verified."""
from pathlib import Path


class KaggleAdapter:
    def __init__(self, dataset_dir: Path):
        self.dataset_dir = dataset_dir

    def submit(self, job):
        raise RuntimeError(
            "Kaggle submission disabled: private storage, credentials, deletion and "
            "provider conditions must be verified before transmitting photographs."
        )


class FakeAdapter:
    """Only for tests; never claims a virtual try-on was generated."""
    def submit(self, job):
        return {"state": "failed", "error": "Test adapter does not generate images"}
