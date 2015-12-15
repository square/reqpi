import collections
import hashlib


class MemoryStore(object):

    def __init__(self, reactor):
        self.hashes = collections.defaultdict(dict)
        self.hashAges = {}
        self.reactor = reactor

    def add(self, requirements):
        sha = hashlib.sha224(requirements).hexdigest()
        for package in requirements.split():
            name, version = package.split('==')
            self.hashes[sha][name.lower()] = name, version
        self.hashAges[sha] = self.reactor.seconds()
        return sha

    def version(self, sha, name):
        self.hashAges[sha] = self.reactor.seconds()
        return self.hashes[sha][name.lower()]

    def removeOlder(self, age):
        era = self.reactor.seconds() - age
        keys = [key for key, value in self.hashAges.items() if value < era]
        for key in keys:
            del self.hashAges[key]
            del self.hashes[key]


class MemoryLocationCache(object):

    def __init__(self):
        self.locations = {}

    def save(self, details, location):
        self.locations[details] = dict(value=location)

    def get(self, details):
        return self.locations.get(details) or {}
