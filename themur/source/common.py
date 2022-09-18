import json
from abc import ABC
from pathlib import Path
from typing import Tuple

import PIL.Image as PImage
import requests
from PIL.Image import Image
from requests import Session


class Source(ABC):
    cache_path: Path
    hist_file: Path
    history: list
    hist_size: int

    def __init__(self, hist_size=10):
        """
        Create an image source with a cache and a history

        :param hist_size: How many history entries to keep
        :type hist_size: int
        """
        self.history = []
        self.cache_path = Path('.cache', self.__class__.__name__)
        self.cache_path.mkdir(parents=True, exist_ok=True)
        self.hist_file = self.cache_path / 'stack.json'
        self.hist_size = hist_size
        self.history = self._load_history()

    def _load_history(self) -> list[str]:
        if self.hist_file.exists():
            return json.load(open(self.hist_file))[:self.hist_size]
        else:
            return []

    def _save_history(self):
        json.dump(self.history, open(self.hist_file, 'w'))

    def _add_to_history(self, path: Path, meta: dict, options: dict):
        if len(self.history) >= self.hist_size:
            self.history.pop(0)
        self.history.append({
            'file': str(path),
            'meta': meta,
            'options': options,
        })
        self._save_history()

    def _pop_from_history(self) -> Tuple[Path, dict, dict]:
        if len(self.history) == 0:
            raise Exception("No entries available in history")
        entry = self.history.pop()
        path = Path(entry['file'])
        meta = entry['meta']
        options = entry['options']
        self._save_history()
        return path, meta, options

    def get_img(self, **kwargs) -> Tuple[Image, Path, dict]:
        """
        Get a new random image from the source.

        :param kwargs: Arguments to be given to the subclass
        :type kwargs: dict
        :return: A random image, its filename and a dictionary with meta information
        :rtype: Tuple[Image, Path, dict]
        """
        img, path, meta = self._get_img(kwargs)
        self._cache(img, path, meta)
        self._add_to_history(path, meta, kwargs)
        return img, path, meta

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

    def _cache(self, img: Image, path: Path, meta: dict):
        file_path = self.cache_path / path
        img.save(file_path)
        json.dump(meta, open(file_path.with_suffix('.json'), 'w'))


class InternetSource(Source, ABC):
    session: Session

    def __init__(self, hist_size=10):
        super().__init__(hist_size=hist_size)
        self.session = requests.Session()
