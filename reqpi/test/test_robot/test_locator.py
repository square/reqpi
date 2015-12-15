from twisted.python import failure
from twisted.internet import defer
from twisted.trial import unittest
from twisted.web import iweb, client

from reqpi.robot import locator

from zope import interface


@interface.implementer(iweb.IAgent)
class DummyAgent(object):

    def __init__(self):
        self.uris = {}

    def request(self, method, uri, headers=None, bodyProducer=None):
        if isinstance(uri, unicode):
            raise TypeError("uri must be bytes, got", uri)
        if method != 'GET':
            raise ValueError('bad method', method)
        if uri not in self.uris:
            raise ValueError('bad uri', uri)
        data = self.uris[uri]
        response = client.Response(('HTTP', 1, 1), 200, 'OK', {}, None)

        def deliverBody(protocol):
            protocol.makeConnection(None)
            protocol.dataReceived(data)
            fail = failure.Failure(client.ResponseDone('byebye'))
            protocol.connectionLost(fail)
        response.deliverBody = deliverBody
        return defer.succeed(response)


class DummyCache(object):

    def __init__(self):
        self.saved = []
        self.locations = {}

    def save(self, details, location):
        self.saved.append((details, location))

    def get(self, details):
        if details in self.locations:
            return dict(value=self.locations[details])
        return {}


class TestLocator(unittest.TestCase):

    def setUp(self):
        self.agent = DummyAgent()
        self.cache = DummyCache()

    def test_locate_one_option(self):
        html = ('<foo><a href="../../packages/source/n/nahman/'
                'nahman-0.3.0.tar.gz#haha">lala</a></foo>')
        self.agent.uris['https://pypi.python.org/simple/nahman/'] = html
        d = locator.locate(self.cache, self.agent, 'nahman', '0.3.0')

        @d.addCallback
        def handle(res):
            self.assertEquals(res, "https://pypi.python.org/packages/source/n/"
                                   "nahman/nahman-0.3.0.tar.gz")
            self.assertEquals(self.cache.saved, [(('nahman', '0.3.0'), res)])
        return d

    test_locate_one_option.timeout = 5

    def test_locate_unicode_option(self):
        html = ('<foo><a href="../../packages/source/n/nahman/'
                'nahman-0.3.0.tar.gz#haha">lala</a></foo>')
        self.agent.uris['https://pypi.python.org/simple/nahman/'] = html
        d = locator.locate(self.cache, self.agent, u'nahman', u'0.3.0')

        @d.addCallback
        def handle(res):
            self.assertEquals(res, "https://pypi.python.org/packages/source/n/"
                                   "nahman/nahman-0.3.0.tar.gz")
            self.assertEquals(self.cache.saved, [(('nahman', '0.3.0'), res)])
        return d

    test_locate_unicode_option.timeout = 5

    def test_locate_no_option(self):
        html = '<foo></foo>'
        self.agent.uris['https://pypi.python.org/simple/nahman/'] = html
        d = locator.locate(self.cache, self.agent, 'nahman', '0.3.0')

        @d.addCallback
        def handle(res):
            self.assertFalse("Should not succeed: %r", res)

        @d.addErrback
        def recover(res):
            self.assert_(res.check(ValueError), "Wrong error: %r" % res)

        return d

    test_locate_no_option.timeout = 5

    def test_locate_cached(self):
        details = 'nahman', '0.3.0'
        self.cache.locations[details] = "https://lala/nahman-0.3.0.tar.gz"
        d = locator.locate(self.cache, self.agent, 'nahman', '0.3.0')

        @d.addCallback
        def handle(res):
            self.assertEquals(res, "https://lala/nahman-0.3.0.tar.gz")

    test_locate_cached.timeout = 5

    def test_collector(self):
        d = defer.Deferred()
        a = locator.Collector(d)
        a.connectionLost(failure.Failure(ValueError("buh bye")))

        @d.addCallback
        def handle(res):
            self.assertFalse("Should not succeed: %r", res)

        @d.addErrback
        def recover(res):
            self.assert_(res.check(ValueError), "Wrong error: %r" % res)

        return d

    test_collector.timeout = 5
