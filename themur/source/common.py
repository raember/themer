import json
from abc import ABC
from pathlib import Path
from typing import Tuple

import PIL.Image as PImage
import requests
from PIL import ExifTags
from PIL.Image import Image
from PIL.TiffImagePlugin import IFDRational
from requests import Session


class Source(ABC):
    cache_home: Path
    cache_path: Path

    def __init__(self, cache_home: Path | str):
        """
        A source for images to be loaded

        :param cache_home: The cache home folder
        :type cache_home: Path | str
        """
        if isinstance(cache_home, str):
            cache_home = Path(cache_home)
        self.cache_home = cache_home
        self.cache_path = self.cache_home / 'cached' / self.__class__.__name__
        self.cache_path.mkdir(parents=True, exist_ok=True)

    @property
    def args(self) -> dict:
        return {'cache_home': str(self.cache_path)}

    def get_img(self, **kwargs) -> Tuple[Image, Path, dict]:
        """
        Get a new random image from the source.

        :param kwargs: Arguments to be given to the subclass
        :type kwargs: dict
        :return: A random image, its filename and a dictionary with meta information
        :rtype: Tuple[Image, Path, dict]
        """
        img, name, meta = self._get_img(kwargs)
        exif = {}
        for k, v in img._getexif().items():
            if k in ExifTags.TAGS:
                if isinstance(v, bytes):
                    try:
                        v = v.decode('utf-8')
                    except:
                        raise
                elif isinstance(v, IFDRational):
                    v = f"{v.real}+i{v.imag}"
                exif[ExifTags.TAGS[k]] = v
        meta['exif'] = exif
        fp = self._cache(img, name, meta)
        return img, fp, meta

    def redo_img(self, **kwargs) -> Tuple[Image, Path, dict]:
        """
        Redo the latest image with different arguments

        :param kwargs: The new arguments to pass to the get_img function
        :type kwargs: dict
        :return: The image redone, its filename and a dictionary with meta information
        :rtype: Tuple[Image, Path, dict]
        """
        if len(self.history) == 0:
            raise Exception("No entries available in history")
        path, meta, options = self._pop_from_history()
        kwargs = {k: v for k, v in kwargs.items() if v is not None}
        options.update(kwargs)
        return self.get_img(**options)

    def get_last(self) -> Tuple[Image, Path, dict]:
        """
        Get the cached image prior to the latest one.

        Fails if there are no entries in the histry.
        :return: The cached image, its filename and a dictionary with meta information
        :rtype: Tuple[Image, Path, dict]
        """
        if len(self.history) == 0:
            raise Exception("No entries available in history")
        self._pop_from_history()
        path, meta, options = self._pop_from_history()
        self._add_to_history(path, meta, options)
        return PImage.open(self.cache_path / path), path, meta

    def _get_img(self, options: dict) -> Tuple[Image, Path, dict]:
        raise NotImplemented('Must be overwritten')

    def _cache(self, img: Image, path: Path, meta: dict) -> Path:
        file_path = self.cache_path / path
        img.save(file_path)
        json.dump(meta, open(file_path.with_suffix('.json'), 'w'))
        return file_path.absolute()


class InternetSource(Source, ABC):
    session: Session

    def __init__(self, cache_home: Path | str):
        super().__init__(cache_home)
        self.session = requests.Session()
