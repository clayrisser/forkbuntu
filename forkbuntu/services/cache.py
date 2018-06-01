from cfoundation import Service
from hashlib import md5
from munch import munchify, Munch, unmunchify
from os import path
import checksum
import checksumdir
import hashlib
import os
import yaml

class Cache(Service):
    def checksum(self, checksum_path):
        value = md5(checksum_path.encode()).hexdigest()
        if path.exists(checksum_path):
            if path.isdir(checksum_path):
                value = checksumdir.dirhash(checksum_path)
            else:
                value = checksum.get_for_file(checksum_path).decode('utf-8')
        return value

    def register(self, key):
        c = self.app.conf
        step = getattr(self.app.steps, key)
        cache = self.get()
        if not 'checksums' in cache:
            cache.checksums = Munch()
        cache.checksums[key] = []
        for checksum_path in step.checksum_paths:
            cache.checksums[key].append(self.checksum(checksum_path))
        return self.__write(cache)

    def get_checksums(self, key=None):
        cache = self.get()
        if key:
            if 'checksums' not in cache or not key in cache.checksums:
                return []
            return cache.checksums[key]
        if 'checksums' not in cache:
            return Munch()
        return cache.checksums

    def finished(self):
        cache = self.get()
        cache.finished = True
        return self.__write(cache)

    def started(self):
        cache = self.get()
        cache.finished = False
        return self.__write(cache)

    def is_finished(self):
        cache = self.get()
        if not 'finished' in cache:
            return False
        return cache.finished

    def get(self):
        c = self.app.conf
        cache_path = path.join(c.paths.cwt, '.cache.yml')
        cache = Munch()
        if not path.exists(cache_path):
            return cache
        with open(cache_path, 'r') as f:
            data = munchify(yaml.load(f))
            if data:
                cache = data
        return cache

    def __write(self, cache):
        c = self.app.conf
        s = self.app.services
        cache_path = path.join(c.paths.cwt, '.cache.yml')
        if not path.isdir(c.paths.cwt):
            os.makedirs(c.paths.cwt)
        with open(cache_path, 'w') as f:
            yaml.dump(unmunchify(cache), f, default_flow_style=False)
        s.util.chown(cache_path)
        return cache
