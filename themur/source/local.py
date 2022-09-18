import random
from pathlib import Path
from typing import Tuple

import PIL.Image as PImage
from PIL.Image import Image

from themur.source.common import Source


class LocalSource(Source):
    """
    Image source for local files
    """
    path: Path

    def __init__(self, path: Path, hist_size: int = 10):
        super().__init__(hist_size=hist_size)
        self.path = path

    def _get_img(self, options: dict) -> Tuple[Image, Path, dict]:
        suffix = options.get('suffix', '.jpg')
        img_paths = list(self.path.rglob(f'*{suffix}'))
        if len(img_paths) == 0:
            raise Exception(f"No files found in {self.path} with '{suffix}' suffix")
        img_path = random.choice(list(self.path.rglob(f'*{suffix}')))
        img = PImage.open(open(img_path))
        meta = {
            'width': img.width,
            'height': img.height,
        }
        return img, Path(img_path.name), meta
