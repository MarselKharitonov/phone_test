"""Minimal contracts shared by experimental try-on backends."""
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import Protocol


class Category(str, Enum):
    TOPS = "tops"
    BOTTOMS = "bottoms"
    ONE_PIECES = "one-pieces"


class Frame(str, Enum):
    SHOULDERS = "shoulders"
    WAIST = "waist"
    FULL = "full"


@dataclass(frozen=True)
class TryOnRequest:
    person: Path
    garment: Path
    category: Category
    frame: Frame
    output: Path

    def validate(self) -> None:
        if not isinstance(self.category, Category) or not isinstance(self.frame, Frame):
            raise ValueError("Category and frame must be recognized values")
        if self.frame != Frame.FULL and self.category != Category.TOPS:
            raise ValueError("Partial-body photos only permit visible upper garments")
        if not self.person.is_file() or not self.garment.is_file():
            raise ValueError("Person and garment inputs must be existing files")
        if self.output.resolve() in (self.person.resolve(), self.garment.resolve()):
            raise ValueError("Output must not overwrite an input")
        if self.output.exists():
            raise ValueError("Output already exists")
        if self.output.suffix.lower() != ".png":
            raise ValueError("Output must be a PNG file")


class TryOnProvider(Protocol):
    def generate(self, request: TryOnRequest) -> Path:
        """Generate an experimental image, not a QC-approved result."""
