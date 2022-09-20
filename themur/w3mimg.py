from pathlib import Path
from subprocess import Popen, PIPE
from tempfile import NamedTemporaryFile

from PIL.Image import Image


class W3mImg:
    path: Path

    def __init__(self, path: Path = Path('/usr/lib/w3m/w3mimgdisplay')):
        self.path = path

    def draw(self, img: Image, x: int = 0, y: int = 0, w: int = 0, h: int = 0):
        if w == 0:
            w = img.width
        if h == 0:
            h = img.height

        with NamedTemporaryFile('w', suffix=f".{img.format}") as fp:
            img.save(fp)
            cmds = [
                W3mImgCommand.draw_image(fp.name, 1, x, y, w, h),
                W3mImgCommand.sync_drawing()
            ]
            p = Popen([str(self.path)], stdout=PIPE, stdin=PIPE, stderr=PIPE)
            out, err = p.communicate(("\n".join(cmds)).encode())


class W3mImgCommand:
    @staticmethod
    def draw_image(img_fp: Path, n: int = 1, x: int = 0, y: int = 0, w: int = 0, h: int = 0, sx: int = None,
                   sy: int = None, sw: int = None, sh: int = None) -> str:
        sx = '' if sx is None else sx
        sy = '' if sy is None else sy
        sw = '' if sw is None else sw
        sh = '' if sh is None else sh
        return f"0;{n};{x};{y};{w};{h};{sx};{sy};{sw};{sh};{img_fp}"

    @staticmethod
    def redraw_image(img_fp: Path, n: int = 1, x: int = 0, y: int = 0, w: int = 0, h: int = 0, sx: int = None,
                     sy: int = None, sw: int = None, sh: int = None) -> str:
        sx = '' if sx is None else sx
        sy = '' if sy is None else sy
        sw = '' if sw is None else sw
        sh = '' if sh is None else sh
        return f"1;{n};{x};{y};{w};{h};{sx};{sy};{sw};{sh};{img_fp}"

    @staticmethod
    def terminate_drawing() -> str:
        return "2;"

    @staticmethod
    def sync_drawing() -> str:
        return "3;"

    @staticmethod
    def nop() -> str:
        return "4;"

    @staticmethod
    def get_img_size(img_fp: Path) -> str:
        return f"5;{img_fp}"

    @staticmethod
    def clear_image(x: int = 0, y: int = 0, w: int = 0, h: int = 0) -> str:
        return f"6;{x};{y};{w};{h}"
