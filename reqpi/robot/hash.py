from __future__ import print_function

import json
from urlparse import urljoin

from twisted.python import log
from twisted.web import resource, server

from zope import interface


@interface.implementer(resource.IResource)
class Hash(object):

    isLeaf = True

    def __init__(self, store, locate, baseurl=None):
        self.store = store
        self.locate = locate
        self.baseurl = baseurl

    def render(self, request):
        m = getattr(self, 'render_' + request.method, None)
        if not m:
            raise server.UnsupportedMethod(getattr(self, 'allowedMethods', ()))
        return m(request)

    def render_GET(self, request):
        if request.postpath[-1] != '':
            raise NotImplementedError("womp womp")
        hash, package = request.postpath[-3:-1]
        package, version = self.store.version(hash, package)
        d = self.locate(package, version)

        @d.addCallback
        def handle(location):
            dummy, name = location.rsplit('/', 1)
            request.write('<a href="{}">{}</a>'.format(location, name))
            request.finish()

        @d.addErrback
        def recover(err):
            log.err(err)
            request.write('<html>Something went wrong -- see logs</html>')
            request.finish()
        return server.NOT_DONE_YET

    def render_POST(self, request):
        req = json.loads(request.content.read())
        requirements = req['requirements']
        sha = self.store.add(requirements)
        url = self.baseurl
        if url is None:
            host = (request.getRequestHostname() + ':' +
                    str(request.getHost().port))
            url = 'http://' + host

        url = urljoin(url, '/robot/hash/' + sha)
        return json.dumps(dict(url=url))

    def putChild(self, name, request):
        raise ValueError("I'm a leaf on the wind, watch how I soar")

    def getChildWithDefault(self, request, default):
        raise ValueError("I'm a leaf on the wind, watch how I soar")
