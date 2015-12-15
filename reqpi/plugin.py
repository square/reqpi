import functools

from reqpi.robot import hash as rrhash
from reqpi.robot import locator
from reqpi.db import model

from twisted.internet import reactor
from twisted.python import usage
from twisted.web import resource, server, client
from twisted.application import strports, service, internet

NOT_THERE = object()


class Options(usage.Options):

    """Options for ncolony service"""

    optParameters = [
        ["http", None, NOT_THERE, "Port for HTTP"],
        ["frequency", None, 60*60,
         "Frequency of garbage collection", int],
        ["max-age", None, 24*60*60,
         "How old a hash should be to be considered garbage",
         int],
        ["url", "u", None, "Canonical base URL"],
    ]

    def postOptions(self):
        if self['http'] is NOT_THERE:
            raise usage.UsageError("http port required")


def makeService(config, reactor=reactor):
    baseurl = config['url']
    root = resource.Resource()
    root.putChild('robot', resource.Resource())
    agent = client.RedirectAgent(client.Agent(reactor))
    cache = model.MemoryLocationCache()
    store = model.MemoryStore(reactor)
    locate = functools.partial(locator.locate, cache, agent)
    child = rrhash.Hash(store, locate, baseurl)
    root.children['robot'].putChild('hash', child)
    site = server.Site(root)
    retService = service.MultiService()
    webService = strports.service(config['http'], site, reactor=reactor)
    webService.setServiceParent(retService)
    timeService = internet.TimerService(config['frequency'],
                                        store.removeOlder,
                                        config['max-age'])
    timeService.clock = reactor
    timeService.setServiceParent(retService)
    return retService
