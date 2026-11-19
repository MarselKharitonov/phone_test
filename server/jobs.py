"""Thread-safe, ephemeral test job store. No network exposure and no persistent photos."""
from dataclasses import dataclass, field
from enum import Enum
from threading import Lock
from uuid import uuid4


class State(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    FAILED = "failed"
    REVIEW = "manual_review"


@dataclass
class Job:
    id: str
    person: bytes = field(repr=False)
    garment: bytes = field(repr=False)
    frame: str
    category: str
    state: State = State.QUEUED
    result: bytes | None = field(default=None, repr=False)
    error: str | None = None


class JobStore:
    def __init__(self, max_image_bytes=8_000_000):
        self.jobs = {}
        self.lock = Lock()
        self.max_image_bytes = max_image_bytes

    def create(self, person, garment, frame, category, consent):
        if consent is not True:
            raise ValueError("Consent is required")
        if frame not in ("shoulders", "waist", "full") or category not in ("tops", "bottoms", "one-pieces"):
            raise ValueError("Invalid frame or category")
        if frame != "full" and category != "tops":
            raise ValueError("Partial frames allow only tops")
        for image in (person, garment):
            if not isinstance(image, bytes) or not 0 < len(image) <= self.max_image_bytes:
                raise ValueError("Invalid image size")
        job = Job(str(uuid4()), person, garment, frame, category)
        with self.lock:
            self.jobs[job.id] = job
        return job

    def get(self, job_id):
        with self.lock:
            return self.jobs.get(job_id)

    def delete(self, job_id):
        with self.lock:
            return self.jobs.pop(job_id, None) is not None
