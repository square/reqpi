from __future__ import print_function

import urlparse
from xml.etree import ElementTree as ET

from twisted.internet import defer
from twisted.web import client

UPSTREAM = 'https://pypi.python.org/simple/'

EXTENSIONS = ['tar.gz', 'tar.bz2', '.zip']


class Collector(object):

    def __init__(self, d):
        self.d = d
        self.bits = []

    def makeConnection(self, transport):
        pass

    def dataReceived(self, data):
        self.bits.append(data)

    def connectionLost(self, reason):
        if reason.check(client.ResponseDone):
            self.d.callback(''.join(self.bits))
        else:
            self.d.errback(reason)


def futf8(s):
    if isinstance(s, unicode):
        return s.encode('utf8')
    return s


def locate(cache, agent, name, version):
    cached = cache.get((name, version))
    if cached:
        return defer.succeed(cached['value'])
    name, version = map(futf8, (name, version))
    url = urlparse.urljoin(UPSTREAM, name) + '/'
    resp = agent.request('GET', url)

    @resp.addCallback
    def handle(deliverer):
        d = defer.Deferred()
        deliverer.deliverBody(Collector(d))
        return d

    @resp.addCallback
    def parse(content):
        root = ET.fromstring(content)
        candidates = {}
        for el in root.iter('a'):
            href = el.attrib['href']
            href = href.split('#')[0]
            href = urlparse.urljoin(url, href)
            lower = href.lower()
            for extension in EXTENSIONS:
                lname = name.lower()
                expected = '{}-{}.{}'.format(lname, version, extension)
                if lower.endswith(expected):
                    candidates[extension] = href
        if not candidates:
            raise ValueError("no such version", name, version)
        for extension in EXTENSIONS:
            if extension in candidates:
                cache.save((name, version), candidates[extension])
                return candidates[extension]
        raise RuntimeError("This should never happen")  # pragma: no cover

    return resp
