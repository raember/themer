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

    def __init__(self, path: Path | str, cache_home: Path | str):
        super().__init__(cache_home)
        if isinstance(path, str):
            path = Path(path)
        self.path = path

    @property
    def args(self) -> dict:
        return {**super().args, 'path': str(self.path)}

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
