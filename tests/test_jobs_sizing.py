import unittest
from server.jobs import JobStore
from server.kaggle_adapter import KaggleAdapter
from stylist.sizing import recommend
from pathlib import Path


class JobTests(unittest.TestCase):
    def test_partial_frame_rejects_bottoms(self):
        with self.assertRaises(ValueError):
            JobStore().create(b"a", b"b", "waist", "bottoms", True)

    def test_consent_required(self):
        with self.assertRaises(ValueError):
            JobStore().create(b"a", b"b", "waist", "tops", False)

    def test_deletion(self):
        store = JobStore()
        job = store.create(b"a", b"b", "waist", "tops", True)
        self.assertTrue(store.delete(job.id))
        self.assertIsNone(store.get(job.id))

    def test_remote_adapter_fails_closed(self):
        with self.assertRaises(RuntimeError):
            KaggleAdapter(Path(".")).submit(None)


class SizeTests(unittest.TestCase):
    def test_missing_measurement(self):
        self.assertEqual(recommend([], {}, ["waist"])["status"], "insufficient_data")

    def test_body_chart(self):
        chart = {"waist": {"type": "body", "min_cm": 80, "max_cm": 84}}
        v = [{"size_label": "M", "stock_status": "available", "measurements": chart}]
        self.assertEqual(recommend(v, {"waist": 82}, ["waist"])["size"], "M")

    def test_garment_measurement_not_treated_as_body(self):
        v = [{"size_label": "M", "stock_status": "available", "measurements":
              {"waist": {"type": "garment", "min_cm": 80, "max_cm": 84}}}]
        self.assertEqual(recommend(v, {"waast": 82, "waist": 82}, ["waist"])["status"], "insufficient_data")
