import operator
from xml.etree import ElementTree as ET
import cStringIO as StringIO
import json

from twisted.trial import unittest
from twisted.internet import defer, tcp

from twisted.web import resource, server
from twisted.web.test import requesthelper

from reqpi.robot import hash as rrhash

from zope.interface import verify


def _render(resource, request):
    result = resource.render(request)
    if isinstance(result, str):
        request.write(result)
        request.finish()
        return defer.succeed(None)
    elif result is server.NOT_DONE_YET:
        if request.finished:
            return defer.succeed(None)
        else:
            return request.notifyFinish()
    else:
        raise ValueError("Unexpected return value: %r" % (result,))


class DummyStore(object):

    def __init__(self):
        self.stuffs = []
        self.versions = {}

    def add(self, stuff):
        self.stuffs.append(stuff)
        return 'hello'

    def version(self, sha, name):
        return self.versions[sha, name]


class HashTest(unittest.TestCase):

    def setUp(self):
        self.store = DummyStore()
        self.locations = {}

        def locate(*args):
            return defer.maybeDeferred(operator.getitem, self.locations, args)
        self.resource = rrhash.Hash(self.store, locate,
                                    'http://testing.org:123')

    def test_iface(self):
        verify.verifyObject(resource.IResource, self.resource)

    def test_leafiness(self):
        self.assertTrue(self.resource.isLeaf)
        with self.assertRaises(Exception):
            self.resource.putChild('lala', None)
        with self.assertRaises(Exception):
            self.resource.getChildWithDefault(None, None)

    def test_POST(self):
        request = requesthelper.DummyRequest([''])
        request.method = 'POST'
        request.uri = '/robot/hash'
        request.content = StringIO.StringIO(json.dumps(dict(requirements='')))
        request.getHost = lambda: tcp.Port(1555, None)
        d = _render(self.resource, request)

        @d.addCallback
        def handle(res):
            self.assertEquals(res, None)
            resp = json.loads(''.join(request.written))
            url = resp.pop('url')
            url, slug = url.rsplit('/', 1)
            self.assertEquals(resp, {})
            self.assertEquals(url, 'http://testing.org:123/robot/hash')
            self.assertNotEquals(slug, '')
        return d

    def test_POST_without_baseurl(self):
        def locate(*args):
            return defer.maybeDeferred(operator.getitem, self.locations, args)
        self.resource = rrhash.Hash(self.store, locate, baseurl=None)
        request = requesthelper.DummyRequest([''])
        request.method = 'POST'
        request.uri = '/robot/hash'
        request.content = StringIO.StringIO(json.dumps(dict(requirements='')))
        request.getHost = lambda: tcp.Port(1555, None)
        d = _render(self.resource, request)

        @d.addCallback
        def handle(res):
            self.assertEquals(res, None)
            resp = json.loads(''.join(request.written))
            url = resp.pop('url')
            url, slug = url.rsplit('/', 1)
            self.assertEquals(resp, {})
            self.assertEquals(url, 'http://dummy:1555/robot/hash')
            self.assertNotEquals(slug, '')
        return d

    def test_no_OPTIONS(self):
        request = requesthelper.DummyRequest([''])
        request.method = 'OPTIONS'
        with self.assertRaises(server.UnsupportedMethod):
            _render(self.resource, request)

    def test_GET_package(self):
        self.store.versions['111', 'twisted'] = 'Twisted', '15.5'
        self.locations['Twisted', '15.5'] = 'lalal/Twisted-15.5.tar.gz'
        request = requesthelper.DummyRequest(['111', 'twisted', ''])
        request.method = 'GET'
        d = _render(self.resource, request)

        @d.addCallback
        def handle(res):
            self.assertEquals(res, None)
            html = ''.join(request.written)
            parsed = ET.fromstring(html)
            link, = parsed.iter('a')
            href = link.attrib['href']
            head, tail = href.rsplit('/', 1)
            self.assertEquals(tail, 'Twisted-15.5.tar.gz')
        return d

    def test_bad_GET(self):
        request = requesthelper.DummyRequest(['111', 'twisted'])
        request.method = 'GET'
        with self.assertRaises(NotImplementedError):
            _render(self.resource, request)

    def test_failed_GET_package(self):
        self.store.versions['111', 'twisted'] = 'Twisted', '15.5'
        request = requesthelper.DummyRequest(['111', 'twisted', ''])
        request.method = 'GET'
        d = _render(self.resource, request)

        @d.addCallback
        def handle(res):
            self.assertEquals(res, None)
            html = ''.join(request.written)
            parsed = ET.fromstring(html)
            self.assertEquals(list(parsed.iter('a')), [])
            res = self.flushLoggedErrors()
            self.assertEquals(len(res), 1)

        return d
