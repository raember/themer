import argparse
import sys
from pathlib import Path

from themur.api import Themur
from themur.colorscheme import ColorScheme
from themur.source import PicsumLorem, LocalSource
from themur.utils import get_monitor_resolution, print_color_table
from themur.utils import print_colortest, get_cursor_pos
from themur.w3mimg import W3mImg

WAL_DIR = Path.home() / '.cache/wal'
CURRENT_IMAGE = WAL_DIR / 'current_wp.jpg'

JOB_CHANGE = 'change'
JOB_LIST_SCHEMES = 'list'


def parse_args():
    parser = argparse.ArgumentParser()
    # New image from Picsum Lorem
    parser.add_argument('--picsum', help='Will source image from picsum lorem', action='store_true', default=False)
    parser.add_argument('--opts', '-o', help='Options to pass to the sources (i.e. Picsum: picsum_id=420,grayscale)',
                        nargs='*', type=arg2dict, default={})
    # New image from local file storage
    parser.add_argument('--local', help='Will source image from a local directory or file', action='store', type=Path)

    parser.add_argument('--previous', '-p', help='Will load the image before the latest one', action='store_true',
                        default=False)
    parser.add_argument('--full', help='Get the full sized image and crop later', action='store_true', default=False)
    parser.add_argument('--redo', help='Do not get a new image but rather re-run with the current one',
                        action='store_true', default=False)
    parser.add_argument('--offset', help='Offset the brighter colors to distinguish between the two', action='store',
                        type=int, default=0)
    parser.add_argument('--reorder', help='Reorder the generated colors for a better match', action='store_true',
                        default=False)
    parser.add_argument('--interpolate', help='Interpolate between the new and the reference colorscheme',
                        action='store', type=float, default=0.0)

    # LIST

    # Additional
    parser.add_argument('-q', '--quiet', help='Whether to not log anything', action='store_true', default=False)
    args = parser.parse_args()
    if args.picsum and args.local:
        print("Source can only be --picsum [--opts ...] or --local path/to/file/or/folder", file=sys.stderr)
        exit(1)
    return args


def arg2dict(s: str) -> tuple[str, str | bool]:
    if '=' not in s:
        return s, True
    k, v = s.split('=', maxsplit=1)
    return k, v


def main():
    args = parse_args()
    themur = Themur()
    w, h = get_monitor_resolution()
    opts = dict(args.opts)
    if isinstance(opts, set) or len(opts) == 0:
        opts = {}
    if args.picsum:
        source = PicsumLorem(themur.cache_dir)
        if not args.full:
            opts['width'] = w
            opts['height'] = h
    elif args.local:
        path = Path(args.local)
        if not path.exists():
            raise FileNotFoundError(path)
        source = LocalSource(path, themur.cache_dir)
    else:
        raise Exception()
    if args.previous:
        img, path, meta = source.get_last()
    else:
        img, path, meta = source.get_img(**opts)
    s = f'\033[1m{path.stem} ({meta["width"]}x{meta["height"]}):'
    if 'title' in meta.keys():
        s += f' "{meta["title"]}"'
    if 'id' in meta.keys():
        s += f" ({meta['id']})"
    if 'author' in meta.keys():
        s += f" by {meta['author']}"
    s += '\033[m'
    print(s)

    for backend, col_scheme in themur.get_color_schemes(path).items():
        print(backend)
        # print_color_table(col_scheme.to_256_colors())
        if args.offset > 0:
            # print("  ==> Offset")
            col_scheme.offset(args.offset)
            # print_color_table(col_scheme.to_256_colors())
        if args.reorder:
            # print("  ==> Reorder")
            col_scheme.reorder(themur.reference_colorscheme)
            # print_color_table(col_scheme.to_256_colors())
        if args.interpolate > 0.0:
            # print("  ==> Interpolate")
            col_scheme.interpolate(themur.reference_colorscheme, args.interpolate)
        print_color_table(col_scheme.to_256_colors())

    PIXEL_PER_ROW = 12
    PIXEL_PER_COLUMN = 6
    h2 = (len(themur.backends) * 4) * PIXEL_PER_ROW
    w2 = int(h2 / h * w)
    w3m = W3mImg()
    # print(os.get_terminal_size())
    # print(getpos())
    row, column = get_cursor_pos()
    if row is not None and column is not None:
        row -= 1
        row *= PIXEL_PER_ROW
        column = PIXEL_PER_COLUMN * (8 * 9 + 1)
        w3m.draw(img, column, row - h2, w2, h2)
    exit()
    img.show()
    print_color_table()
    col = ColorScheme.load(Path('resources/colorschemes/material_darker.json'))
    print_colortest(col.to_256_colors())
    print_color_table(col.to_256_colors())
    print_color_table()
    exit()
    w, h = get_monitor_resolution()
    picsum = PicsumLorem()
    img, path, meta = picsum.get_img(width=w, height=h)
    img.show()
    img2, path2, meta2 = picsum.get_img()
    img2.show()
    img3, path3, meta3 = picsum.redo_img(grayscale=True)
    img3.show()
    img4, path4, meta4 = picsum.get_last()
    img4.show()
    print('Done')


if __name__ == '__main__':
    main()
