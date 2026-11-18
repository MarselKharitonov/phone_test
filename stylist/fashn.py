"""FASHN test adapter. Dependencies are deliberately loaded only on use."""
from pathlib import Path
from .contracts import TryOnRequest


class FashnProvider:
    def __init__(self, weights_dir: Path):
        self.weights_dir = weights_dir
        self._pipeline = None

    def generate(self, request: TryOnRequest) -> Path:
        request.validate()
        from PIL import Image, ImageOps
        from fashn_vton import TryOnPipeline

        if self._pipeline is None:
            self._pipeline = TryOnPipeline(weights_dir=str(self.weights_dir))
        with Image.open(request.person) as image:
            person = ImageOps.exif_transpose(image).convert("RGB")
        with Image.open(request.garment) as image:
            garment = ImageOps.exif_transpose(image).convert("RGB")
        result = self._pipeline(person_image=person, garment_image=garment,
                                category=request.category.value)
        generated = result.images[0]
        if generated.size != person.size:
            raise ValueError("Output dimensions differ from input; manual review required")
        with request.output.open("xb") as destination:
            generated.save(destination, format="PNG")
        return request.output
