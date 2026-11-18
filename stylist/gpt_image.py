"""Reserved GPT Image interface; no network operations are implemented."""
from pathlib import Path
from .contracts import TryOnRequest


class GptImageProvider:
    def generate(self, request: TryOnRequest) -> Path:
        request.validate()
        raise RuntimeError(
            "GPT Image is disabled: applicable regional terms, data handling and "
            "paid API authorization must be verified before implementation."
        )
