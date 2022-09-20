import json
from pathlib import Path

from themur import print_color_table
from themur.utils import rgb_to_256col_ansi, find_closest_color, s2rgb, rgb2s, rgb2lab


class ColorScheme:
    data: dict

    @staticmethod
    def load(fp: Path | dict) -> 'ColorScheme':
        scheme = ColorScheme()
        if isinstance(fp, dict):
            scheme.data = fp
        else:
            scheme.data = json.load(open(fp))
        return scheme

    def dump(self, fp: Path):
        json.dump(self.data, open(fp, 'w'))

    def to_rgb(self) -> list[tuple[int, int, int]]:
        return [s2rgb(hx) for hx in self.data['colors'].values()]

    def to_256_colors(self) -> list[str]:
        term_cols = []
        for rgb in self.to_rgb():
            term_cols.append(rgb_to_256col_ansi(*rgb))
        return term_cols

    def print_approximate_color_table(self):
        print_color_table(self.to_256_colors())

    def offset(self, diff: int):
        for i, (r, g, b) in enumerate(self.to_rgb()[9:16]):
            # print(f"color{i + 9}: {rgb2s(r, g, b)}", end=' -> ')
            r = min(255, r + diff)
            g = min(255, g + diff)
            b = min(255, b + diff)
            # print(rgb2s(r, g, b))
            self.data['colors'][f"color{i + 9}"] = rgb2s(r, g, b)

    def reorder(self, reference: 'ColorScheme'):
        rcols = reference.to_rgb()[1:8]
        cols = [rgb2lab(r, g, b) for r, g, b in self.to_rgb()[1:8]]
        for i, rc in enumerate(rcols):
            l, a, b = rgb2lab(rc[0], rc[1], rc[2])
            c = find_closest_color(l, a, b, cols)
            j = cols.index(c)
            # print(f"color{i + 1}: {self.data['colors'][f'color{i + 1}']} -> {self.data['colors'][f'color{j + 1}']}")
            self.data['colors'][f"color{i + 1}"] = self.data['colors'][f"color{j + 1}"]
            self.data['colors'][f"color{i + 9}"] = self.data['colors'][f"color{j + 9}"]
            cols[j] = (9999, 9999, 9999)

    def interpolate(self, reference: 'ColorScheme', ratio: float):
        ratio = min(1.0, max(0.0, ratio))
        rcols = reference.to_rgb()
        cols = self.to_rgb()
        for i, ((r1, g1, b1), (r2, g2, b2)) in enumerate(zip(cols, rcols)):
            if i % 8 == 0:  # Black of the lighter row
                continue
            rd = r2 - r1
            gd = g2 - g1
            bd = b2 - b1
            if i % 7 == 0:  # Whites
                ratio2 = max(0.8, ratio + 0.5)
            else:
                ratio2 = ratio
            r = int(r1 + rd * ratio2)
            g = int(g1 + gd * ratio2)
            b = int(b1 + bd * ratio2)
            self.data['colors'][f"color{i}"] = rgb2s(r, g, b)
