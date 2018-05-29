from cfoundation import Service
from munch import munchify, Munch, unmunchify
from os import path
import checksum
import checksumdir
import hashlib
import yaml

class Cache(Service):
    def checksum(self, checksum_path):
        value = None
        if path.exists(checksum_path):
            if path.isdir(checksum_path):
                value = checksumdir.dirhash(checksum_path)
            else:
                value = checksum.get_for_file(checksum_path).decode('utf-8')
        return value

    def register(self, key):
        c = self.app.conf
        s = self.app.services
        step = getattr(self.app.steps, key)
        cache = self.get()
        cache[key] = []
        for checksum_path in step.checksum_paths:
            cache[key].append(self.checksum(checksum_path))
        cache_path = path.join(c.paths.cwt, '.cache.yml')
        with open(cache_path, 'w') as f:
            yaml.dump(unmunchify(cache), f, default_flow_style=False)
        s.util.chown(cache_path)
        return cache

    def get(self, key=None):
        c = self.app.conf
        cache_path = path.join(c.paths.cwt, '.cache.yml')
        cache = Munch()
        if not path.exists(cache_path):
            return cache
        with open(cache_path, 'r') as f:
            data = munchify(yaml.load(f))
            if data:
                cache = data
        if key:
            if not key in cache:
                return []
            return cache[key]
        return cache
