import unittest

from twisted.internet import task

from reqpi.db import model


class TestMemoryStore(unittest.TestCase):

    def setUp(self):
        self.reactor = task.Clock()
        self.store = model.MemoryStore(self.reactor)

    def test_one_thing(self):
        reqs = 'foo==1.1.2\n'
        sha = self.store.add(reqs)
        name, version = self.store.version(sha + '', 'foo')
        self.assertEquals(name, 'foo')
        self.assertEquals(version, '1.1.2')

    def test_mixed_case(self):
        reqs = 'Foo==1.1.2\n'
        sha = self.store.add(reqs)
        name, version = self.store.version(sha + '', 'fOo')
        self.assertEquals(name, 'Foo')
        self.assertEquals(version, '1.1.2')

    def test_gc(self):
        reqs = 'foo==1.1.2\n'
        sha1 = self.store.add(reqs)
        reqs = 'bar==1.1.2\n'
        sha2 = self.store.add(reqs)
        reqs = 'baz==1.1.2\n'
        sha3 = self.store.add(reqs)
        self.reactor.advance(100)
        reqs = 'foo==1.1.2\n'
        sha1 = self.store.add(reqs)
        self.store.version(sha2, 'bar')
        self.store.removeOlder(50)
        with self.assertRaises(LookupError):
            self.store.version(sha3, 'baz')
        self.store.version(sha1, 'foo')
        self.store.version(sha2, 'bar')


class TestMemoryLocationCache(unittest.TestCase):

    def setUp(self):
        self.cache = model.MemoryLocationCache()

    def test_no_get(self):
        t = self.cache.get(('foo', '1'))
        self.assertEquals(t, {})

    def test_put_get(self):
        self.cache.save(('foo', '1'), '/foo.tttt')
        t = self.cache.get(('foo', '1'))
        self.assertEquals(t, dict(value='/foo.tttt'))
