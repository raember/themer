import subprocess
from typing import Tuple


def get_monitor_resolution() -> Tuple[int, int]:
    for line in subprocess.check_output(('xdpyinfo')).decode().split('\n'):
        if 'dimensions:' in line:
            left, right = line.split('x', maxsplit=1)
            width = int(left.rsplit(' ', maxsplit=1)[-1])
            height = int(right.split(' ', maxsplit=1)[0])
            return width, height
    raise Exception("Couldn't find the monitor resolution(s)")
