from __future__ import annotations

import os
from hashlib import md5
from os import path

import yaml
from munch import Munch, unmunchify

from ..helpers import to_munch
from ..service import Service


class Cache(Service):
    def checksum(self, checksum_path: str) -> str:
        if path.exists(checksum_path):
            if path.isdir(checksum_path):
                return self._dir_checksum(checksum_path)
            return self._file_checksum(checksum_path)
        return md5(checksum_path.encode()).hexdigest()

    def register(self, key: str) -> Munch:
        step = getattr(self.app.steps, key)
        cache = self.get()
        if "checksums" not in cache:
            cache.checksums = Munch()
        cache.checksums[key] = []
        for checksum_path in step.checksum_paths or []:
            cache.checksums[key].append(self.checksum(checksum_path))
        return self._write(cache)

    def get_checksums(self, key: str | None = None) -> list[str] | Munch:
        cache = self.get()
        if key:
            if "checksums" not in cache or key not in cache.checksums:
                return []
            return cache.checksums[key]
        if "checksums" not in cache:
            return Munch()
        return cache.checksums

    def finished(self) -> Munch:
        cache = self.get()
        cache.finished = True
        return self._write(cache)

    def started(self) -> Munch:
        cache = self.get()
        cache.finished = False
        return self._write(cache)

    def is_finished(self) -> bool:
        cache = self.get()
        if "finished" not in cache:
            return False
        return cache.finished

    def get(self) -> Munch:
        c = self.app.conf
        cache_path = path.join(c.paths.cwt, ".cache.yml")
        cache = Munch()
        if not path.exists(cache_path):
            return cache
        with open(cache_path) as f:
            data = yaml.safe_load(f)
            if data:
                cache = to_munch(data)
        return cache

    def _file_checksum(self, file_path: str) -> str:
        digest = md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(65536), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def _dir_checksum(self, dir_path: str) -> str:
        digest = md5()
        for root, dirs, files in os.walk(dir_path):
            dirs.sort()
            for filename in sorted(files):
                file_path = path.join(root, filename)
                digest.update(path.relpath(file_path, dir_path).encode())
                if path.isfile(file_path):
                    digest.update(self._file_checksum(file_path).encode())
        return digest.hexdigest()

    def _write(self, cache: Munch) -> Munch:
        c = self.app.conf
        s = self.app.services
        cache_path = path.join(c.paths.cwt, ".cache.yml")
        if not path.isdir(c.paths.cwt):
            os.makedirs(c.paths.cwt)
        with open(cache_path, "w") as f:
            yaml.dump(unmunchify(cache), f, default_flow_style=False)
        s.util.chown(cache_path)
        return cache
