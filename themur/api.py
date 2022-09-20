import asyncio
import json
import os
from pathlib import Path
from typing import Callable

import pywal
from pywal.backends.colorthief import get as colorthief_get
from pywal.backends.colorz import get as colorz_get
from pywal.backends.haishoku import get as haishoku_get
from pywal.backends.schemer2 import get as schemer2_get
from pywal.backends.wal import get as wal_get

from themur.colorscheme import ColorScheme
from themur.source import Source, PicsumLorem, LocalSource


class Themur:
    config_dir: Path
    config: dict
    cache_dir: Path
    wal_cache_dir: Path
    hist_file: Path
    hist_size: int
    history: list[dict]
    backends: dict[str, Callable[[str, bool], list[str]]]
    sources = {
        'LocalSource': LocalSource,
        'PicsumLorem': PicsumLorem
    }
    reference_colorscheme: ColorScheme
    current_colorscheme: ColorScheme
    current_colorscheme_fp: Path

    def __init__(self,
                 config_dir: Path = Path(os.environ['XDG_CONFIG_HOME'], 'themur'),
                 cache_dir: Path = Path(os.environ['XDG_CACHE_HOME'], 'themur'),
                 hist_size=10):
        self.config_dir = config_dir
        self.config_dir.mkdir(parents=True, exist_ok=True)
        config_fp = self.config_dir / 'config.json'
        if config_fp.is_file():
            self.config = json.load(open(config_fp))
        else:
            self.config = {
                'w3mimg': '/usr/lib/w3m/w3mimgdisplay',
                'schemer2': f"{os.environ.get('GO_PATH', os.environ['HOME'] + '/go')}/bin"
            }
        os.environ['PATH'] = f"{os.environ['PATH']}:{self.config['schemer2']}"
        self.cache_dir = cache_dir
        self.wal_cache_dir = self.cache_dir / 'wal'
        self.wal_cache_dir.mkdir(parents=True, exist_ok=True)
        self.hist_file = self.cache_dir / 'history.json'
        self.hist_size = hist_size
        self.history = self._load_history()
        self.backends = {
            'colorthief': colorthief_get,
            'colorz': colorz_get,
            'haishoku': haishoku_get,
            'schemer2': schemer2_get,
            'wal': wal_get,
        }
        self.reference_colorscheme = ColorScheme.load('resources/colorschemes/material_darker.json')
        self.current_colorscheme_fp = self.cache_dir / "current_colorscheme.json"
        if self.current_colorscheme_fp.exists():
            self.current_colorscheme = ColorScheme.load(self.current_colorscheme_fp)
        else:
            self.current_colorscheme = self.reference_colorscheme

    def _load_history(self) -> list[dict]:
        if self.hist_file.exists():
            return json.load(open(self.hist_file))[:self.hist_size]
        else:
            return []

    def _save_history(self):
        json.dump(self.history, open(self.hist_file, 'w'))

    def _add_to_history(self, path: Path, source: Source, meta: dict, options: dict):
        if len(self.history) >= self.hist_size:
            self.history.pop(0)
        self.history.append({
            'file': str(path),
            'source': source.__class__.__name__,
            'source_args': source.args,
            'meta': meta,
            'options': options,
        })
        self._save_history()

    def _peek_history(self) -> tuple[Path, Source, dict, dict]:
        if len(self.history) == 0:
            raise Exception("No entries available in history")
        entry = self.history[-1]
        path = Path(entry['file'])
        source = self.sources[entry['source']](**entry['source_args'])
        meta = entry['meta']
        options = entry['options']
        return path, source, meta, options

    def _pop_from_history(self) -> tuple[Path, Source, dict, dict]:
        if len(self.history) == 0:
            raise Exception("No entries available in history")
        path, source, meta, options = self._peek_history()
        self.history.pop()
        self._save_history()
        return path, source, meta, options

    def get_color_schemes(self, path: Path) -> dict[str, ColorScheme]:
        async def get_cols():
            async def get_col(path: str, backend: str) -> dict:
                return pywal.colors.get(path, backend=backend, cache_dir=self.wal_cache_dir)

            cols = {}
            for backend in self.backends.keys():
                cols[backend] = ColorScheme.load(await get_col(str(path), backend))
            return cols

        return asyncio.run(get_cols())
