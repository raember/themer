import io
import random
from pathlib import Path
from typing import Tuple

import PIL.Image as PImage
from PIL.Image import Image
from urllib3.util import Url

from themur.source.common import InternetSource

HIGHEST_PICSUM_LOREM_ID = 1084


class PicsumLorem(InternetSource):
    """
    Image source utilizing the Picsum Lorem API (see https://picsum.photos/)
    """

    def get_img(self, picsum_id: str = None, width: int = None, height: int = None, grayscale: bool = None,
                blur: int = None) -> Tuple[Image, Path, dict]:
        """
        Get a new random image from the source.

        :param picsum_id: The ID of the picsum image, if available
        :type picsum_id: str
        :param width: The width of the image (if available). Without height, this will result in a square image
        :type width: int
        :param height: The height of the image (if available). Without width, this will result in a square image
        :type height: int
        :param grayscale: Whether the image should be grayscale or not (default: False)
        :type grayscale: bool
        :param blur: Whether and how strong of a blur should be applied between 0 and 10 (default: 0 = no blur)
        :type blur: int
        :return: A random image, its filename and a dictionary with meta information
        :rtype: Tuple[Image, Path, dict]
        """
        if width is not None:
            width = min(5000, width)
        if height is not None:
            height = min(5000, height)
        return super(PicsumLorem, self).get_img(**{
            'picsum_id': picsum_id,
            'width': width,
            'height': height,
            'grayscale': grayscale,
            'blur': blur
        })

    def redo_img(self, width: int = None, height: int = None, grayscale: bool = None, blur: int = None) \
            -> Tuple[Image, Path, dict]:
        """
        Redo the latest image with different arguments

        :param width: The width of the image (if available). Without height, this will result in a square image
        :type width: int
        :param height: The height of the image (if available). Without width, this will result in a square image
        :type height: int
        :param grayscale: Whether the image should be grayscale or not (default: False)
        :type grayscale: bool
        :param blur: Whether and how strong of a blur should be applied between 0 and 10 (default: 0 = no blur)
        :type blur: int
        :return: A random image, its filename and a dictionary with meta information
        :rtype: Tuple[Image, Path, dict]
        """
        return super(PicsumLorem, self).redo_img(**{
            'width': width,
            'height': height,
            'grayscale': grayscale,
            'blur': blur
        })

    def _get_img(self, options: dict) -> Tuple[Image, Path, dict]:
        height = options.get('height')
        width = options.get('width')
        path = ""
        meta = {}
        picsum_id = options.get('picsum_id')
        if height is None and width is None:
            if picsum_id is None:
                picsum_id = str(random.randint(0, HIGHEST_PICSUM_LOREM_ID))
            meta = self._get_info(picsum_id)
            width = meta['width']
            height = meta['height']
        if picsum_id is not None:
            path += f"/id/{picsum_id}"
        if width is not None:
            path += f"/{width}"
        if height is not None:
            path += f"/{height}"
        query = []
        grayscale = options.get('grayscale')
        if grayscale is not None and grayscale:
            query.append("grayscale")
        blur = options.get('blur')
        if blur is not None and blur > 0:
            blur = min(10, blur)
            if blur != 1:
                blur_str = f"blur={blur}"
            else:
                blur_str = "blur"
            query.append(blur_str)
        url = Url("https", host="picsum.photos", path=path, query='&'.join(query))
        resp = self.session.get(url)
        resp.raise_for_status()
        picsum_id = resp.headers['picsum-id']
        img = PImage.open(io.BytesIO(resp.content))
        suffix = {
            'JPEG': '.jpg',
            'PNG': '.png',
        }[img.format]
        query_str = ''
        if len(query) > 0:
            query_str = f"_{'_'.join(query)}"
        name = f"picsum_lorem_{picsum_id}-{width}x{height}{query_str}"

        if len(meta) == 0:
            meta = self._get_info(picsum_id)

        # Modify kwargs for redos
        options.clear()
        options['picsum_id'] = picsum_id
        options['width'] = int(meta['width'])
        options['height'] = int(meta['height'])
        return img, Path(name).with_suffix(suffix), meta

    def _get_info(self, picsum_id: str) -> dict:
        url = Url("https", host="picsum.photos", path=f"/id/{picsum_id}/info")
        resp2 = self.session.get(url)
        resp2.raise_for_status()
        return resp2.json()
