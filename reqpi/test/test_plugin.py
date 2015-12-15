import unittest

from twisted.python import usage
from twisted.internet import task
from twisted.web import server, client
from twisted.web.test import requesthelper

from reqpi import plugin
from reqpi.robot import hash as rrhash


class TestOptions(unittest.TestCase):

    def test_success(self):
        options = plugin.Options()
        options.parseOptions(['--url', 'http://whatever:999',
                              '--http', '1234',
                              '--frequency', '5',
                              '--max-age', '10'])
        self.assertEquals(options['url'], 'http://whatever:999')
        self.assertEquals(options['http'], '1234')
        self.assertEquals(options['frequency'], 5)
        self.assertEquals(options['max-age'], 10)

    def test_defaults(self):
        options = plugin.Options()
        options.parseOptions(['--http', '1234'])
        self.assertEquals(options['http'], '1234')
        self.assertEquals(options['frequency'], 60*60)
        self.assertEquals(options['max-age'], 24*60*60)

    def test_failure(self):
        options = plugin.Options()
        with self.assertRaises(usage.UsageError):
            options.parseOptions([])


class DummyReactor(object):

    def __init__(self):
        self.tcp = {}
        self.clock = task.Clock()
        self.callLater = self.clock.callLater
        self.seconds = self.clock.seconds

    def listenTCP(self, port, factory, backlog=0, interface=''):
        self.tcp[port] = factory


class TestMakeService(unittest.TestCase):

    def test_simple(self):
        myDummyReactor = DummyReactor()
        myDummyRequest = requesthelper.DummyRequest(['robot', 'hash'])
        cfg = dict(http='999', url='http://somewhere.com:1234', frequency=1)
        cfg['max-age'] = 10
        s = plugin.makeService(cfg, myDummyReactor)
        s.startService()
        web = myDummyReactor.tcp.pop(999)
        self.assertEquals(myDummyReactor.tcp, {})
        self.assertIsInstance(web, server.Site)
        resource = web.getResourceFor(myDummyRequest)
        self.assertIsInstance(resource, rrhash.Hash)
        locate = resource.locate
        store = resource.store
        args = locate.args
        loc, agent = args
        self.assertIsInstance(agent, client.RedirectAgent)
        call, = myDummyReactor.clock.getDelayedCalls()
        loop = call.func
        removeOlder = call.func.f
        self.assertEquals(removeOlder.im_func, store.removeOlder.im_func)
        self.assertEquals(removeOlder.im_self, store.removeOlder.im_self)
        self.assertEquals(loop.a, (10,))
        self.assertEquals(call.getTime(), myDummyReactor.clock.seconds() + 1)
